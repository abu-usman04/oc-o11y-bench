"""Prepare upstream cases and run pinned Harbor locally."""

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import tomllib
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream" / "o11y-bench"
BENCH_COMMIT = "b66d8cfbbe309d2e03e9a301baea056d9718b71b"
CASES = (
    "promql-error-rate",
    "logql-deployment-rollout-events",
    "find-slow-traces",
    "service-degradation-rca",
)


def prepare_task(upstream, output, name):
    from scripts.sync_tasks import generate_task

    specs = list((upstream / "tasks-spec").rglob(name + ".yaml"))
    if len(specs) != 1:
        raise ValueError("case must identify exactly one upstream task")
    output.mkdir(parents=True, exist_ok=True)
    generate_task(specs[0], output)
    task = output / name
    path = task / "task.toml"
    original = path.read_text()
    expected = tomllib.loads(original)
    expected["environment"].pop("mcp_servers")
    native = original.split("[[environment.mcp_servers]]", 1)[0].rstrip() + "\n"
    if tomllib.loads(native) != expected:
        raise RuntimeError("task preparation would change more than the MCP declaration")
    path.write_text(native)
    return task


def command(args, *, cwd=ROOT, env=None, timeout=None):
    return subprocess.run(args, cwd=cwd, env=env, check=True, timeout=timeout)


