# OpenCluster benchmark assessment

Model: openrouter/z-ai/glm-5.1

**Ungraded: no LLM judge verdict or benchmark pass score.**
Harbor process exit code: 0
Harbor trial errors: 1
Execution completion, answer correctness and benchmark grading are separate outcomes.

## Answer

> No answer was produced.

### Question

    Over the last hour, what overall share of HTTP requests returned 5xx across user-service,
    order-service, and payment-service? In Prometheus those names are the `job` label values on
    `http_requests_total` for API traffic here - ignore webapp and api-gateway. Report the share for the
    full 60-minute window aggregated together, not a conclusion from a single short slice of the timeline.

Investigation: **failed**; Agent-claimed assessment: **unavailable**.
Tool attempts: **10**, including **0 failed/blocked** and **0 limited**.
Read budget: **30** (unchanged); stopped by: **unavailable**.
Tokens: 45914 input / 3426 output.
Agent elapsed: 90.6 seconds.
Exact repeated requests: none.
Model-observation clipping: none detected.

**Investigation failure:**

    the reasoning step could not run: malformed_output: openrouter/z-ai/glm-5.1: a finding cites unavailable prior evidence

### Trace examples in the answer

No trace example was stated or requested.

## Independent checks

Canonical facts were read from the original benchmark stack at this run's scenario clock. They are independent evidence, not a judge verdict.
- **Engineering review (not an upstream judge verdict)**: FAILED ATTEMPT: no valid final answer. The native Agent rejected unavailable prior-evidence citations after 10 successful backend reads. This is a conclusion-contract failure, not a connectivity or capture failure.
- **Engineering review (not an upstream judge verdict)**: Tool Run #8 measured 0.034482758620689655 (3.4483%), matching the canonical ratio at this scenario clock. A correct intermediate measurement does not turn the failed trial into a pass.
- **Engineering review (not an upstream judge verdict)**: The Agent repeatedly guessed the code label before inspecting actual labels in #7. The metric uses status. Keep the read budget; improve label discovery and current-versus-prior citation guidance. This failed attempt was not retried.

**The final response states 5xx share accurately.**

    Matching metrics exist in the snapshot window: Query returned 1 result: 0.034483
Fact displays are excerpts. [Full canonical queries and returned data](fact-audit.json)

### Findings and uncertainty


### Tool attempts

