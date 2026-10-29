# Agent citation and query-quality fixes

Status: authorized by the user on 2026-10-29; review before implementation.

## Critique

The previous run proved recording fidelity, not Agent correctness. Prometheus failed conclusion citation validation. Cross-source exhausted thirty reads, repeated guessed labels and invalid syntax, received two clipped observations, and overstated an internal mechanism. More reads, a looser validator or benchmark-specific answers would hide these problems.

The smallest useful change is to constrain unavailable citation choices, explain corrections clearly, and improve general query guidance and budget visibility. Keep the existing Agent loop, provider SDKs, data-access boundaries and security behavior. Do not introduce a planner framework, query-rewriting engine, response cache or automatic causal judge inside production.

## Implementation

1. Work from the previously evaluated production commit f3f0e700 in an isolated worktree, preserving the user's refactoring checkout. The benchmark workspace stays D:/Development/oc-o11y-bench. Store this plan here, not in production docs.
2. At the existing Agent.Run/provider seam, write a failing regression for unsupported prior citations. When no prior evidence has actually been supplied, constrain evidence_refs to an empty array; current reads remain run_refs. Preserve legitimate historical citations and all backend validation. Give precise repair feedback without silently dropping or rewriting citations.
3. Add general investigation guidance: discover actual service/status labels, recover from empty reads by checking labels, use compact rankings before broad range reads, focus windows and filters, and treat clipped data as partial. Show remaining reads each model turn. Keep the default thirty-read limit, turn/deadline limits and model unchanged. Use the existing tool descriptions for correct LogQL alternatives and TraceQL duration syntax. Keep pool/lock mechanisms as hypotheses unless directly established.
4. Add minimal regressions at the existing Agent.Run and provider/HTTP seams, plus existing tool tests only if a tool description changes observable behavior. Run focused tests and the production make verify gates. Commit the production fix separately and pin the benchmark to that commit; identify both production and recorder hashes.
5. Run smoke, then the four original cases once each with z-ai/glm-5.1 and thirty reads. Preserve questions, original benchmark data and rubric, real Tool observations, endpoints and all failures. Do not retry failures to improve the score.
6. Grade the same saved answers using the original upstream checks, truth queries, rubric and judge when the required credential is available. The user selected OpenRouter-routed grading with the existing key, and category statistics. Keep the original Anthropic SDK, judge family, rubric and aggregation; record the OpenRouter model alias and route. Do not represent a different judge or gateway configuration as an official leaderboard submission. Keep execution, scoring infrastructure errors, rubric verdicts and engineering causality review separate.
7. Produce a concise capability/run/benchmark audit with a leaderboard-style summary and one row per case: attempts, native outcome, judge pass/fail or unavailable, solved count for the selected four, token usage, available cost, correctness evidence, unsupported claims, and remaining defects. Pass-cubed and Pass-at-three are unavailable for a one-attempt selection; global ranking is not established. Inventory all original task categories against shipped Tool capabilities to explain what remains unsupported without claiming unrun tasks passed or failed.
8. Review standards and spec independently, fix justified findings, complete focused checks, and remove temporary containers and credentials. Do not merge or publish a PR or leaderboard submission.

## Acceptance

The actual no-history citation failure has a regression and invalid references remain rejected. Valid prior references still work. Budget visibility and query guidance are general, with no benchmark answers or increased limits. All four cases are attempted and all evidence is retained. The audit states exactly which conclusions are supported, contradicted or unproven, which checks passed, and which scoring/ranking metrics are unavailable. A benchmark pass does not certify every causal sentence or all product capabilities.

## Expected files

Production changes remain in internal/investigation/agent/prompt.go, run.go, conclusion.go and existing Agent tests; provider-specific guidance stays in the existing Prometheus/Loki/Tempo tool definitions if needed. No new production packages or dependencies. Benchmark changes are limited to its commit pin, scoring invocation if needed and the audit report. Plans stay under plans/ in the benchmark workspace; generated results stay under jobs/.
