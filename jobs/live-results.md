# OpenCluster live results — 2026-10-29

Model: z-ai/glm-5.1 through OpenRouter. Native control-plane commit: f3f0e700.
All runs below are ungraded. No benchmark correctness score or pass rate is claimed.

| Run | Native outcome | Tool attempts (failed) | Findings | Agent seconds | Results |
| --- | --- | ---: | ---: | ---: | --- |
| Connectivity smoke | 3 concluded | 4 (0) | 4 | 119.7 | [Report](D:/Development/oc-o11y-bench/jobs/smoke-20261029-050120-237307/opencluster-result.md) · [All smoke records](D:/Development/oc-o11y-bench/jobs/smoke-20261029-050120-237307/promql-error-rate__TE85Vqa/agent/smoke.json) · [ATIF](D:/Development/oc-o11y-bench/jobs/smoke-20261029-050120-237307/promql-error-rate__TE85Vqa/agent/trajectory.json) · [Logs](D:/Development/oc-o11y-bench/jobs/smoke-20261029-050120-237307/promql-error-rate__TE85Vqa/agent/backend.log) |
| Prometheus | concluded | 8 (0) | 1 | 80.5 | [Report](D:/Development/oc-o11y-bench/jobs/promql-error-rate-20261029-050728-7eebec/opencluster-result.md) · [JSON](D:/Development/oc-o11y-bench/jobs/promql-error-rate-20261029-050728-7eebec/promql-error-rate__bjPigX4/agent/investigation.json) · [ATIF](D:/Development/oc-o11y-bench/jobs/promql-error-rate-20261029-050728-7eebec/promql-error-rate__bjPigX4/agent/trajectory.json) · [Logs](D:/Development/oc-o11y-bench/jobs/promql-error-rate-20261029-050728-7eebec/promql-error-rate__bjPigX4/agent/backend.log) |
| Loki | concluded | 1 (0) | 3 | 37.2 | [Report](D:/Development/oc-o11y-bench/jobs/logql-deployment-rollout-events-20261029-051056-f14e95/opencluster-result.md) · [JSON](D:/Development/oc-o11y-bench/jobs/logql-deployment-rollout-events-20261029-051056-f14e95/logql-deployment-rollout-events__ufLrPi8/agent/investigation.json) · [ATIF](D:/Development/oc-o11y-bench/jobs/logql-deployment-rollout-events-20261029-051056-f14e95/logql-deployment-rollout-events__ufLrPi8/agent/trajectory.json) · [Logs](D:/Development/oc-o11y-bench/jobs/logql-deployment-rollout-events-20261029-051056-f14e95/logql-deployment-rollout-events__ufLrPi8/agent/backend.log) |
| Tempo | concluded | 6 (0) | 6 | 105.6 | [Report](D:/Development/oc-o11y-bench/jobs/find-slow-traces-20261029-051749-8f6496/opencluster-result.md) · [JSON](D:/Development/oc-o11y-bench/jobs/find-slow-traces-20261029-051749-8f6496/find-slow-traces__nbcYCLZ/agent/investigation.json) · [ATIF](D:/Development/oc-o11y-bench/jobs/find-slow-traces-20261029-051749-8f6496/find-slow-traces__nbcYCLZ/agent/trajectory.json) · [Logs](D:/Development/oc-o11y-bench/jobs/find-slow-traces-20261029-051749-8f6496/find-slow-traces__nbcYCLZ/agent/backend.log) |
| Cross-source | concluded; tool_runs | 31 (3) | 7 | 230.4 | [Report](D:/Development/oc-o11y-bench/jobs/service-degradation-rca-20261029-052132-b9aad7/opencluster-result.md) · [JSON](D:/Development/oc-o11y-bench/jobs/service-degradation-rca-20261029-052132-b9aad7/service-degradation-rca__e5fLRCX/agent/investigation.json) · [ATIF](D:/Development/oc-o11y-bench/jobs/service-degradation-rca-20261029-052132-b9aad7/service-degradation-rca__e5fLRCX/agent/trajectory.json) · [Logs](D:/Development/oc-o11y-bench/jobs/service-degradation-rca-20261029-052132-b9aad7/service-degradation-rca__e5fLRCX/agent/backend.log) |

## What the Agent reported

- Prometheus: approximately 3.4% 5xx share over the requested full hour. Its trace includes an initial wrong-label query, label inspection and corrected status-label queries.
- Loki: three v2.5.0 deployment records, with service names and deployment timestamps.
- Tempo: slow checkout and payment examples, including a 17.6-second checkout trace. Search truncation is stated in the Conclusion.
- Cross-source: order-service dominated checkout latency. The underlying internal cause remained unresolved, and the Investigation reached the 30-read budget; the blocked extra read remains in the Tool history.

## Reading the records

Tool records retain purpose, arguments, effective windows, outcomes, errors, truncation, source identifiers and timestamps. Findings retain their Tool Run citations. Token totals and available latency are recorded.
Full Tool-result bodies and private model reasoning are not persisted. Smoke's full three-Investigation history is in smoke.json; its root ATIF represents the final smoke Investigation.
Harbor prints an empty mean of 0 when verification is disabled. That is not a graded score for these runs.
Agent seconds exclude image building, bootstrap, verification and Harbor cleanup.

## Infrastructure fixes and retained attempt

Windows checkout CRLF conversion prevented Linux script execution; restored files were verified against the pinned Git tree and future clones retain LF. Windows cp1252 decoding then broke Harbor postprocessing of a Unicode trajectory; project launchers and the Harbor subprocess now use UTF-8.
The [first Tempo attempt](D:/Development/oc-o11y-bench/jobs/find-slow-traces-20261029-051308-f3b550/opencluster-result.md) is retained: the Agent concluded, but Harbor failed during postprocessing. The successful rerun is listed above.

## Reproduction

The original upstream checkout's local Tempo-question line wrapping was preserved. These case runs used the clean pinned checkout at .work/benchmark-pinned. The helper .work/run-pinned.py selects it; run it from this workspace with a case name and --no-grade.
Config and secrets are excluded from version control and package artifacts. No configured keys were found in the inspected successful job artifacts.