| Run | Tool | Outcome | Purpose |
| --- | --- | --- | --- |
| [#1](#run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-1) | prometheus_discover_metrics | succeeded | Discover the exact metric name for HTTP request counts to compute 5xx share |
| [#2](#run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-2) | prometheus_query | succeeded, empty | Compute overall 5xx share across the three services for the full 60-minute window |
| [#3](#run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-3) | prometheus_query | succeeded, empty | Break down 5xx share per service for context |
| [#4](#run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-4) | prometheus_query | succeeded | Get total request volume per service for context |
| [#5](#run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-5) | prometheus_query | succeeded, empty | Check if there are any 5xx requests at all |
| [#6](#run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-6) | prometheus_query | succeeded | List all HTTP status codes seen across the three services in the window |
| [#7](#run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-7) | prometheus_query | succeeded | Inspect raw series labels to find the status code label name |
| [#8](#run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-8) | prometheus_query | succeeded | Compute overall 5xx share across three services over the 60-minute window using correct label name |
| [#9](#run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-9) | prometheus_query | succeeded | Per-service 5xx share for breakdown |
| [#10](#run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-10) | prometheus_query | succeeded | Per-service per-status increase counts for verification |

### Where these files came from

Control-plane endpoint: `GET /api/v1/investigations/c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e` supplies the public Conclusion and Tool Run records.
`adapterElapsedSeconds` is added by this benchmark adapter. It is not backend telemetry.
Integration configuration comes from `POST /api/v1/integrations/{id}/verify`.
`backend.log` is the OpenCluster process log, not queried Loki log data.
`trajectory.json` is reconstructed ATIF; it contains the Agent's recorded answer and observations, not private reasoning.
[Public result](promql-error-rate__fY68VwW/agent/artifacts/investigation.json) · [Actual Tool observations and HTTP metadata](promql-error-rate__fY68VwW/agent/artifacts/tool-results.json) · [Application log](promql-error-rate__fY68VwW/agent/artifacts/backend.log)

An instant Prometheus read has one evaluation timestamp. A selector such as `[60m]` reads the preceding hour; equal evaluation bounds do not mean an empty lookback.
Public execution timestamps are rounded to seconds by the pinned API. Equal start/finish values do not prove zero duration. Captured HTTP timestamps retain subsecond precision; their elapsed interval measures time to response headers.

<a id="run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-1"></a>
### Tool Run 1

**prometheus_discover_metrics** — Discover the exact metric name for HTTP request counts to compute 5xx share
Read window: 2026-10-29T06:06:58.981457Z to 2026-10-29T07:06:58.981457Z

Arguments:

    {
      "hint": "http_requests",
      "selector": ""
    }

Prometheus metric discovery "http_requests": 1 names, 2026-10-29T06:06:58Z to 2026-10-29T07:06:58Z; incomplete=false
Sources: Prometheus metric-names.

Endpoint: **GET /api/v1/label/__name__/values** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__fy68vww__env:9090`.
HTTP timing: 2026-10-29T07:07:51.912001085Z to 2026-10-29T07:07:51.917586273Z; 5.585 ms to response headers.

Actual request parameters:

    {
      "end": [
        "1793257618.981457"
      ],
      "limit": [
        "51"
      ],
      "match[]": [
        "{__name__=~\".*http_requests.*\"}"
      ],
      "start": [
        "1793254018.981457"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 1] prometheus_discover_metrics {"hint":"http_requests","selector":""}
    WINDOW: this read covered 2026-10-29T06:06:58Z to 2026-10-29T07:06:58Z
    SUMMARY: Prometheus metric discovery "http_requests": 1 names, 2026-10-29T06:06:58Z to 2026-10-29T07:06:58Z; incomplete=false
    CONTENT: {"selector":"{__name__=~\".*http_requests.*\"}","names":["http_requests_total"],"from":"2026-10-29T06:06:58.981457Z","until":"2026-10-29T07:06:58.981457Z","incomplete":false}

<a id="run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-2"></a>
### Tool Run 2

**prometheus_query** — Compute overall 5xx share across the three services for the full 60-minute window
Evaluation at: 2026-10-29T07:06:58Z

Arguments:

    {
      "end": "2026-10-29T07:06:58Z",
      "mode": "instant",
      "query": "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m])) / sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
    }

Prometheus instant "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m])) / sum(increase(ht…": 0 series, 0 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__fy68vww__env:9090`.
HTTP timing: 2026-10-29T07:08:07.912466234Z to 2026-10-29T07:08:07.917333918Z; 4.867 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m])) / sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
      ],
      "time": [
        "1793257618"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 2] prometheus_query {"end":"2026-10-29T07:06:58Z","mode":"instant","query":"sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m])) / sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"}
    WINDOW: this read covered 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z
    SUMMARY: Prometheus instant "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m])) / sum(increase(ht…": 0 series, 0 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false
    CONTENT: {"query":"sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m])) / sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T07:06:58Z","until":"2026-10-29T07:06:58Z","series":[],"incomplete":false}

<a id="run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-3"></a>
### Tool Run 3

**prometheus_query** — Break down 5xx share per service for context
Evaluation at: 2026-10-29T07:06:58Z

Arguments:

    {
      "end": "2026-10-29T07:06:58Z",
      "mode": "instant",
      "query": "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m])) / sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
    }

Prometheus instant "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m])) / sum b…": 0 series, 0 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__fy68vww__env:9090`.
HTTP timing: 2026-10-29T07:08:07.927006906Z to 2026-10-29T07:08:07.929927534Z; 2.921 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m])) / sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
      ],
      "time": [
        "1793257618"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 3] prometheus_query {"end":"2026-10-29T07:06:58Z","mode":"instant","query":"sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m])) / sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"}
    WINDOW: this read covered 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z
    SUMMARY: Prometheus instant "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m])) / sum b…": 0 series, 0 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false
    CONTENT: {"query":"sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m])) / sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T07:06:58Z","until":"2026-10-29T07:06:58Z","series":[],"incomplete":false}

<a id="run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-4"></a>
### Tool Run 4

**prometheus_query** — Get total request volume per service for context
Evaluation at: 2026-10-29T07:06:58Z

Arguments:

    {
      "end": "2026-10-29T07:06:58Z",
      "mode": "instant",
      "query": "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
    }

Prometheus instant "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))": 3 series, 3 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false; retained {job="order-service"}=39.18888888888888 at 2026-10-29T07:06:58Z
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__fy68vww__env:9090`.
HTTP timing: 2026-10-29T07:08:07.937463137Z to 2026-10-29T07:08:07.952399727Z; 14.936 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
      ],
      "time": [
        "1793257618"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 4] prometheus_query {"end":"2026-10-29T07:06:58Z","mode":"instant","query":"sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"}
    WINDOW: this read covered 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z
    SUMMARY: Prometheus instant "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))": 3 series, 3 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false; retained {job="order-service"}=39.18888888888888 at 2026-10-29T07:06:58Z
    CONTENT: {"query":"sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T07:06:58Z","until":"2026-10-29T07:06:58Z","series":[{"labels":{"job":"order-service"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"39.18888888888888"}]},{"labels":{"job":"payment-service"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"10.048433048433049"}]},{"labels":{"job":"user-service"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"9.043589743589743"}]}],"incomplete":false}

<a id="run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-5"></a>
### Tool Run 5

**prometheus_query** — Check if there are any 5xx requests at all
Evaluation at: 2026-10-29T07:06:58Z

Arguments:

    {
      "end": "2026-10-29T07:06:58Z",
      "mode": "instant",
      "query": "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m]))"
    }

Prometheus instant "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m]))": 0 series, 0 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__fy68vww__env:9090`.
HTTP timing: 2026-10-29T07:08:18.070452691Z to 2026-10-29T07:08:18.072902718Z; 2.450 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m]))"
      ],
      "time": [
        "1793257618"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 5] prometheus_query {"end":"2026-10-29T07:06:58Z","mode":"instant","query":"sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m]))"}
    WINDOW: this read covered 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z
    SUMMARY: Prometheus instant "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m]))": 0 series, 0 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false
    CONTENT: {"query":"sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",code=~\"5..\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T07:06:58Z","until":"2026-10-29T07:06:58Z","series":[],"incomplete":false}

<a id="run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-6"></a>
### Tool Run 6

**prometheus_query** — List all HTTP status codes seen across the three services in the window
Evaluation at: 2026-10-29T07:06:58Z

Arguments:

    {
      "end": "2026-10-29T07:06:58Z",
      "mode": "instant",
      "query": "sum by (code) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
    }

Prometheus instant "sum by (code) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))": 1 series, 1 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false; retained {}=58.28091168091167 at 2026-10-29T07:06:58Z
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__fy68vww__env:9090`.
HTTP timing: 2026-10-29T07:08:18.082450018Z to 2026-10-29T07:08:18.087958234Z; 5.508 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum by (code) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
      ],
      "time": [
        "1793257618"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 6] prometheus_query {"end":"2026-10-29T07:06:58Z","mode":"instant","query":"sum by (code) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"}
    WINDOW: this read covered 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z
    SUMMARY: Prometheus instant "sum by (code) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))": 1 series, 1 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false; retained {}=58.28091168091167 at 2026-10-29T07:06:58Z
    CONTENT: {"query":"sum by (code) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T07:06:58Z","until":"2026-10-29T07:06:58Z","series":[{"labels":{},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"58.28091168091167"}]}],"incomplete":false}

