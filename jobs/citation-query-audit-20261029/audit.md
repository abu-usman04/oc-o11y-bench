# OpenCluster capability, run and benchmark audit — 29 October 2026

**Local rubric result: 4/4 selected cases passed, each at 1.0. All four Investigations concluded.**
**Engineering result: the Tempo and cross-source answers contain material errors or unsupported causal claims. Do not treat the rubric result as proof that every conclusion is correct.**

**Release gate: make verify DID NOT PASS. A progress-stream test also fails on the unchanged baseline; the pinned Go 1.26.9 runtime has GO-2026-6809.**

The Agent can retrieve and cite useful metrics, logs and traces. This run does not establish reliable autonomous root-cause determination. The defensible cross-source conclusion is: order-service bottleneck established; database involvement suspected; causal mechanism unresolved.

## Leaderboard-style local summary

| Model | Effort | Selected solved | Local Pass@1 | Pass³ | Pass@3 | Mean Agent tokens/trial | Cost/trial | Global rank |
|---|---|---:|---:|---|---|---:|---|---|
| z-ai/glm-5.1 | Provider default | 4/4 | 100% | N/A | N/A | 47,770 | Unavailable | Not established |

This is a local evaluation using unchanged upstream checks, truth queries, rubric, scoring and Anthropic SDK judge through OpenRouter. It is not an official approval or submission. The leaderboard requires three attempts per task; this audit has one attempt on 4/64 tasks (6.25% task coverage). Sixty tasks were not run. Pass³, Pass@3 and a comparable rank cannot be calculated. Actual billable cost and judge token totals were not retained; no estimate is presented as actual cost.

