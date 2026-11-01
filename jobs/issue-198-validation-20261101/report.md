# Issue #198 validation — November 1, 2026

The bounded observations are now independently inspectable, and the two new Tempo samples have correct deterministic service counts. This does not establish reliable autonomous RCA: both RCA answers make material unsupported causal claims, despite all six local upstream rubric grades being 1.0. No release-readiness, full-suite benchmark, Pass@N, Pass³, or ranking claim is made.

## Revisions and method

- Application evaluated: `f6154db2d418d355142b89fce05bbb894ef273fd`.
- Final control-plane revision: `0e55641e4f977d05517d9f26d3d65bee13a5b330`; only Makefile/README and the existing end-to-end Investigation fixture differ from the evaluated application revision. The test-only correction distinguishes the public Tool name from the Relay capability ID.
- Both archived builds produced the same instrumented executable SHA-256: `5234d0e07dc7de22454dfa1e8d7735eaa9ea9f1d14f5851c70a18bc4608f0014`. [Independent rebuild/parity record](binary-parity.json). Embedded toolchain is Go 1.26.10; the existing recorder tests passed during both builds.
- Benchmark adapter: `bf5dd0fbaab7e49d98db9651b493139ec90901fa`; instrumentation SHA-256 `078e727d8caec7b750bdb3e1222f69e854ec9be68efa5f23a16bc8458b55f2c1`.
- Unmodified upstream: `b66d8cfbbe309d2e03e9a301baea056d9718b71b`, verified tree `5bc5734e7dc95baa6808e5cb7b43992787960b42`. Model `openrouter/z-ai/glm-5.1`, 30-read budget, one trial/attempt per job, Harbor 0.24.0, and each case's exact October 29 scenario clock were preserved.
- Tempo/RCA were run first and repeated before the same Prometheus/Loki cases. These are six jobs across four selected cases, plus one unscored connectivity smoke, not broader coverage or a statistical reliability estimate.
- Original manifests remain unchanged. They attribute actual model execution to f6154db; the separate parity record establishes the final revision's identical executable. No full prompts, private model reasoning, or remote delivery acknowledgments were added.

## Results

| Case / attempt | Tool attempts / source HTTP reads | Empty | Failed | Input / output tokens | Agent seconds | Local rubric | Engineering verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| [Tempo 1](../find-slow-traces-20261101-195453-b285ce/opencluster-result.md) | 15 / 15 | 5 | 0 | 88,237 / 5,171 | 52.3 | 1.0 | Partial: correct sample counts; completeness and latency overclaims |
| [RCA 1](../service-degradation-rca-20261101-195753-abd4cd/opencluster-result.md) | 30 / 30 | 8 | 5 | 221,406 / 8,781 | 131.8 | 1.0 | Failed: unsupported database cause, timing and trace attribution |
| [Tempo 2](../find-slow-traces-20261101-200154-454c7c/opencluster-result.md) | 4 / 4 | 0 | 0 | 31,436 / 3,437 | 33.3 | 1.0 | Partial: correct sample counts; broad latency attribution unsupported |
| [RCA 2](../service-degradation-rca-20261101-200528-0dcd72/opencluster-result.md) | 28 / 28 | 9 | 1 | 332,543 / 8,758 | 89.6 | 1.0 | Failed: unsupported pool exhaustion, cache mechanism and causal timing |
| [Prometheus](../promql-error-rate-20261101-200856-304a7f/opencluster-result.md) | 8 / 7 | 1 | 1 | 31,390 / 2,893 | 42.3 | 1.0 | Supported: approximately 3.39%, with fractional increase estimates |
| [Loki](../logql-deployment-rollout-events-20261101-201055-6b14ea/opencluster-result.md) | 1 / 1 | 0 | 0 | 8,856 / 854 | 11.2 | 1.0 | Supported with qualification: deployment starts, not proven completion |