<a id="run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-7"></a>
### Tool Run 7

**prometheus_query** — Inspect raw series labels to find the status code label name
Evaluation at: 2026-10-29T07:06:58Z

Arguments:

    {
      "end": "2026-10-29T07:06:58Z",
      "mode": "instant",
      "query": "http_requests_total{job=~\"user-service|order-service|payment-service\"}"
    }

Prometheus instant "http_requests_total{job=~\"user-service|order-service|payment-service\"}": 6 series, 6 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false; retained http_requests_total{instance="order-service:8083", job="order-service", status="…=2863 at 2026-10-29T07:06:58Z
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__fy68vww__env:9090`.
HTTP timing: 2026-10-29T07:08:24.929574147Z to 2026-10-29T07:08:24.932044152Z; 2.470 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "http_requests_total{job=~\"user-service|order-service|payment-service\"}"
      ],
      "time": [
        "1793257618"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 7] prometheus_query {"end":"2026-10-29T07:06:58Z","mode":"instant","query":"http_requests_total{job=~\"user-service|order-service|payment-service\"}"}
    WINDOW: this read covered 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z
    SUMMARY: Prometheus instant "http_requests_total{job=~\"user-service|order-service|payment-service\"}": 6 series, 6 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false; retained http_requests_total{instance="order-service:8083", job="order-service", status="…=2863 at 2026-10-29T07:06:58Z
    CONTENT: {"query":"http_requests_total{job=~\"user-service|order-service|payment-service\"}","mode":"instant","resultType":"vector","from":"2026-10-29T07:06:58Z","until":"2026-10-29T07:06:58Z","series":[{"labels":{"__name__":"http_requests_total","instance":"order-service:8083","job":"order-service","status":"200"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"2863"}]},{"labels":{"__name__":"http_requests_total","instance":"order-service:8083","job":"order-service","status":"500"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"72"}]},{"labels":{"__name__":"http_requests_total","instance":"payment-service:8084","job":"payment-service","status":"200"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"983"}]},{"labels":{"__name__":"http_requests_total","instance":"payment-service:8084","job":"payment-service","status":"500"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"38"}]},{"labels":{"__name__":"http_requests_total","instance":"user-service:8082","job":"user-service","status":"200"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"891"}]},{"labels":{"__name__":"http_requests_total","instance":"user-service:8082","job":"user-service","status":"500"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value"
Display excerpt only; the complete bounded observation is retained in tool-results.json.

<a id="run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-8"></a>
### Tool Run 8

**prometheus_query** — Compute overall 5xx share across three services over the 60-minute window using correct label name
Evaluation at: 2026-10-29T07:06:58Z

Arguments:

    {
      "end": "2026-10-29T07:06:58Z",
      "mode": "instant",
      "query": "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m])) / sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
    }

Prometheus instant "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m])) / sum(increase(…": 1 series, 1 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false; retained {}=0.034482758620689655 at 2026-10-29T07:06:58Z
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__fy68vww__env:9090`.
HTTP timing: 2026-10-29T07:08:37.076641295Z to 2026-10-29T07:08:37.07983095Z; 3.189 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m])) / sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
      ],
      "time": [
        "1793257618"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 8] prometheus_query {"end":"2026-10-29T07:06:58Z","mode":"instant","query":"sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m])) / sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"}
    WINDOW: this read covered 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z
    SUMMARY: Prometheus instant "sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m])) / sum(increase(…": 1 series, 1 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false; retained {}=0.034482758620689655 at 2026-10-29T07:06:58Z
    CONTENT: {"query":"sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m])) / sum(increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T07:06:58Z","until":"2026-10-29T07:06:58Z","series":[{"labels":{},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"0.034482758620689655"}]}],"incomplete":false}

