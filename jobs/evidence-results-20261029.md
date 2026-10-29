# Evidence rerun assessment - 2026-10-29

Model: OpenRouter z-ai/glm-5.1. Production source: f3f0e700. Read budget: 30, unchanged. One attempt per case; no automatic or model-failure retries. All cases remain ungraded.

Connectivity smoke passed all four native Tools. Its three Investigations, four exact observations and four associated HTTP reads are in [the smoke report](smoke-20261029-070025-778ace/opencluster-result.md).

| Case | Native outcome | Tool attempts / HTTP reads | Engineering assessment |
| --- | --- | ---: | --- |
| [promql-error-rate](promql-error-rate-20261029-070722-536997/opencluster-result.md) | failed | 10 / 10 | FAILED: intermediate 3.4483% matches truth; final citation validation failed. |
| [logql-deployment-rollout-events](logql-deployment-rollout-events-20261029-071421-de2002/opencluster-result.md) | concluded | 1 / 1 | Three deployments, services and UTC timestamps supported. |
| [find-slow-traces](find-slow-traces-20261029-071609-bffb90/opencluster-result.md) | concluded | 14 / 14 | Examples verified; cited-trace deterministic check passed; population claims need bounds. |
| [service-degradation-rca](service-degradation-rca-20261029-071908-c18832/opencluster-result.md) | concluded / read limit | 31 / 30 | Order-service bottleneck supported; internal root cause unproven; read budget exhausted. |

## What changed and what it proves

Every recorded Integration Tool attempt has its exact bounded observation as submitted to the real provider adapter. Matching HTTP records expose actual method, source, path, parameters, status and precise time-to-headers timestamps. Explicitly blocked attempts have no fabricated HTTP request.

The unchanged upstream parser successfully reads each real exported Agent directory. Supplementary JSON lives under artifacts/. Reports separate answers, canonical facts, deterministic checks, engineering critique and unknown judge verdicts. Full IDs stated in the answer are prominent and their captured operations are named.

The Agent itself was not changed. The rerun still shows guessed labels, repeated invalid query syntax, model-level clipping and unsupported causal claims. Recording success is not answer correctness.

## Recommended next small changes

1. Make current Tool Run citations versus prior-Investigation citations unambiguous, especially when no prior evidence exists. Preserve validation; do not silently discard invalid references.
2. Use observed service/status labels and correct query syntax. Start with a compact cross-service ranking, then query the suspect service and incident window. Narrow or filter logs before requesting more data.
3. Show remaining reads before exhaustion and keep unverified internal mechanisms as hypotheses. Keep the 30-read limit for the next comparison.

Do not interpret these four single-attempt, ungraded cases as Pass^3, Pass@3 or full-suite coverage. Some o11y-bench cases require capabilities the current read-only Tools do not offer.

## Reading the evidence

Open a case report first. Its Tool table links each attempt to the real arguments, endpoint and bounded observation. Raw public Investigation results, capture JSONL, associated Tool results and application logs remain linked. backend.log is the application log; Loki observations contain the queried log data.

Source limits, the Agent's pre-existing 16 KiB model-observation cuts and recorder completeness are separate. Cross-source observations #11 and #19 were cut before provider submission; their exact bounded inputs were retained. Private reasoning, unlimited backend documents and rejected conclude-call arguments are not recorded.

The first failed Prometheus rerun is retained and was not retried. The underlying query value was verified independently, but it produced no valid final answer. Trial exceptions remain visible even when Harbor exits with process code zero.

Smoke's full three-Investigation history is in smoke.json and the shared observation capture. Its root ATIF represents only the final Tempo connectivity Investigation.
