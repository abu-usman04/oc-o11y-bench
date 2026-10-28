# Phase 5: real OpenCluster benchmark

Status: approved implementation finished and locally verified. Live acceptance remains pending credentials and a responsive Docker daemon; C: currently has no free space.

- Keep all new code and artifacts in this standalone workspace. Build production code from clean commit f3f0e700c5927f94e893681e4b12bf40b741ebff; preserve the existing control-plane working directory.
- Use o11y-bench commit b66d8cfbbe309d2e03e9a301baea056d9718b71b and Harbor 0.24.0. Reuse upstream task generation, telemetry and grading. Reproducibly remove only the MCP capability declaration from generated task metadata; record that difference. Add PostgreSQL with a run-level Compose overlay.
- Test the public adapter seam first in one test file: exact question and window, normal bootstrap/session/Origin, Integration verification, real-result export, failure and timeout cancellation. These fixture tests do not count as live Integration acceptance.
- Run the real Linux backend inside main. Generate per-trial secrets, bootstrap through HTTP, verify native Integrations and query grants, submit a Conversation, collect the actual Conclusion and durable Tool Runs. Never inject grading answers or implement another reasoning loop.
- Provide an ignored editable config and tracked example. Keep secrets out of arguments, logs and artifacts. One model, one attempt, one concurrent trial, no automatic retries. Require actual non-empty native Tool Runs before benchmark acceptance. First run promql-error-rate, then logql-deployment-rollout-events, find-slow-traces and service-degradation-rca. Report unavailable metrics and unsupported tasks honestly. Credentials and working Docker are required for live validation.

Review: independent Standards and Spec reviews found no residual issues after the credential-safe log correction. Scope and seams match the approved proposal; no production changes or new service abstractions were added.

Verification: seven tests in one focused file, Ruff lint/format, mypy, locked dependency checks, source/wheel builds, real Harbor adapter/schema/parser loading, offline Compose merge validation, and the documented preparation command pass. No live telemetry or model run is claimed. Next: fill config.toml, restore Docker/disk space, run smoke, then promql-error-rate and inspect its actual grader report.