<a id="run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-9"></a>
### Tool Run 9

**prometheus_query** — Per-service 5xx share for breakdown
Evaluation at: 2026-10-29T07:06:58Z

Arguments:

    {
      "end": "2026-10-29T07:06:58Z",
      "mode": "instant",
      "query": "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m])) / sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
    }

Prometheus instant "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m])) / sum…": 3 series, 3 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false; retained {job="order-service"}=0.025641025641025644 at 2026-10-29T07:06:58Z
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__fy68vww__env:9090`.
HTTP timing: 2026-10-29T07:08:37.087728493Z to 2026-10-29T07:08:37.089956577Z; 2.228 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m])) / sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
      ],
      "time": [
        "1793257618"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 9] prometheus_query {"end":"2026-10-29T07:06:58Z","mode":"instant","query":"sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m])) / sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"}
    WINDOW: this read covered 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z
    SUMMARY: Prometheus instant "sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m])) / sum…": 3 series, 3 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false; retained {job="order-service"}=0.025641025641025644 at 2026-10-29T07:06:58Z
    CONTENT: {"query":"sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\",status=~\"5..\"}[60m])) / sum by (job) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T07:06:58Z","until":"2026-10-29T07:06:58Z","series":[{"labels":{"job":"order-service"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"0.025641025641025644"}]},{"labels":{"job":"payment-service"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"0.09999999999999999"}]},{"labels":{"job":"user-service"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"0"}]}],"incomplete":false}

<a id="run-c7f0c538-fcaf-4aa3-a447-c48ff8f99a7e-10"></a>
### Tool Run 10

**prometheus_query** — Per-service per-status increase counts for verification
Evaluation at: 2026-10-29T07:06:58Z

Arguments:

    {
      "end": "2026-10-29T07:06:58Z",
      "mode": "instant",
      "query": "sum by (job, status) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
    }

Prometheus instant "sum by (job, status) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))": 6 series, 6 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false; retained {job="order-service", status="200"}=38.18404558404558 at 2026-10-29T07:06:58Z
Sources: Prometheus instant.

Endpoint: **POST /api/v1/query** - HTTP 200.
Configured source: `http://o11y-stack-promql-error-rate__fy68vww__env:9090`.
HTTP timing: 2026-10-29T07:08:37.096879445Z to 2026-10-29T07:08:37.098954435Z; 2.075 ms to response headers.

