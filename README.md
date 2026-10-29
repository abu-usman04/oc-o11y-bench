# OpenCluster observability benchmark

Run the real OpenCluster Investigation Agent against selected Grafana o11y-bench cases locally.
Harbor manages isolated trials. The upstream benchmark supplies real Prometheus, Loki and Tempo,
the questions, grading and HTML reports. OpenCluster performs all model reasoning and Tool execution.

## Quick Start

Requirements: Git, uv, a working Linux Docker daemon and Docker Compose.
Python 3.14 and project dependencies are installed by the launcher. Keep enough disk space for Docker images.
The production repository is read through Git; its working-directory edits are not included in builds.
Launchers clone upstream with core.autocrlf=false so its Linux shell scripts retain LF line endings.
The harness uses UTF-8 mode so Unicode Findings and traces work on Windows.

1. Edit the prepared, Git-ignored `config.toml`:
   - Set `model.name` to an exact model ID and `model.api_key` to its API key.
   - Use `model.provider = "anthropic"` or `"openrouter"`.
   - For scored runs, set `grading.anthropic_api_key`. A blank value reuses the Agent key
     when its provider is Anthropic. The grader is upstream's pinned Anthropic judge.
   - Leave the repository path and commit unchanged to evaluate the reviewed control-plane revision.
2. Prepare and check connectivity, then run one case:

```powershell
.\run.ps1 prepare
.\run.ps1 smoke
.\run.ps1 promql-error-rate --no-grade
```

On Linux or WSL, use `bash run.sh` with the same arguments.
Use one platform's virtual environment at a time. Launchers keep new uv/Python/temp caches in `.work/`.

`prepare` generates four cases without Docker or API calls.
`smoke` starts disposable local containers and runs three real Investigations, requiring non-empty
Prometheus metrics, Loki excerpts, Tempo search results and a retrieved trace with spans.
It is unscored and does not need a grader key.
A case run requires a successful smoke receipt for the same binary, benchmark and configured model.

Use --no-grade to run the original case using only the Agent API key. It preserves the real question,
Investigation, Findings, Tool Runs and ATIF, and skips the judge and correctness score. Omit --no-grade
when you want upstream scoring and have supplied its Anthropic key.

One trial is one attempt, not one model call. Set account spending limits before running;
connectivity checks and rubric grading also consume model usage. No Grafana Cloud or Harbor Cloud key is needed.

## Architecture

```text
Harbor -> thin adapter -> local OpenCluster HTTP API -> real Investigation Agent
                                                    -> native Prometheus/Loki/Tempo Integrations
       -> unchanged upstream verifier -> grading artifacts and HTML report
```

Each trial builds the pinned control-plane source with a benchmark-only entry point inside Harbor's `main` container.
It wraps the existing real provider interface to retain bounded Tool observations and records read-only HTTP
metadata. Agent logic, provider policy and the default 30-read budget stay unchanged. The manifest records
the production commit, instrumentation hash and resulting binary hash.
PostgreSQL has a private network and disposable memory-backed storage. The upstream telemetry sidecar
and its task-specific data remain unchanged. No application ports are published.

The adapter bootstraps a local administrator through the normal API and uses its session cookie and Origin.
It creates and verifies Integrations, checks their query availability, and submits a Conversation
with the exact benchmark question and an explicit scenario-time window. It never seeds application SQL.

## Usage and Results

```powershell
.\run.ps1 logql-deployment-rollout-events --no-grade
.\run.ps1 find-slow-traces --no-grade
.\run.ps1 service-degradation-rca --no-grade
```

Inspect each result before expanding to more cases. Every run stays at one attempt, one concurrent
trial and zero automatic retries. Each job gets a unique directory under `jobs/`.

Useful files:
- `opencluster-result.md`: readable answer, trace examples, cited Findings, uncertainty, Tool table and endpoint details.
  Execution status, independent facts and any judge verdict are stated separately.
- `opencluster-manifest.json`: code/binary/instrumentation identity, model, scenario time and unchanged read budget.
- `*/agent/trajectory.json`: the only root JSON transcript; unchanged upstream grading can parse this directory.
- `*/agent/artifacts/investigation.json`: public response from `GET /api/v1/investigations/{id}`.
- `*/agent/artifacts/integrations.json`: real Integration verification responses and query availability.
- `*/agent/artifacts/tool-results.json`: actual bounded observations supplied to the provider, real call IDs,
  associated HTTP method/source/path/parameters/status and precise request timestamps. Ambiguity is explicit.
