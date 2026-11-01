# OpenCluster benchmark assessment

Model: openrouter/z-ai/glm-5.1

Local rubric verdict: **passed**; weighted score: 1.0. Judge: anthropic/claude-haiku-5.5@high. [Criterion verdicts](local-grading/grading_details.json), [canonical truth](local-grading/truth.json), [grading route and scope](grading-context.json). Saved-answer grading does not constitute an official leaderboard submission.
Harbor process exit code: 0
Harbor trial errors: 0
Execution completion, answer correctness and benchmark grading are separate outcomes.

## Rubric verdicts

**The final response states 5xx share accurately.: pass**

    The truth is 0.033898 (3.39%), and the response's 3.4% (2.01 / 59.27) is within 1% of that, over the full 60-minute window.

**The response expresses the result as a percentage, ratio, or share: pass**

    The response expresses the result as a percentage and explicitly labels it as the "5xx share".


## Answer

> Over the 60-minute window ending at 10:54:29 UTC on 2026-10-29, approximately **3.4%** of HTTP requests across user-service, order-service, and payment-service returned 5xx status codes.
> 
> This is based on `sum(increase(http_requests_total{...}))` evaluated over the full [60m] window:
> - **5xx requests:** ~2.01 (status=~"5..")
> - **Total requests:** ~59.27
> - **5xx share:** 2.01 / 59.27 ≈ **3.4%**
> 
> Per-service breakdown:
> - **order-service:** ~2.6% 5xx (1.00 / 39.18)
> - **payment-service:** ~9.1% 5xx (1.00 / 11.05) — highest error rate
> - **user-service:** 0% 5xx (0 / 9.04) — no 5xx errors in this window
> 
> Note: The metric uses a `status` label (not `code`) for HTTP status classification. The `increase()` function produces fractional estimates from counter extrapolation, so the share is approximate.

### Question

    Over the last hour, what overall share of HTTP requests returned 5xx across user-service,
    order-service, and payment-service? In Prometheus those names are the `job` label values on
    `http_requests_total` for API traffic here - ignore webapp and api-gateway. Report the share for the
    full 60-minute window aggregated together, not a conclusion from a single short slice of the timeline.

Investigation: **concluded**; Agent-claimed assessment: **answer_only**.
Tool attempts: **8**, including **1 failed/blocked** and **0 limited**.
Read budget: **30** (unchanged); stopped by: **Agent conclusion**.
Tokens: 31390 input / 2893 output.
Agent elapsed: 42.3 seconds.
Exact repeated requests: none.
Model-observation clipping: none detected.

### Trace examples in the answer

No trace example was stated or requested.

## Independent checks

Canonical facts were read from the original benchmark stack at this run's scenario clock. They are independent evidence, not a judge verdict.
- **Engineering review (not an upstream judge verdict)**: Runs 2/6 give estimated increases of 59.2667 total and 2.00904 5xx, approximately 3.39%. Runs 7/8 support order-service 2.56%, payment-service 9.09% and user-service 0%; the user-service zero is explicitly returned, not inferred from an absent series.
- **Engineering review (not an upstream judge verdict)**: The answer correctly qualifies fractional increase estimates and uses the 60m lookback with equal instant evaluation bounds. Run 4 corrects the initial empty code label to status. All eight observations match; one malformed discovery selector failed.

**The final response states 5xx share accurately.**

    Matching metrics exist in the snapshot window: Query returned 1 result: 0.033898
Fact displays are excerpts. [Full canonical queries and returned data](fact-audit.json)

### Findings and uncertainty

