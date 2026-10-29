package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
	"testing"

	"github.com/open-cluster/oc-control-plane/internal/integrations"
	"github.com/open-cluster/oc-control-plane/internal/investigation/agent"
	"github.com/open-cluster/oc-control-plane/internal/investigation/agent/openrouter"
	"go.opentelemetry.io/otel/trace"
)

func TestRecorderUsesRealSDKAndRetainsOnlyScopedToolEvidence(t *testing.T) {
	const observation = "[run 1] prometheus_query {}\nCONTENT: {\"series\":[{\"value\":\"0.02\"}]}"
	var providerToolMessages int
	source := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if r.URL.Path == "/api/v1/query" {
			body, _ := io.ReadAll(r.Body)
			if r.Method != http.MethodPost || string(body) != "query=test%5B60m%5D" {
				t.Errorf("request changed: %s %s", r.Method, body)
			}
			_, _ = io.WriteString(w, `{"status":"success","data":{"value":"0.02"}}`)
			return
		}
		var request struct {
			Messages []struct{ Role, Content string }
		}
		if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
			t.Error(err)
		}
		hasResult := false
		for _, message := range request.Messages {
			if message.Role == "tool" {
				hasResult = true
				providerToolMessages++
				if message.Content != observation {
					t.Error("Tool observation changed before SDK forwarding")
				}
			}
		}
		name, id, arguments := "prometheus_query", "read-1", `{"input":{"query":"test[60m]","mode":"instant"}}`
		if hasResult {
			name, id, arguments = "conclude", "done", `{}`
		}
		_ = json.NewEncoder(w).Encode(map[string]any{
			"id": "generation-1", "object": "chat.completion", "created": 1, "model": "z-ai/glm-5.1",
			"choices": []any{map[string]any{"index": 0, "finish_reason": "tool_calls", "message": map[string]any{
				"role": "assistant", "tool_calls": []any{map[string]any{"id": id, "type": "function", "function": map[string]any{"name": name, "arguments": arguments}}},
			}}},
		})
	}))
	defer source.Close()
	var exported bytes.Buffer
	recorder := newRecorder(&exported, []string{source.URL})
	provider, err := openrouter.New(agent.ModelConfig{Provider: "openrouter", Model: "z-ai/glm-5.1", Credential: agent.Secret("model-secret"), BaseURL: source.URL}, openrouter.Options{HTTPClient: &http.Client{Transport: recorder}})
	if err != nil {
		t.Fatal(err)
	}
	recorder.next = provider
	for _, id := range []string{"11111111111111111111111111111111", "22222222222222222222222222222222"} {
		traceID, _ := trace.TraceIDFromHex(id)
		spanID, _ := trace.SpanIDFromHex("1111111111111111")
		ctx := trace.ContextWithSpanContext(context.Background(), trace.NewSpanContext(trace.SpanContextConfig{TraceID: traceID, SpanID: spanID}))
		prompt := agent.Prompt{Model: "z-ai/glm-5.1", Content: []agent.Block{{Text: "PRIVATE QUESTION"}}, MaxOutputTokens: 32000,
			Tools: []integrations.ToolDefinition{(integrations.Tool{Name: "prometheus_query"}).Definition(), agent.ConcludeDefinition()}}
		completion, err := recorder.Complete(ctx, prompt)
		if err != nil {
			t.Fatal(err)
		}
		values := url.Values{"query": {"test[60m]"}}
		request, _ := http.NewRequestWithContext(ctx, http.MethodPost, source.URL+"/api/v1/query", strings.NewReader(values.Encode()))
		request.Header.Set("Content-Type", "application/x-www-form-urlencoded")
		request.Header.Set("Authorization", "Bearer source-secret")
		response, err := recorder.RoundTrip(request)
		if err != nil {
			t.Fatal(err)
		}
		body, _ := io.ReadAll(response.Body)
		response.Body.Close()
		if !bytes.Contains(body, []byte("0.02")) {
			t.Fatal("source response changed")
		}
		prompt.Turns = []agent.Turn{{Assistant: agent.AssistantTurn{Text: "PRIVATE REASONING", Calls: completion.ToolCalls}, ToolResults: []agent.ToolResultTurn{{CallID: "read-1", Content: observation}}}}
		if _, err = recorder.Complete(ctx, prompt); err != nil {
			t.Fatal(err)
		}
		if _, err = recorder.Complete(ctx, prompt); err != nil {
			t.Fatal(err)
		}
	}
	if providerToolMessages != 4 {
		t.Fatalf("SDK Tool messages = %d", providerToolMessages)
	}
	data := exported.String()
	decoder := json.NewDecoder(&exported)
	counts := map[string]int{}
	for decoder.More() {
		var record map[string]any
		if err := decoder.Decode(&record); err != nil {
			t.Fatal(err)
		}
		counts[record["kind"].(string)]++
	}
	if counts["observation"] != 2 || counts["request"] != 2 {
		t.Fatalf("capture counts: %v", counts)
	}
	for _, secret := range []string{"model-secret", "source-secret", "PRIVATE QUESTION", "PRIVATE REASONING", "Authorization"} {
		if strings.Contains(data, secret) {
			t.Fatalf("export contains forbidden data %q", secret)
		}
	}
}

func TestCaptureLimitsDoNotChangeProviderInput(t *testing.T) {
	for _, example := range []struct {
		name        string
		count, size int
	}{
		{"record", 1, maxRecordBytes}, {"total", 90, 100 * 1024},
	} {
		t.Run(example.name, func(t *testing.T) {
			received := 0
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				var request struct {
					Messages []struct{ Role, Content string }
				}
				if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
					t.Error(err)
				}
				for _, message := range request.Messages {
					if message.Role == "tool" {
						received += len(message.Content)
					}
				}
				w.Header().Set("Content-Type", "application/json")
				_, _ = io.WriteString(w, `{"id":"g","object":"chat.completion","created":1,"model":"z-ai/glm-5.1","choices":[{"index":0,"finish_reason":"tool_calls","message":{"role":"assistant","tool_calls":[{"id":"done","type":"function","function":{"name":"conclude","arguments":"{}"}}]}}]}`)
			}))
			defer server.Close()
			var output bytes.Buffer
			capture := newRecorder(&output, nil)
			provider, err := openrouter.New(agent.ModelConfig{Provider: "openrouter", Model: "z-ai/glm-5.1", Credential: agent.Secret("key"), BaseURL: server.URL}, openrouter.Options{})
			if err != nil {
				t.Fatal(err)
			}
			capture.next = provider
			prompt := agent.Prompt{Model: "z-ai/glm-5.1", MaxOutputTokens: 32000, Tools: []integrations.ToolDefinition{agent.ConcludeDefinition()}}
			turn := agent.Turn{}
			expected := 0
			for i := 0; i < example.count; i++ {
				content := fmt.Sprintf("[run %d] prometheus_query {}\nCONTENT: ", i+1) + strings.Repeat("x", example.size)
				expected += len(content)
				turn.ToolResults = append(turn.ToolResults, agent.ToolResultTurn{CallID: fmt.Sprint(i), Content: content})
			}
			prompt.Turns = []agent.Turn{turn}
			if _, err = capture.Complete(context.Background(), prompt); err != nil {
				t.Fatal(err)
			}
			if received != expected {
				t.Fatalf("provider input changed: got %d bytes, want %d", received, expected)
			}
			if !strings.Contains(output.String(), `"kind":"capture_error"`) {
				t.Fatal("capture overflow was not explicit")
			}
			if output.Len() > maxCaptureBytes+maxRecordBytes {
				t.Fatal("capture exceeded its total bound")
			}
		})
	}
}
