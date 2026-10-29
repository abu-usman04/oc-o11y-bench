# OpenCluster observability benchmark

Run the real OpenCluster Investigation Agent against selected Grafana o11y-bench cases locally.
Harbor manages isolated trials. The upstream benchmark supplies real Prometheus, Loki and Tempo,
the questions, grading and HTML reports. OpenCluster performs all model reasoning and Tool execution.

## Quick Start

Requirements: Git, uv, a working Linux Docker daemon and Docker Compose.
Python 3.14 and project dependencies are installed by the launcher. Keep enough disk space for Docker images.
The production repository is read through Git; its working-directory edits are not included in builds.
Launchers clone upstream with core.autocrlf=false so its Linux shell scripts retain LF line endings.

1. Edit the prepared, Git-ignored `config.toml`:
   - Set `model.name` to an exact model ID and `model.api_key` to its API key.
   - Use `model.provider = "anthropic"` or `"openrouter"`.
   - For scored runs, set `grading.anthropic_api_key`. A blank value reuses the Agent key
     when its provider is Anthropic. The grader is upstream's pinned Anthropic judge.
   - Leave the repository path and commit unchanged to evaluate the reviewed control-plane revision.
2. Prepare and check connectivity, then run one scored case:

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

Each trial runs the clean, pinned Linux control-plane binary inside Harbor's `main` container.
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

Run these only after inspecting the first scored result. Every run stays at one attempt, one concurrent
trial and zero automatic retries. Each job gets a unique directory under `jobs/`.

Useful files:
- `opencluster-result.md`: readable question, Conclusion, Findings, every Tool attempt, timing and usage.
- `opencluster-manifest.json`: code/binary/benchmark identity, model and scenario time.
- `*/agent/integrations.json`: verification and Tool availability.
- `*/agent/investigation.json`: actual public Conclusion, Tool Runs and token totals.
- `*/agent/trajectory.json`: ATIF derived from those public records.
- `*/agent/smoke.json`: unscored connectivity checks and actual Investigations.
- `*/agent/failure.json`, `*/agent/backend.log`: failure details and a bounded, redacted log tail.
- `*/verifier/grading_details.json`, `*/verifier/reward.txt`: upstream grading.
- `run_report.html`: upstream report for a scored job.

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
- Durable Tool Runs do not contain full Tool-result payloads or private model reasoning.
  ATIF explicitly marks that limit and uses synthetic ordinal-based call IDs. It is not a complete
  original model transcript. Input/output token totals are available; cache breakdown and dollar cost are not.
- Loki currently supports bounded log excerpts, not aggregate LogQL result vectors/matrices.
  Exact exhaustive counts/shares may be unsupported. Tempo metrics/tag discovery and native Prometheus
  histogram payloads are outside the shipped Tools. Do not claim full benchmark coverage.
- The ten-minute benchmark limit is retained; OpenCluster can ordinarily run longer.
- Local fixture tests and successful preparation do not prove live Integration compatibility.
  Until `smoke` and a scored run actually finish, live connectivity and grading remain unverified.

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