- **observation**: Over the 60-minute window (09:54–10:54 UTC on 2026-10-29), the overall share of HTTP requests returning 5xx across user-service, order-service, and payment-service was approximately 3.4% (≈2.01 5xx out of ≈59.27 total requests). ([#6](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-6), [#2](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-2))
- **observation**: Per-service 5xx shares: order-service ~2.6% (≈1.00 / ≈39.18), payment-service ~9.1% (≈1.00 / ≈11.05), user-service 0% (0 / ≈9.04). ([#7](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-7), [#8](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-8))
- **observation**: The http_requests_total metric uses a 'status' label (not 'code') for HTTP status codes, with observed values '200' and '500'. ([#4](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-4))
- **Limitation**: increase() over 60m produces fractional estimates from counter extrapolation, not exact integer counts; the ~3.4% share is an approximation.

### Tool attempts

| Run | Tool | Outcome | Purpose |
| --- | --- | --- | --- |
| [#1](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-1) | prometheus_query | succeeded, empty | Get total 5xx HTTP requests across user-service, order-service, and payment-service over the 60-minute window |
| [#2](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-2) | prometheus_query | succeeded | Get total HTTP requests across user-service, order-service, and payment-service over the 60-minute window |
| [#3](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-3) | prometheus_discover_metrics | failed | Confirm the metric name and labels exist for the three target services |
| [#4](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-4) | prometheus_query | succeeded | See raw series labels to identify the status code label name |
| [#5](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-5) | prometheus_discover_metrics | succeeded | Discover metric names containing http_requests to confirm exact metric name |
| [#6](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-6) | prometheus_query | succeeded | Get total 5xx HTTP requests across the three services with correct 'status' label |
| [#7](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-7) | prometheus_query | succeeded | Get per-service 5xx request counts over the 60-minute window |
| [#8](#run-2a60a37d-777a-4d73-91fb-e92f47fead2b-8) | prometheus_query | succeeded | Get per-service total request counts over the 60-minute window |

### Where these files came from

Control-plane endpoint: `GET /api/v1/investigations/2a60a37d-777a-4d73-91fb-e92f47fead2b` supplies the public Conclusion and Tool Run records.
`adapterElapsedSeconds` is added by this benchmark adapter. It is not backend telemetry.
Integration configuration comes from `POST /api/v1/integrations/{id}/verify`.
`backend.log` is the OpenCluster process log, not queried Loki log data.
`trajectory.json` is reconstructed ATIF; it contains the Agent's recorded answer and observations, not private reasoning.
[Public result](promql-error-rate__hegMwNj/agent/artifacts/investigation.json) · [Actual Tool observations and HTTP metadata](promql-error-rate__hegMwNj/agent/artifacts/tool-results.json) · [Application log](promql-error-rate__hegMwNj/agent/artifacts/backend.log)

An instant Prometheus read has one evaluation timestamp. A selector such as `[60m]` reads the preceding hour; equal evaluation bounds do not mean an empty lookback.
Execution timestamps preserve stored subsecond precision; durationMs is derived from the execution interval. HTTP timing measures time to response headers.

<a id="run-2a60a37d-777a-4d73-91fb-e92f47fead2b-1"></a>
### Tool Run 1

**prometheus_query** — Get total 5xx HTTP requests across user-service, order-service, and payment-service over the 60-minute window
Execution: 2026-11-01T20:09:37.37214Z to 2026-11-01T20:09:37.376473Z; durationMs: 4.333.
Evaluation at: 2026-10-29T10:54:29Z

Arguments:

    {
      "end": "2026-10-29T10:54:29Z",
      "mode": "instant",
      "query": "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m]))"
    }

Prometheus instant "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m]))": 0 series, 0 samples; 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z; incomplete=false
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__hegmwnj__env:9090`.
HTTP timing: 2026-11-01T20:09:37.372266402Z to 2026-11-01T20:09:37.376092756Z; 3.826 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m]))"
      ],
      "time": [
        "1793271269"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 1] prometheus_query {"end":"2026-10-29T10:54:29Z","mode":"instant","query":"sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m]))"}
    WINDOW: effective bounds 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z
    SUMMARY: Prometheus instant "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m]))": 0 series, 0 samples; 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z; incomplete=false
    CONTENT: {"query":"sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T10:54:29Z","until":"2026-10-29T10:54:29Z","series":[],"incomplete":false}

<a id="run-2a60a37d-777a-4d73-91fb-e92f47fead2b-2"></a>
### Tool Run 2

**prometheus_query** — Get total HTTP requests across user-service, order-service, and payment-service over the 60-minute window
Execution: 2026-11-01T20:09:37.386014Z to 2026-11-01T20:09:37.387933Z; durationMs: 1.919.
Evaluation at: 2026-10-29T10:54:29Z

Arguments:

    {
      "end": "2026-10-29T10:54:29Z",
      "mode": "instant",
      "query": "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
    }

Prometheus instant "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))": 1 series, 1 samples; 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z; incomplete=false; retained {}=59.266666666666666 at 2026-10-29T10:54:29Z
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__hegmwnj__env:9090`.
HTTP timing: 2026-11-01T20:09:37.386172444Z to 2026-11-01T20:09:37.387675459Z; 1.503 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
      ],
      "time": [
        "1793271269"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 2] prometheus_query {"end":"2026-10-29T10:54:29Z","mode":"instant","query":"sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"}
    WINDOW: effective bounds 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z
    SUMMARY: Prometheus instant "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))": 1 series, 1 samples; 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z; incomplete=false; retained {}=59.266666666666666 at 2026-10-29T10:54:29Z
    CONTENT: {"query":"sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T10:54:29Z","until":"2026-10-29T10:54:29Z","series":[{"labels":{},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"59.266666666666666"}]}],"incomplete":false}

<a id="run-2a60a37d-777a-4d73-91fb-e92f47fead2b-3"></a>
### Tool Run 3

**prometheus_discover_metrics** — Confirm the metric name and labels exist for the three target services
Execution: 2026-11-01T20:09:37.396318Z to 2026-11-01T20:09:37.396338Z; durationMs: 0.02.
Read window: 2026-10-29T09:54:29.760429Z to 2026-10-29T10:54:29.760429Z

Arguments:

    {
      "hint": "http_requests_total",
      "selector": "job=~\"user-service|order-service|payment-service\""
    }

selector must be label matchers enclosed in braces, at most 2048 bytes
Endpoint association: No source request recorded (rejected or not executed before HTTP).

Actual observation submitted to the provider adapter:

    [run 3] prometheus_discover_metrics {"hint":"http_requests_total","selector":"job=~\"user-service|order-service|payment-service\""}
    FAILED: selector must be label matchers enclosed in braces, at most 2048 bytes

<a id="run-2a60a37d-777a-4d73-91fb-e92f47fead2b-4"></a>
### Tool Run 4

**prometheus_query** — See raw series labels to identify the status code label name
Execution: 2026-11-01T20:09:40.510563Z to 2026-11-01T20:09:40.51253Z; durationMs: 1.967.
Evaluation at: 2026-10-29T10:54:29Z

Arguments:

    {
      "end": "2026-10-29T10:54:29Z",
      "mode": "instant",
      "query": "http_requests_total{job=~\"user-service|order-service|payment-service\"}"
    }

Prometheus instant "http_requests_total{job=~\"user-service|order-service|payment-service\"}": 6 series, 6 samples; 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z; incomplete=false; retained http_requests_total{instance="order-service:8083", job="order-service", status="…=2863 at 2026-10-29T10:54:29Z
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__hegmwnj__env:9090`.
HTTP timing: 2026-11-01T20:09:40.510693496Z to 2026-11-01T20:09:40.512105439Z; 1.412 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "http_requests_total{job=~\"user-service|order-service|payment-service\"}"
      ],
      "time": [
        "1793271269"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 4] prometheus_query {"end":"2026-10-29T10:54:29Z","mode":"instant","query":"http_requests_total{job=~\"user-service|order-service|payment-service\"}"}
    WINDOW: effective bounds 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z
    SUMMARY: Prometheus instant "http_requests_total{job=~\"user-service|order-service|payment-service\"}": 6 series, 6 samples; 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z; incomplete=false; retained http_requests_total{instance="order-service:8083", job="order-service", status="…=2863 at 2026-10-29T10:54:29Z
    CONTENT: {"query":"http_requests_total{job=~\"user-service|order-service|payment-service\"}","mode":"instant","resultType":"vector","from":"2026-10-29T10:54:29Z","until":"2026-10-29T10:54:29Z","series":[{"labels":{"__name__":"http_requests_total","instance":"order-service:8083","job":"order-service","status":"200"},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"2863"}]},{"labels":{"__name__":"http_requests_total","instance":"order-service:8083","job":"order-service","status":"500"},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"72"}]},{"labels":{"__name__":"http_requests_total","instance":"payment-service:8084","job":"payment-service","status":"200"},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"983"}]},{"labels":{"__name__":"http_requests_total","instance":"payment-service:8084","job":"payment-service","status":"500"},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"38"}]},{"labels":{"__name__":"http_requests_total","instance":"user-service:8082","job":"user-service","status":"200"},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"891"}]},{"labels":{"__name__":"http_requests_total","instance":"user-service:8082","job":"user-service","status":"500"},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":
Display excerpt only; the complete bounded observation is retained in tool-results.json.

<a id="run-2a60a37d-777a-4d73-91fb-e92f47fead2b-5"></a>
### Tool Run 5

**prometheus_discover_metrics** — Discover metric names containing http_requests to confirm exact metric name
Execution: 2026-11-01T20:09:40.521296Z to 2026-11-01T20:09:40.522945Z; durationMs: 1.649.
Read window: 2026-10-29T09:54:29.760429Z to 2026-10-29T10:54:29.760429Z

Arguments:

    {
      "hint": "http_requests"
    }

Prometheus metric discovery "http_requests": 1 names, 2026-10-29T09:54:29Z to 2026-10-29T10:54:29Z; incomplete=false
Sources: Prometheus metric-names.

Endpoint: **GET /api/v1/label/__name__/values** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__hegmwnj__env:9090`.
HTTP timing: 2026-11-01T20:09:40.521421276Z to 2026-11-01T20:09:40.522620794Z; 1.199 ms to response headers.

Actual request parameters:

    {
      "end": [
        "1793271269.760429"
      ],
      "limit": [
        "51"
      ],
      "match[]": [
        "{__name__=~\".*http_requests.*\"}"
      ],
      "start": [
        "1793267669.760429"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 5] prometheus_discover_metrics {"hint":"http_requests"}
    WINDOW: effective bounds 2026-10-29T09:54:29Z to 2026-10-29T10:54:29Z
    SUMMARY: Prometheus metric discovery "http_requests": 1 names, 2026-10-29T09:54:29Z to 2026-10-29T10:54:29Z; incomplete=false
    CONTENT: {"selector":"{__name__=~\".*http_requests.*\"}","names":["http_requests_total"],"from":"2026-10-29T09:54:29.760429Z","until":"2026-10-29T10:54:29.760429Z","incomplete":false}

<a id="run-2a60a37d-777a-4d73-91fb-e92f47fead2b-6"></a>
### Tool Run 6

**prometheus_query** — Get total 5xx HTTP requests across the three services with correct 'status' label
Execution: 2026-11-01T20:09:44.206251Z to 2026-11-01T20:09:44.208413Z; durationMs: 2.162.
Evaluation at: 2026-10-29T10:54:29Z

Arguments:

    {
      "end": "2026-10-29T10:54:29Z",
      "mode": "instant",
      "query": "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m]))"
    }

Prometheus instant "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m]))": 1 series, 1 samples; 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z; incomplete=false; retained {}=2.009039548022599 at 2026-10-29T10:54:29Z
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__hegmwnj__env:9090`.
HTTP timing: 2026-11-01T20:09:44.206387158Z to 2026-11-01T20:09:44.208045457Z; 1.658 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m]))"
      ],
      "time": [
        "1793271269"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 6] prometheus_query {"end":"2026-10-29T10:54:29Z","mode":"instant","query":"sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m]))"}
    WINDOW: effective bounds 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z
    SUMMARY: Prometheus instant "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m]))": 1 series, 1 samples; 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z; incomplete=false; retained {}=2.009039548022599 at 2026-10-29T10:54:29Z
    CONTENT: {"query":"sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T10:54:29Z","until":"2026-10-29T10:54:29Z","series":[{"labels":{},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"2.009039548022599"}]}],"incomplete":false}

<a id="run-2a60a37d-777a-4d73-91fb-e92f47fead2b-7"></a>
### Tool Run 7

**prometheus_query** — Get per-service 5xx request counts over the 60-minute window
Execution: 2026-11-01T20:09:49.539093Z to 2026-11-01T20:09:49.54187Z; durationMs: 2.777.
Evaluation at: 2026-10-29T10:54:29Z

Arguments:

    {
      "end": "2026-10-29T10:54:29Z",
      "mode": "instant",
      "query": "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m]))"
    }

Prometheus instant "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m]))": 3 series, 3 samples; 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z; incomplete=false; retained {job="order-service"}=1.0045197740112994 at 2026-10-29T10:54:29Z
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__hegmwnj__env:9090`.
HTTP timing: 2026-11-01T20:09:49.539225652Z to 2026-11-01T20:09:49.541539478Z; 2.314 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m]))"
      ],
      "time": [
        "1793271269"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 7] prometheus_query {"end":"2026-10-29T10:54:29Z","mode":"instant","query":"sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m]))"}
    WINDOW: effective bounds 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z
    SUMMARY: Prometheus instant "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m]))": 3 series, 3 samples; 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z; incomplete=false; retained {job="order-service"}=1.0045197740112994 at 2026-10-29T10:54:29Z
    CONTENT: {"query":"sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T10:54:29Z","until":"2026-10-29T10:54:29Z","series":[{"labels":{"job":"order-service"},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"1.0045197740112994"}]},{"labels":{"job":"payment-service"},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"1.0045197740112994"}]},{"labels":{"job":"user-service"},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"0"}]}],"incomplete":false}

<a id="run-2a60a37d-777a-4d73-91fb-e92f47fead2b-8"></a>
### Tool Run 8

**prometheus_query** — Get per-service total request counts over the 60-minute window
Execution: 2026-11-01T20:09:49.554798Z to 2026-11-01T20:09:49.55755Z; durationMs: 2.752.
Evaluation at: 2026-10-29T10:54:29Z

Arguments:

    {
      "end": "2026-10-29T10:54:29Z",
      "mode": "instant",
      "query": "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
    }

Prometheus instant "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))": 3 series, 3 samples; 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z; incomplete=false; retained {job="order-service"}=39.17627118644068 at 2026-10-29T10:54:29Z
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__hegmwnj__env:9090`.
HTTP timing: 2026-11-01T20:09:49.554921735Z to 2026-11-01T20:09:49.557223589Z; 2.302 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
      ],
      "time": [
        "1793271269"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 8] prometheus_query {"end":"2026-10-29T10:54:29Z","mode":"instant","query":"sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"}
    WINDOW: effective bounds 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z
    SUMMARY: Prometheus instant "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))": 3 series, 3 samples; 2026-10-29T10:54:29Z to 2026-10-29T10:54:29Z; incomplete=false; retained {job="order-service"}=39.17627118644068 at 2026-10-29T10:54:29Z
    CONTENT: {"query":"sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T10:54:29Z","until":"2026-10-29T10:54:29Z","series":[{"labels":{"job":"order-service"},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"39.17627118644068"}]},{"labels":{"job":"payment-service"},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"11.049717514124294"}]},{"labels":{"job":"user-service"},"samples":[{"timestamp":"2026-10-29T10:54:29Z","value":"9.040677966101695"}]}],"incomplete":false}
