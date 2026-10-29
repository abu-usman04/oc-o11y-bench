# OpenCluster o11y-bench

Test the real OpenCluster Agent against Grafana o11y-bench using Prometheus, Loki and Tempo.

Requirements: Git, [uv](https://docs.astral.sh/uv/getting-started/installation/),
and Docker with Compose and Linux containers running.

## Setup

Clone both repositories into the same parent folder:

```sh
git clone https://github.com/open-cluster/oc-control-plane.git
git clone https://github.com/abu-usman04/oc-o11y-bench.git
cd oc-o11y-bench
cp config.example.toml config.toml
```

Edit `config.toml`:

- `model.provider`: `openrouter` or `anthropic`.
- `model.name`: the model ID, such as `z-ai/glm-5.1` for OpenRouter.
- `model.api_key`: your provider key.
- `run.controlplane_repo` and `run.controlplane_commit`: your checkout path and full
  commit SHA. The defaults work with the sibling clone above.

The launchers install Python 3.14 and dependencies. `config.toml` stays out of Git.
Runs and grading consume API credits.

## Run

On Windows, use PowerShell:

```powershell
.\run.ps1 prepare
.\run.ps1 smoke
.\run.ps1 promql-error-rate --no-grade
```

On Linux/macOS, use `bash run.sh` instead of `.\run.ps1`.
Run `smoke` again after changing the model or control-plane revision.

Other cases: `logql-deployment-rollout-events`, `find-slow-traces`,
and `service-degradation-rca`.

To grade a saved OpenRouter run using the same key, replace `JOB_NAME`:

```sh
uv run --locked python -m opencluster_bench.grade jobs/JOB_NAME
```

For direct Anthropic grading, omit `--no-grade` when running a case.
Set `grading.anthropic_api_key` only if the grader needs a different key.

## Results

Open `jobs/JOB_NAME/opencluster-result.md` for the answer, findings and Tool calls.
The job also retains JSON observations, endpoint details, logs and grading results.
See [recorded runs and audits](jobs/README.md) for existing analyses.

Jobs are committed for analysis; keep credentials out of them.
These local results do not establish an official leaderboard ranking.