def git_value(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def build_binary(repo, commit):
    binary = ROOT / ".work" / "bin" / commit / "controlplane"
    if binary.exists():
        return binary
    binary.parent.mkdir(parents=True, exist_ok=True)
    image = "oc-o11y-bench-controlplane:" + commit
    archive = subprocess.Popen(["git", "-C", str(repo), "archive", commit], stdout=subprocess.PIPE)
    try:
        subprocess.run(
            [
                "docker",
                "build",
                "--target",
                "build",
                "-t",
                image,
                "-f",
                "deploy/compose/Dockerfile",
                "-",
            ],
            stdin=archive.stdout,
            check=True,
        )
    finally:
        if archive.stdout:
            archive.stdout.close()
        if archive.wait() != 0:
            raise RuntimeError("could not archive the pinned control-plane commit")
    container = subprocess.check_output(["docker", "create", image], text=True).strip()
    try:
        command(["docker", "cp", container + ":/out/controlplane", str(binary)])
    finally:
        command(["docker", "rm", container])
    return binary


def build_stack():
    # Do not invoke upstream's process-wide cleanup script on the user's host.
    for tag, directory in (
        ("o11y-bench-main:latest", "environment"),
        ("o11y-bench-o11y-stack:latest", "docker"),
    ):
        command(
            [
                "docker",
                "build",
                "--label",
                "oc.benchmark.commit=" + BENCH_COMMIT,
                "-t",
                tag,
                str(UPSTREAM / directory),
            ]
        )
    inspected = subprocess.run(
        ["docker", "network", "inspect", "o11y-bench-shared"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if inspected.returncode:
        command(["docker", "network", "create", "o11y-bench-shared"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=("prepare", "smoke", *CASES))
    parser.add_argument("--config", type=Path, default=ROOT / "config.toml")
    args = parser.parse_args()
    if git_value(UPSTREAM, "rev-parse", "HEAD") != BENCH_COMMIT:
        raise ValueError("upstream checkout must match the pinned benchmark commit")
    if git_value(UPSTREAM, "status", "--porcelain"):
        raise ValueError("upstream checkout must be clean")
    tasks = ROOT / ".work" / "tasks"
    selected = (
        CASES
        if args.case == "prepare"
        else ("promql-error-rate" if args.case == "smoke" else args.case,)
    )
    for case in selected:
        prepare_task(UPSTREAM, tasks, case)
    if args.case == "prepare":
        print("Prepared four upstream cases; only their MCP declarations were omitted.")
        return
    with args.config.open("rb") as source:
        config = tomllib.load(source)
    model = config["model"]
    provider, name, key = (
        model.get(field, "").strip() for field in ("provider", "name", "api_key")
    )
    if provider not in ("anthropic", "openrouter") or not name or not key:
        raise ValueError("fill model.provider, model.name and model.api_key in config.toml")
    grading_key = config.get("grading", {}).get("anthropic_api_key", "").strip()
    if not grading_key and provider == "anthropic":
        grading_key = key
    if args.case != "smoke" and not grading_key:
        raise ValueError("fill grading.anthropic_api_key for a scored run")
    run = config["run"]
    commit = run["controlplane_commit"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("controlplane_commit must be a full Git commit SHA")
    repo = (args.config.resolve().parent / run["controlplane_repo"]).resolve()
    if git_value(repo, "rev-parse", commit + "^{commit}") != commit:
        raise ValueError("the pinned control-plane commit must exist locally")
    scenario = (
        run.get("scenario_time", "") or (datetime.now(UTC) - timedelta(seconds=5)).isoformat()
    )
    end = datetime.fromisoformat(scenario.replace("Z", "+00:00"))
    if end.tzinfo is None or end > datetime.now(UTC):
        raise ValueError("scenario_time must include an offset and must not be in the future")
    try:
        subprocess.run(
            ["docker", "info"],
            check=True,
            timeout=15,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.SubprocessError, OSError) as error:
        raise RuntimeError("Docker is not ready; start a working Linux Docker daemon") from error
    binary = build_binary(repo, commit)
    binary_hash = hashlib.sha256(binary.read_bytes()).hexdigest()
    gate_path = ROOT / ".work" / "connectivity.json"
    identity = {
        "controlplaneCommit": commit,
        "binarySHA256": binary_hash,
        "benchmarkCommit": BENCH_COMMIT,
        "provider": provider,
        "model": name,
    }
    if args.case != "smoke":
        gate = json.loads(gate_path.read_text()) if gate_path.exists() else {}
        if gate.get("identity") != identity:
            raise ValueError("run ./run.sh smoke successfully with this code/model before scoring")
    build_stack()
    job_name = (
        args.case + "-" + datetime.now(UTC).strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(3)
    )
    private = ROOT / ".work" / "secrets" / job_name
    private.mkdir(parents=True, mode=0o700)
    model_file, postgres_file = private / "model-key", private / "postgres-password"
    for path, value in ((model_file, key), (postgres_file, secrets.token_urlsafe(32))):
        path.write_text(value)
        path.chmod(0o600)
    env = os.environ.copy()
    env.update(
        {
            "OC_BENCH_BINARY": binary.as_posix(),
            "OC_BENCH_RUNTIME": (ROOT / "opencluster_bench" / "runtime.py").as_posix(),
            "OC_BENCH_MODEL_KEY": model_file.as_posix(),
            "OC_BENCH_PG_PASSWORD": postgres_file.as_posix(),
            "OC_BENCH_MODEL": name,
            "OC_BENCH_PROVIDER": provider,
            "OC_BENCH_COMMIT": commit,
            "OC_BENCH_SMOKE": "1" if args.case == "smoke" else "0",
            "OC_BENCH_WINDOW_HOURS": "1" if args.case == "promql-error-rate" else "24",
            "O11Y_SCENARIO_TIME_ISO": end.astimezone(UTC).isoformat(),
            "ANTHROPIC_API_KEY": grading_key,
        }
    )
    manifest = {
        **identity,
        "scenarioTime": env["O11Y_SCENARIO_TIME_ISO"],
        "case": args.case,
        "attempts": 1,
        "concurrentTrials": 1,
        "harborVersion": "0.24.0",
        "omittedTaskMetadata": ["environment.mcp_servers"],
    }
    job_dir = ROOT / "jobs" / job_name
    argv = [
        "harbor",
        "run",
        "--yes",
        "--path",
        str(tasks),
        "--include-task-name",
        selected[0],
        "--jobs-dir",
        str(ROOT / "jobs"),
        "--job-name",
        job_name,
        "--agent",
        "opencluster_bench.agent:OpenClusterAgent",
        "--model",
        provider + "/" + name,
        "--n-attempts",
        "1",
        "--n-concurrent",
        "1",
        "--max-retries",
        "0",
        "--extra-docker-compose",
        str(ROOT / "environment" / "compose.override.yaml"),
    ]
    if args.case == "smoke":
        argv.append("--disable-verification")
    try:
        completed = subprocess.run(argv, cwd=ROOT, env=env)
        job_dir.mkdir(parents=True, exist_ok=True)
        (job_dir / "opencluster-manifest.json").write_text(json.dumps(manifest, indent=2))
        if completed.returncode:
            raise RuntimeError("Harbor did not complete; inspect this job's artifacts")
        if args.case == "smoke":
            receipts = list(job_dir.glob("*/agent/smoke.json"))
            if len(receipts) != 1 or not json.loads(receipts[0].read_text()).get("passed"):
                raise RuntimeError("native Integration connectivity has not passed")
            gate_path.write_text(json.dumps({"identity": identity, "job": job_name}, indent=2))
            print("Live native Integration connectivity passed; this run was not scored.")
        else:
            command(
                [
                    sys.executable,
                    "-m",
                    "o11y_bench",
                    "finalize",
                    "--jobs-dir",
                    str(ROOT / "jobs"),
                    "--job-name",
                    job_name,
                    "--path",
                    str(tasks),
                ],
                cwd=UPSTREAM,
                env=env,
            )
        print("Artifacts: " + str(job_dir))
    finally:
        model_file.unlink(missing_ok=True)
        postgres_file.unlink(missing_ok=True)
        private.rmdir()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from None