[Machine-readable metrics and ordinal lists](results.json). No nonexecuted budget/duplicate attempts were recorded. One Prometheus discovery validation failed before source HTTP, hence eight attempts but seven network reads. Agent seconds are the adapter's admission-to-terminal polling interval; they exclude build/seed/grading and subsequent observation retrieval. Shared-host scheduling, differing samples and query choices prevent a causal performance comparison.

The historical totals were 33,508 / 9,863 / 46,485 / 101,224 Agent tokens for Prometheus / Loki / Tempo / RCA. New Tempo totals vary from 34,873 to 93,408; new RCA totals are 230,187 and 341,301. These measurements justify reporting variability and investigating query choice; they do not justify a performance claim or additional compaction, caching, planning, or larger read budgets.

## Exact evidence and independent checks

All 86 Tool-result texts in the six evaluation jobs match their on-demand retained observations exactly. The separate connectivity smoke matched four more. Each job preserves `tool-results.json`, `retained-observations.json`, the original Investigation, original answer/trajectory, HTTP metadata, logs, and unchanged rubric outputs. The recorder observes the existing Completer boundary, not a remote-provider delivery receipt.

- Tempo 1, Run 5: 20 returned checkout traces, user-service 10 and payment-service 6; webapp/gateway/order-service 20 each.
- Tempo 2, Run 1: 20 returned checkout traces, user-service 12 and payment-service 5; webapp/gateway/order-service 20 each. Both counts were recomputed from trace lists, once per service per trace. Neither sample has missing service statistics. The historical sample's 12/20 and 5/20 remains preserved and is not retroactively replaced by the new 10/20 and 6/20 sample.
- Handler-span examples occupy about 72% of their individual traces. They do not prove exclusive CPU/own-processing time, identify missing database spans, or certify every returned trace's bottleneck. A full search page establishes possible incompleteness, not additional observed records; a false incompleteness flag does not prove a population census.
- RCA 1's database logs end at 04:56:30, before its claimed 05:00–05:51 peak; the 2,575 ms query is at 01:48:40. The 25 ms payment child is in Run 21, not the cited representative Run 17. Rate-based mean and estimated p99 observations are useful, but job-level queries within a selected hour do not establish global onset or endpoint-specific causality.
- RCA 2 again interprets missing child spans as database operations and infers pool exhaustion/11–14 second waits without direct support. Database warnings precede the peak, while visible connection timeouts start at 08:16, after it. Cache lag/stale keys/memory near the user-service excursion establish association, not a verified cache mechanism or checkout propagation.
- Prometheus returns an explicit user-service zero, not an absent series. Its estimated 2.00904 / 59.2667 increases support approximately 3.39% over the 60-minute lookback with equal instant bounds.
- Loki returns deployment-started events at 01:47:00Z and 07:55:00Z. A tentative coordinated-rollout hypothesis is distinguishable from proof; “all upgraded” overstates completion/readiness.

Each job includes independent sample/span extraction in `engineering-observations.json` and detailed, explicitly separate engineering notes in `fact-audit.json`. Canonical grader replay facts never substitute for the Agent's actual returned sample.

## Source incompleteness, clipping and storage

| Attempt | Source-incompleteness flag ordinals | Model-clipped ordinals | Total prepared UTF-8 bytes | Largest observation bytes |
| --- | --- | --- | ---: | ---: |
| Tempo 1 | 5 | none | 24,311 | 7,703 |
| RCA 1 | 6, 13, 14, 16, 18 | 13, 16, 18, 28 | 116,856 | 17,221 |
| Tempo 2 | 1 | none | 12,849 | 7,832 |
| RCA 2 | 5, 6, 12, 13, 14, 15, 16, 19, 20, 21, 22, 25, 28 | 16, 19, 20, 21, 22, 28 | 199,372 | 16,850 |
| Prometheus | none | none | 7,276 | 1,831 |
| Loki | none | none | 1,753 | 1,753 |