[Official scoring definitions](https://o11ybench.ai/leaderboard/) · [OpenRouter Anthropic compatibility](https://openrouter.ai/docs/cookbook/coding-agents/claude-code-integration)

## Results by case

| Case | Category | Native outcome | Rubric | Reads / 30 | Empty | Failed | Model cuts | Agent tokens | Seconds |
|---|---|---|---|---:|---:|---:|---|---:|---:|
| [promql-error-rate](../promql-error-rate-20261029-105457-a33cd3/opencluster-result.md) | prometheus_query | concluded | passed (1.0) | 6 | 0 | 0 | none | 33,508 | 44.4 |
| [logql-deployment-rollout-events](../logql-deployment-rollout-events-20261029-105757-b7a9ea/opencluster-result.md) | loki_query | concluded | passed (1.0) | 1 | 0 | 0 | none | 9,863 | 20.2 |
| [find-slow-traces](../find-slow-traces-20261029-110031-61566d/opencluster-result.md) | tempo_query | concluded | passed (1.0) | 10 | 3 | 0 | none | 46,485 | 61.6 |
| [service-degradation-rca](../service-degradation-rca-20261029-110353-fca189/opencluster-result.md) | investigation | concluded | passed (1.0) | 14 | 4 | 0 | [8] | 101,224 | 113.2 |

All actual Tool results and endpoint details remain in each linked report and its artifacts. Scores were obtained from saved answers; grading did not call the Agent again. No failed attempt was replaced by a better attempt.

## Statistics and capability by benchmark category

| Category | Original tasks | Attempted | Rubric solved | Unrun | Current boundary |
|---|---:|---:|---:|---:|---|
| dashboarding | 7 | 0 | 0 | 7 | Unsupported: no Grafana dashboard write Tool. |
| grafana_api | 6 | 0 | 0 | 6 | Unsupported: no Grafana datasource/dashboard API Tool. |
| investigation | 11 | 1 | 1 | 10 | Cross-source reads shipped. This run establishes the main service, but not the claimed DB mechanism or precise onset. |
| loki_query | 10 | 1 | 1 | 9 | Bounded log excerpts shipped. Aggregate LogQL counts/percentiles are unsupported; excerpts cannot establish exhaustive totals when limited. |
| prometheus_query | 17 | 1 | 1 | 16 | Scalar/vector/range PromQL and metric-name discovery shipped; 16 tasks unrun. Native histogram payloads are unsupported. |
| tempo_query | 13 | 1 | 1 | 12 | Bounded trace search/get shipped. TraceQL metrics/tag discovery and exhaustive service inventories are unsupported. |

Do not claim all 64 tasks are supported. At least the 13 Grafana API/dashboard tasks require absent capabilities. Loki aggregate and Tempo metrics tasks expose further gaps. Unrun tasks are not recorded as passed or failed; tool availability does not guarantee correct reasoning.

## Independent correctness review

### promql-error-rate

Original rubric: **passed**, score 1.0. [Answer, criterion explanations and evidence](../promql-error-rate-20261029-105457-a33cd3/opencluster-result.md).

- Supported: the full-hour 5xx share is about 3.4%; canonical truth is 0.033898. The ratio is based on 60-minute counter increases, not one short slice.
- Counter increases such as 2.01 and 59.27 are extrapolated estimates, not exact integer event counts. Six reads completed without empty reads or model clipping.

### logql-deployment-rollout-events

Original rubric: **passed**, score 1.0. [Answer, criterion explanations and evidence](../logql-deployment-rollout-events-20261029-105757-b7a9ea/opencluster-result.md).

- Supported: exactly three returned deployment log lines name user-service (01:47 UTC), order-service and payment-service (07:55 UTC); canonical counts and service names agree.
- The shared deployment time suggests coordination but does not prove coordination or an incident trigger.

### find-slow-traces

Original rubric: **passed**, score 1.0. [Answer, criterion explanations and evidence](../find-slow-traces-20261029-110031-61566d/opencluster-result.md).

- Supported: checkout trace 4715b7764646608b1a48f1b3a2cec04b is 17.648s, including 12.706s in order-service; payment trace 6661aabbc96f535480066bbe28c66e55 is 3.181s, including 2.290s in payment-service. The deterministic full-ID check passed.
- Incorrect: the answer says user-service occurs in 10/20 checkout search results and payment-service in 6/20. Actual Tool Run 4 contains 12/20 and 5/20 respectively. The judge used a different nondeterministic search sample and did not catch this mismatch.
- Unproven: all-route, job-level P99 and service presence do not establish user-service as responsible for checkout latency. No user-service checkout span was fetched to demonstrate that claim.
- Scope: 20 checkout and 5 payment results are returned subsets, not exhaustive day-wide totals. Hitting the limit conservatively means possibly incomplete; it does not prove more results exist. Existing Agent feedback misleadingly states that the source held more.
- Three empty reads remain: invented checkout/payment service identifiers and a guessed route label. TraceQL syntax was valid and there were no model-observation cuts.

### service-degradation-rca

Original rubric: **passed**, score 1.0. [Answer, criterion explanations and evidence](../service-degradation-rca-20261029-110353-fca189/opencluster-result.md).

- Supported: order-service is the principal bottleneck; canonical peak p95 ranks order-service 10s, user-service 4.5s, payment-service 2.2s. Trace 4715b7764646608b1a48f1b3a2cec04b has 12.706s in order-service; 0595f4e097fcacc5724644e76d76ad60 has 5.860s with a 25ms user-service child.
- Incorrect: payment-service was unaffected conflicts with Tool Run 4 returning a 1.858s POST /api/payments trace, and canonical payment p95 reaching 2.2s. Less affected is supported; unaffected is not.
- Metric semantics: Runs 5, 8 and 10 use raw cumulative duration_sum / duration_count. The 45-to-160ms values are cumulative means, not incident-window means. Use rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m]) for a recent mean or histogram_quantile for tail latency.
- Unproven: database degradation is promoted to cause despite missing DB metrics/spans and no correlation of slow-query logs with the example traces. Missing child spans identify uninstrumented time, not DB wait. DB involvement is a hypothesis; the causal mechanism remains unresolved.
- Timing: a 04:13 DB timeout on a 37ms GET /api/cart failure does not establish the onset of sustained checkout slowness. Claims about precise onset/recovery and user-service contributions exceed the evidence.
- Efficiency improved to 14 reads, four empty and no HTTP errors, but Run 8 still hit the existing 16KiB model-content cut. Fourteen reads left room to test competing explanations; stopping early did not make the mechanism established.

## What changed, what improved, what remains

- Citation handling: a fresh Investigation now constrains unavailable prior citations to an empty array; current reads use run_refs. Brief/history citations and backend validation remain. Invalid references receive explicit repair guidance rather than being silently accepted.
- Query guidance: remaining reads are visible; labels, focused windows, compact aggregates, correct LogQL alternatives, TraceQL duration syntax, trace IDs and uncertainty receive concise guidance. No new planner, query rewriter, framework or dependencies were added.
- The new Prometheus case used 6 reads instead of the previous failed run with 10 reads; Tempo used 10 rather than 14; cross-source used 14 rather than exhausting 30. No duplicate calls or HTTP query errors occurred in these four runs. Seven empty reads and one model-content cut remain. These are single-run observations with fresh scenario clocks, not a controlled statistical improvement estimate.
- Reference validation establishes that cited evidence is available. Whether the evidence supports each claim still requires checking the actual returned observations.

