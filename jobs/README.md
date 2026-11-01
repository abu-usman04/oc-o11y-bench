# Recorded benchmark jobs

These records are committed for analysis, including unsuccessful and ungraded attempts.
Credentials and local configuration remain excluded.

Start with the [issue #198 validation](issue-198-validation-20261101/report.md):
exact retained observations match capture, but passing rubrics still conceal RCA errors.

The earlier [capability audit](citation-query-audit-20261029/audit.md) and
[HTML dashboard](citation-query-audit-20261029/index.html) remain available.
The audit includes category statistics, criterion verdicts, exact trace examples and corrections.

The October 29 evaluation used z-ai/glm-5.1, one attempt per selected case and the unchanged
30-read limit. Four local upstream rubrics passed. The independent audit found incorrect
sample counts and unsupported causal claims in two answers. This is no official leaderboard
submission or certification of autonomous root-cause investigation.

| Record | What it contains |
|---|---|
| issue-198-validation-20261101/ | November 1 comparison, exact metrics, independent engineering verdicts, binary parity and release verification. |
| citation-query-reruns.json | Exact job names for the four October 29 selected attempts. |
| citation-query-audit-20261029/ | Overall findings, category totals, structured statistics and verification logs. |
| Each case directory | Human-readable result, manifest, saved answer, native Tool observations and endpoint metadata. |
| local-grading/ | Original upstream per-criterion verdicts and canonical truth, when grading was run. |
| grading-context.json | Judge model, route, benchmark identity and local evaluation scope. |
| fact-audit.json | Canonical facts and explicitly labelled independent engineering corrections. |
| Earlier case and smoke directories | Previous outcomes and connectivity checks; their manifests identify code and model. |

A completed run is not proof that its answer is correct. Keep the original answer, evidence
and independent review together. Actual recorded runtime errors and release-gate failures
remain visible in the reports. Do not calculate a global rank from this selected subset.