Byte sizes above were recomputed with explicit UTF-8 decoding and independently checked against the saved texts. Review corrected a Windows-default decoding error in draft totals; original observations were unchanged.

Source flags are conservative indications of possible incompleteness. Model clipping is independent, including list omission that need not end in a byte-cut marker. Headers/arguments explain observations larger than the unchanged 16 KiB content budget; every complete text remains below the 64 KiB storage ceiling. Report display excerpts are a third presentation limit, explicitly labelled, and do not replace the complete saved text.

[Measured PostgreSQL datum size, INSERT execution and WAL costs](../issue-198-storage-20261101/report.md) remain the Phase 2 storage evidence. Their single local replay excludes lock acquisition, network/encoding and commit fsync; do not interpret it as statistically established end-to-end write latency. The invalid Windows text-mode replay is retained and excluded. Observations are sensitive operational data, retained with their owning Investigation; there is no independent evidence TTL or new retention service.

## Verification and remaining acceptance

The complete default `make verify` passed with exit 0 on final control-plane revision `0e55641e4f977d05517d9f26d3d65bee13a5b330`, using real PostgreSQL/listeners and Kubernetes end-to-end fixtures. Both modules, vulnerability/license checks, deployment validation/build/tests and secret-history scanning completed in the same run. [Exact command, environment, revisions and results](verification.json); [complete successful output](release-gate.log). This is a code gate result, not a certification of RCA conclusions. Both vulnerability scans report zero reachable vulnerabilities and zero in imported packages, while noting three advisories in required modules whose affected code does not appear to be called. The license scanner also reports non-Go assembly inspection limits; these qualifications remain in the verification record and complete output. [Required-module advisory details](vulnerability-details.log).

Focused unit/race/PostgreSQL/HTTP/SSE/authorization/lease checks, both code-review axes, all 18 benchmark adapter tests, Ruff, package mypy, pinned Mintlify build/link checks, OpenAPI/docs contracts, and the original repository's 464-commit secret-history scan passed. Final binary parity and recorder tests passed. Existing local Tempo guidance, benchmark HTML and upstream task edits remain outside authored commits.

Environment attempts are preserved: nested Docker path/Git metadata/scratch formatting checks, Windows Docker endpoint failure, isolated upstream stat-cache normalization, test-container loopback forwarding, the reproduced cross-package fixture cleanup failure, and grader loopback preflights. Grader sidecar preflights used no judge/model request; corrected grading uses the upstream's existing private bridge bind/connect settings. No benchmark specification or rubric was modified.

The fixture cleanup regression passed with root-package serialization while retaining every test and `-race`. A subsequent complete gate passed control-plane race tests in 613.257 seconds and PostgreSQL race tests in 403.339 seconds, then failed the existing Investigation end-to-end fixture, which confused the public Tool name with a dotted Relay capability ID. Its focused reproduction failed in 103.242 seconds; correcting only the three public-name references passed in 46.920 seconds, with all assertions and deadlines unchanged. [Preserved failed gate and RED/GREEN record](release-attempt-1fa6933.json). The end-to-end command was left unchanged because it has one container-test package. The subsequent complete default `make verify` passed all these stages without omitting tests or race coverage. The initial archived Relay copy failed Go VCS stamping before the end-to-end fixture started. A clean isolated Git checkout of the same Relay revision b55d544898b3e75c374931b7a2a43fa29b4064b3 is now selected through the existing OC_E2E_RELAY_SOURCE harness input. Its real Kubernetes proof passed in 50.640 seconds before the complete gate rerun. The original Relay working tree was not modified.

Even after a successful code release gate, these RCA outcomes remain an acceptance concern. The appropriate result is a reviewable implementation with explicit reasoning limitations, not a claim that rubric passes certify autonomous root-cause correctness. No second judge, causal validator, query rewriter, additional provider, Hubble integration, or frontend change was added.