- `*/agent/artifacts/capture.jsonl`: redacted recorder output; `backend.log` is the application's own log.
- `*/agent/artifacts/smoke.json`, `failure.json`: connectivity records or failure details.
- `fact-audit.json`, when present: canonical facts and deterministic checks, without an LLM judge verdict.
- `*/verifier/grading_details.json`, `reward.txt`, `truth.json`: unchanged upstream grading, only for scored runs.
- `run_report.html`: upstream report for a scored job.

Diagnostic JSON lives under `artifacts/` because the upstream parser treats every root JSON file as a transcript.
Trace examples list IDs stated in the answer; the report never invents an example from search results.
An instant Prometheus evaluation can legitimately have equal bounds while `[60m]` reads the preceding hour.
Public Tool execution timestamps have second precision. HTTP timestamps retain subsecond precision and measure
request-to-response-headers time, not complete Tool execution.
Reports name captured trace operations beside IDs and show HTTP timing directly. They also distinguish source
limits from the Agent's pre-existing 16 KiB model-observation cuts; a complete recording can faithfully contain
a cut observation. Failed Investigations expose their actual error separately from Harbor's process exit code.

Docker readiness is checked before any build. Application execution has a bounded deadline;
unfinished Investigations are cancelled, and failures are reported rather than converted into answers.
A completed Investigation can still receive a low score: execution success and answer correctness differ.
Ungraded reports explicitly show that no correctness score was requested. The JSON/ATIF records
retain Tool arguments, outcomes, errors, truncation, source references and timestamps.

## Reproducibility and Limits

- Benchmark: `grafana/o11y-bench@b66d8cfbbe309d2e03e9a301baea056d9718b71b`.
- Harbor: `0.24.0`; Python dependencies are locked in `uv.lock`.
- Control plane: full commit SHA in `config.toml`; a Git archive excludes uncommitted edits.
- A blank scenario time chooses just before the run. The resolved UTC time is recorded.
  A configured time must have an offset and cannot be in the future.
- Task generation uses upstream's generator. A checked, reproducible metadata adjustment omits only
  `environment.mcp_servers`, because this adapter uses native Integrations. Instructions, setup,
  sidecar Compose and grading code are preserved. There is no MCP replacement.
- Upstream's broad stale-project cleanup script is not run. Harbor deletes its own trial containers.
- Public Tool Runs still contain summaries. The external recorder additionally retains the exact bounded
  Tool observations submitted to the real provider adapter, not unlimited vendor responses or private reasoning.
  Captures are limited to 128 KiB per record and 8 MiB per run; overflow or missing evidence fails capture acceptance
  without changing the provider input. Headers and model messages are excluded; known secrets are redacted.
  ATIF remains reconstructed, with real call IDs and observations when captured. Input/output totals are available;
  cache breakdown and dollar cost are not.
- Loki currently supports bounded log excerpts, not aggregate LogQL result vectors/matrices.
  Exact exhaustive counts/shares may be unsupported. Tempo metrics/tag discovery and native Prometheus
  histogram payloads are outside the shipped Tools. Do not claim full benchmark coverage.
- The ten-minute benchmark limit is retained; OpenCluster can ordinarily run longer.
- Fixture tests do not prove live connectivity or answer correctness. Smoke verifies native connectivity;
  canonical facts and deterministic checks verify specific claims. Only upstream grading supplies benchmark verdicts.
  Selected ungraded cases cannot produce a full-suite Pass³ or Pass@3 score. Some benchmark tasks need capabilities
  the current read-only Tools do not offer.

## Contributing

Keep benchmark code here, outside the production repository. Use one focused test file:

```powershell
uv run --locked python -m unittest discover -s tests -v
uv run --locked ruff check opencluster_bench tests
uv run --locked ruff format --check opencluster_bench tests
uv run --locked mypy opencluster_bench
```

Keep completed config files, secrets, generated tasks, binaries and results out of Git.
Provider credentials are mounted as files; temporary database credentials are removed after the job.
Bootstrap credentials and sealing keys are generated per trial. Report genuine product defects
with a reproducer before proposing production changes.
