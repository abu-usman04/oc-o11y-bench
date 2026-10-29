# Benchmark evidence and report improvements

Status: implementation, independent reviews and the authorized live rerun completed on 2026-10-29. All evidence captures are complete. Three original cases concluded; Prometheus failed native conclusion validation and was retained without retry. No judge verdict or full-suite pass is claimed. Review baseline: 01c83dd8da7652b3d2059e07722650b27986bbc7.

## Critique before implementation

The current report reproduces JSON without assessing whether it answers the question. Diagnostic JSON also breaks the unchanged upstream transcript parser. Public Tool Run summaries omit the actual observations and cannot support a complete audit. Raising the read limit or choosing a different model would hide these measurement problems.

Keep these changes outside the production repository. Do not add production persistence, another reasoning loop, a recording proxy, a new judge, or a general observability framework. Use the existing application Completer interface to observe bounded Tool results sent to the real provider. A benchmark-only entry point may record read-request metadata through the standard HTTP transport; it must forward requests and responses unchanged and must never record headers or model messages. Identify that instrumentation in the build manifest.

The previous Tempo and cross-source answers contain full trace IDs. Make them visible instead of changing the original answers. A missing requested trace ID must be reported as missing, never supplied by the report writer.

## Scope and sequence

1. Fix grading compatibility first. Keep trajectory.json as the only root JSON transcript in agent/. Put Investigation, Integration, observation, request and failure artifacts in agent/artifacts/. Keep upstream questions and grader code unchanged. Test the complete exported directory with the real upstream parser.
2. Make each report readable. Lead with the original answer, execution status, grading status and remaining uncertainty. Show cited Findings, representative trace IDs, one row per Tool attempt, actual observations, failed/empty/truncated results, duplicate calls, budget use, time semantics and links to raw evidence. Explain each artifact's API origin. Do not present model claims as independently verified facts or turn unavailable scores or durations into zero.
3. Retain real evidence. Build the pinned production source with a small external benchmark entry point using the existing application and real provider adapters. Record the bounded Tool observations as passed to the provider, their real call IDs, and matching observability read method/path/parameters/status/timestamps. Do not record assistant reasoning, Authorization headers or credentials. Scope observations by Investigation trace ID and transcript position plus real call ID; join the trace ID to the Investigation using its structured application log. Correlate endpoint records by the same trace, exact configured source origin, tool parameters and call time interval; leave ambiguity unmatched. Limit each capture record to 128 KiB and the complete capture to 8 MiB; record overflow or failure explicitly, preserve provider inputs unchanged, and fail capture acceptance when evidence is incomplete. Filter request capture to the three configured origins and supported read endpoints. Store captures privately until runtime redaction/export. Declare any unmatched request or missing observation; do not reconstruct missing payloads from summaries.
4. Retain the current evaluation conditions. Keep control-plane commit f3f0e700c5927f94e893681e4b12bf40b741ebff, benchmark commit b66d8cfbbe309d2e03e9a301baea056d9718b71b, Harbor 0.24.0, OpenRouter z-ai/glm-5.1, original questions, and the default 30-read budget. Build and record an instrumentation hash. Preserve user files, old jobs and the local upstream formatting edit.
5. Verify before spending model usage. Follow red then green for each slice. Keep the Python adapter/report tests in their existing file. Add one focused Go httptest.Server file for the new recorder at the real provider SDK seam. Check parser compatibility, exact SDK forwarding, observation fidelity, metadata origin, redaction, trace visibility, failed calls and bounded capture. Run formatting, lint, typing, build and the complete relevant suites.
6. Rerun connectivity smoke, then Prometheus, Loki, Tempo and cross-source once each, sequentially, without grading. Compare each report with canonical facts read from a disposable original benchmark stack at that run's clock; also run applicable deterministic checks. These checks must remain separate from an LLM judge verdict. Retain failures, do not automatically retry, and do not count ungraded completion as a benchmark pass.
7. Review the complete change against this plan and repository standards; fix substantive findings, commit the work, and report observed results and limitations. Remove trial containers and temporary credential files. Do not create a PR or merge production changes.

