// This benchmark entry point wraps existing application seams; it does not reason or run Tools.
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/open-cluster/oc-control-plane/internal/app"
	"github.com/open-cluster/oc-control-plane/internal/config"
	"github.com/open-cluster/oc-control-plane/internal/investigation/agent"
	"github.com/open-cluster/oc-control-plane/internal/investigation/agent/anthropic"
	"github.com/open-cluster/oc-control-plane/internal/investigation/agent/openrouter"
	"go.opentelemetry.io/otel/trace"
)

const maxRecordBytes = 128 * 1024
const maxCaptureBytes = 8 * 1024 * 1024

type recorder struct {
	next    agent.Completer
	base    http.RoundTripper
	out     io.Writer
	sources map[string]string
	seen    map[string]bool
	issued  map[string]string
	mu      sync.Mutex
	written int
	failed  bool
}

func newRecorder(out io.Writer, sources []string) *recorder {
	r := &recorder{out: out, base: http.DefaultTransport, sources: map[string]string{}, seen: map[string]bool{}, issued: map[string]string{}}
	for _, source := range sources {
		parsed, err := url.Parse(source)
		if err == nil && parsed.Host != "" && parsed.User == nil {
			r.sources[parsed.Scheme+"://"+parsed.Host] = strings.TrimRight(parsed.Path, "/")
		}
	}
	return r
}

func (r *recorder) record(value map[string]any) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.failed {
		return
	}
	encoded, err := json.Marshal(value)
	if err != nil || len(encoded) > maxRecordBytes || r.written+len(encoded)+1 > maxCaptureBytes {
		r.captureError()
		return
	}
	encoded = append(encoded, '\n')
	n, err := r.out.Write(encoded)
	r.written += n
	if err != nil || n != len(encoded) {
		r.captureError()
	}
}

// Called with mu held. Capture failure never changes the forwarded provider input.
func (r *recorder) captureError() {
	r.failed = true
	_, _ = io.WriteString(r.out, "{\"kind\":\"capture_error\",\"error\":\"capture limit or write failure; evidence is incomplete\"}\n")
	_, _ = fmt.Fprintln(os.Stderr, "benchmark capture incomplete")
}

func scope(ctx context.Context) string {
	return trace.SpanContextFromContext(ctx).TraceID().String()
}

func (r *recorder) Complete(ctx context.Context, prompt agent.Prompt) (agent.Completion, error) {
	for i, turn := range prompt.Turns {
		for j, result := range turn.ToolResults {
			if !strings.HasPrefix(result.Content, "[run ") {
				continue
			}
			key := fmt.Sprintf("%s/%d/%d/%s", scope(ctx), i, j, result.CallID)
			if r.seen[key] {
				continue
			}
			r.seen[key] = true
			record := map[string]any{"kind": "observation", "traceId": scope(ctx), "callId": result.CallID,
				"turn": i, "position": j, "content": result.Content, "isError": result.IsError,
				"issuedAt": r.issued[scope(ctx)+"/"+result.CallID], "observedAt": time.Now().UTC().Format(time.RFC3339Nano)}
			for _, call := range turn.Assistant.Calls {
				if call.ID == result.CallID {
					record["tool"] = call.Name
					record["arguments"] = string(call.Arguments)
					break
				}
			}
			r.record(record)
		}
	}
	completion, err := r.next.Complete(ctx, prompt)
	issued := time.Now().UTC().Format(time.RFC3339Nano)
	for _, call := range completion.ToolCalls {
		r.issued[scope(ctx)+"/"+call.ID] = issued
	}
	return completion, err
}

func (r *recorder) RoundTrip(request *http.Request) (*http.Response, error) {
	origin := request.URL.Scheme + "://" + request.URL.Host
	prefix, known := r.sources[origin]
	path := strings.TrimPrefix(request.URL.Path, prefix)
	allowed := path == "/api/v1/query" || path == "/api/v1/query_range" || path == "/api/v1/label/__name__/values" ||
		path == "/loki/api/v1/query_range" || path == "/api/search" || strings.HasPrefix(path, "/api/v2/traces/")
	if !known || !allowed || (request.Method != http.MethodGet && request.Method != http.MethodPost) {
		return r.base.RoundTrip(request)
	}
	parameters := request.URL.Query()
	parameterError := ""
	if request.Method == http.MethodPost {
		if request.GetBody == nil {
			parameterError = "request body copy unavailable"
		} else {
			body, err := request.GetBody()
			if err != nil {
				parameterError = "request body copy unavailable"
			} else {
				data, readErr := io.ReadAll(io.LimitReader(body, 16385))
				_ = body.Close()
				if readErr != nil || len(data) > 16384 {
					parameterError = "request parameters exceed capture bound"
				} else {
					form, parseErr := url.ParseQuery(string(data))
					if parseErr != nil {
						parameterError = "request parameters could not be parsed"
					} else {
						for key, values := range form {
							parameters[key] = append(parameters[key], values...)
						}
					}
				}
			}
		}
	}
	started := time.Now().UTC()
	response, err := r.base.RoundTrip(request)
	record := map[string]any{"kind": "request", "traceId": scope(request.Context()), "method": request.Method,
		"origin": origin, "path": request.URL.Path, "parameters": parameters,
		"startedAt": started.Format(time.RFC3339Nano), "headersAt": time.Now().UTC().Format(time.RFC3339Nano)}
	if response != nil {
		record["status"] = response.StatusCode
	}
	if err != nil {
		record["error"] = "source request failed"
	}
	if parameterError != "" {
		record["parameterError"] = parameterError
	}
	r.record(record)
	return response, err
}

func main() {
	if err := start(); err != nil {
		_, _ = fmt.Fprintln(os.Stderr, "benchmark application failed:", err)
		os.Exit(1)
	}
}

func start() error {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	cfg, err := config.Load(os.LookupEnv)
	if err != nil {
		return err
	}
	file, err := os.OpenFile(os.Getenv("OC_BENCH_CAPTURE_FILE"), os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		return fmt.Errorf("cannot open private benchmark capture")
	}
	defer file.Close()
	capture := newRecorder(file, []string{os.Getenv("PROMETHEUS_URL"), os.Getenv("LOKI_URL"), os.Getenv("TEMPO_URL")})
	http.DefaultTransport = capture
	model := agent.ModelConfig{Provider: cfg.ModelProvider, Model: cfg.ModelName, Credential: agent.Secret(cfg.ModelAPIKey), MaxOutputTokens: cfg.ModelMaxOutputTokens}.WithDefaults()
	switch model.Provider {
	case openrouter.Name:
		capture.next, err = openrouter.New(model, openrouter.Options{})
	case anthropic.Name:
		capture.next, err = anthropic.New(model, anthropic.Options{})
	default:
		return fmt.Errorf("unsupported benchmark provider")
	}
	if err != nil {
		return err
	}
	return app.Run(ctx, cfg, os.Stderr, app.Options{Version: os.Getenv("OC_BENCH_COMMIT") + "+benchmark-recorder", Completer: capture})
}