- More reads would not fix the remaining failures: the RCA had 16 reads left. Its bottlenecks are query semantics, scope and causal certainty. The grader also missed unsupported extra claims because its rubric is narrower than a full correctness audit.
- Next small fixes should make returned-sample counts deterministic, state possibly incomplete rather than claiming proven overflow, require query-local timing/rate semantics, and keep unobserved mechanisms as hypotheses. Add focused regressions and compare a frozen scenario before expanding the benchmark. Avoid a generic causal-validation framework or a larger read cap.

## Verification and provenance

**Full gate: make verify did not pass.**

**Passed:** Focused Agent/provider/Loki/Tempo Go tests; OpenAPI and generated documentation validation; gofmt, go vet, golangci-lint and both module builds; Real PostgreSQL race suite; All previously failing SSH-dependent HTTP tests after host-network correction; test/e2e race suite; 18 benchmark unit tests; Benchmark ruff and mypy; Wheel and source package build; License checks; Compose/Helm validation, deployment image build and deployment test; API key scan of 99 result/audit files; packages exclude completed config/jobs/.work; temporary credential files removed; Git history secret scan.

**Existing test failure:** TestLiveProgressEventMatchesSerializedSchema reproduces on both the changed commit and unchanged baseline. [Changed-commit log](verification/verification-network-recheck.log), [baseline log](verification/baseline-progress-check.log).

**Networking:** Initial nested-container SSH loopback failures passed with host-network verification; no source workaround added. [Rechecks and e2e log](verification/network-and-e2e-verification.log).

**Security:** the existing pinned Go 1.26.9 toolchain has [GO-2026-6809](https://pkg.go.dev/vuln/GO-2026-6809), fixed in Go 1.26.10. Update and rebuild before calling the release gate green. [Vulnerability scan](verification/remaining-verification.log).

**History secrets:** Passed: 461 commits, 11.46 MB scanned; no leaks found. [Remaining gate log](verification/remaining-gates.log).

Production commit: `b1b8706d10a43a48f1212ae6b240146c23dcb541` on `codex/agent-citations-queries`. Original refactoring checkout is preserved.
Benchmark commit: `b66d8cfbbe309d2e03e9a301baea056d9718b71b` (version 1.1.0). Judge: `anthropic/claude-haiku-5.5@high through OpenRouter Anthropic Messages endpoint`.
Recorder hash: `2a23b52861be31ad0f0532ce1a197c25b19c0a77b53044c359fa12ca1834f479`. Binary hash: `af4407b32c55af89189e22dd392c9be0f77385a3e2542cc70584921938b1cead`.
Smoke passed all three Integrations with four non-empty native observations, including trace retrieval. Unit regressions were written failing first. Benchmark unit tests, lint, type checking and package build passed. Standards and Spec reviews found reporting issues that were fixed before final audit; their remaining production note is a duplicated error string. No PR was created or merged.

## Standards

Production: no hard violations; one minor duplicated error string. Benchmark: execution-status and executing-grader provenance findings were fixed and rechecked.

## Spec

Production: no findings. Benchmark: preserving engineering notes and execution status was fixed and regression-tested; both reviewers checked the final case/category arithmetic and scope claims.

## Reading the artifacts

| File | Origin and meaning |
|---|---|
| opencluster-result.md | Human-readable answer, upstream criterion verdicts, independent engineering corrections and per-read endpoints. |
| */agent/artifacts/investigation.json | Public GET /api/v1/investigations/{id}; native outcome, summary and Tool Run metadata. |
| */agent/artifacts/tool-results.json | Exact bounded Tool observations submitted to the provider adapter, with correlated method, source, path, parameters, status and timestamps. These are parsed Tool results, not unlimited HTTP bodies. |
| */agent/trajectory.json | Upstream-readable ATIF transcript with actual retained Tool observations and saved final answer; not private model reasoning. |
| local-grading/grading_details.json | Original upstream per-criterion score, outcome, explanation and answer quotes. |
| local-grading/truth.json | Canonical benchmark truth from a separate replay at the recorded scenario clock. Tempo search can return a different sample from the Agent search. |
| fact-audit.json | Canonical facts/checks plus explicitly labelled independent engineering corrections; the Agent answer is retained unchanged. |
| grading-context.json | Judge model, endpoint, benchmark identity and local-evaluation scope. No key. |
| audit-data.json | These four selected results, category inventory and verification summary in valid JSON. |

JSON does not support comments. Field names, endpoint metadata and this index supply the explanation. A successful HTTP read is not a correct answer. Instant Prometheus reads legitimately have equal bounds while a [60m] expression reads the preceding hour; public execution timestamps have second precision. HTTP timestamps retain subsecond precision. Opaque source identifiers remain stable backend references; reports name the Integration, Tool, endpoint and trace operation for people.