## Test seams and acceptance

The approved seams remain the public control-plane HTTP adapter and exported artifacts. Strengthen the export seam with the real upstream parser over the actual directory layout. The capture requirement additionally uses the existing public Completer interface and real provider SDK against httptest.Server; it does not test private Agent implementation details.

Acceptance requires unchanged upstream parser success over a real new job directory; one readable report per run with visible trace IDs when the Agent supplied them; every native Tool attempt represented, with actual bounded observation or an explicit missing reason; endpoint details distinguished from control-plane API provenance; no configured secrets in artifacts; unchanged default read budget; and clearly separated execution, deterministic checks, canonical facts and judge verdicts.

## Expected folder changes

Keep opencluster_bench/agent.py for Harbor export, runtime.py for API execution and safe artifact export, report.py for readable rendering, and __main__.py for building and running. Add a small evidence.py only if shared capture-reading and matching logic would otherwise be duplicated. Add environment/recorder.go, environment/recorder_test.go and a small benchmark Dockerfile for the instrumented entry point. Keep tests/test_adapter.py as the sole Python test file.

New jobs contain opencluster-result.md and the existing manifest at job level, trajectory.json and instruction.txt at agent level, and explanatory raw evidence under agent/artifacts/. Store fact-only audit outputs alongside each job, outside the transcript directory. JSON stays valid JSON; explanations belong in metadata and the readable report.

## Known limits

This is a selected-case evaluation, not a full benchmark claim. Current Tools do not cover all o11y-bench tasks. A correct bottleneck diagnosis may still leave its internal trigger unknown. The recorder retains bounded observations supplied to the provider adapter, not private model reasoning or an unlimited backend document. HTTP metadata describes actual requests; response timing is time to headers unless explicitly measured otherwise.

## Completed verification and results

Fifteen Python tests pass in the existing single test file, including the real Harbor export lifecycle and unchanged upstream parser. The real OpenRouter SDK httptest.Server check and per-record/total capture-bound checks pass in the one Go test file. Ruff lint/format, mypy, instrumented Linux build and distribution builds pass. Independent Spec and Standards reviews have no residual findings after the correlation corrections. Runtime instrumentation remains outside the production repository.

Connectivity smoke concluded three Investigations and verified all four native Tools. The original case attempts produced ten captured observations for the failed Prometheus Investigation, one for Loki, fourteen for Tempo and thirty-one for cross-source. Including smoke, sixty exact bounded observations are retained. Cross-source made thirty source requests and its final read was explicitly blocked by the unchanged limit.

Canonical facts were replayed at each job's scenario clock. Prometheus obtained the correct intermediate 3.4483 percent ratio but supplied invalid prior-evidence citations and produced no valid final answer. Loki's three deployment records and timestamps are supported. Tempo's cited slow traces pass the upstream deterministic check. Cross-source's order-service bottleneck and 10-second peak p95 are supported; its resource-pool mechanism and earlier-user-service contributing-factor claims remain unproven.

Reports now expose native failures even when Harbor exits zero, label assessment certainty as Agent-claimed, put engineering critique before detailed Findings, show stated trace IDs with captured operations, and show actual HTTP time-to-headers timestamps. They distinguish source limits, pre-existing 16 KiB model-observation clipping and recording completeness. Cross-source observations eleven and nineteen were cut by the Agent before provider submission; their exact bounded inputs were retained.

The results index is jobs/evidence-results-20261029.md. All real exported directories pass the unchanged upstream parser and ATIF validation; report artifact links resolve. Configured API keys are absent from inspected job/package artifacts. Temporary credential files and trial/replay containers were removed; pre-existing user containers, local benchmark formatting edits, IDE files and production checkout were preserved.

Remaining product work is deliberately outside this measurement change: improve current-versus-prior citation guidance, use observed labels and valid query syntax, shape compact initial queries before detailed reads, and keep unsupported mechanisms as hypotheses. The rerun demonstrates these limitations rather than hiding them with more reads or model retries.