Actual request parameters:

    {
      "limit": [
        "51"
      ],
      "query": [
        "sum by (job, status) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"
      ],
      "time": [
        "1793257618"
      ],
      "timeout": [
        "5s"
      ]
    }

Actual observation submitted to the provider adapter:

    [run 10] prometheus_query {"end":"2026-10-29T07:06:58Z","mode":"instant","query":"sum by (job, status) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))"}
    WINDOW: this read covered 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z
    SUMMARY: Prometheus instant "sum by (job, status) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))": 6 series, 6 samples; 2026-10-29T07:06:58Z to 2026-10-29T07:06:58Z; incomplete=false; retained {job="order-service", status="200"}=38.18404558404558 at 2026-10-29T07:06:58Z
    CONTENT: {"query":"sum by (job, status) (increase(http_requests_total{job=~\"user-service|order-service|payment-service\"}[60m]))","mode":"instant","resultType":"vector","from":"2026-10-29T07:06:58Z","until":"2026-10-29T07:06:58Z","series":[{"labels":{"job":"order-service","status":"200"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"38.18404558404558"}]},{"labels":{"job":"order-service","status":"500"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"1.0048433048433048"}]},{"labels":{"job":"payment-service","status":"200"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"9.043589743589743"}]},{"labels":{"job":"payment-service","status":"500"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"1.0048433048433048"}]},{"labels":{"job":"user-service","status":"200"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"9.043589743589743"}]},{"labels":{"job":"user-service","status":"500"},"samples":[{"timestamp":"2026-10-29T07:06:58Z","value":"0"}]}],"incomplete":false}
