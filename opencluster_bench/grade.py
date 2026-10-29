"""Score saved answers with the pinned upstream judge through OpenRouter."""

import argparse
import json
import os
import tomllib
from dataclasses import asdict
from pathlib import Path

from opencluster_bench.__main__ import BENCH_COMMIT, ROOT
from opencluster_bench.report import write_report


def configure_judge(config):
    model = config["model"]
    if model.get("provider") != "openrouter" or not model.get("api_key", "").strip():
        raise ValueError("OpenRouter grading requires the configured OpenRouter Agent key")
    name = "anthropic/claude-haiku-5.5@high"
    os.environ.update(
        {
            "ANTHROPIC_API_KEY": "",
            "ANTHROPIC_AUTH_TOKEN": model["api_key"],
            "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
        }
    )
    return name, {
        "route": "OpenRouter Anthropic Messages compatibility endpoint",
        "endpoint": "https://openrouter.ai/api/v1/messages",
        "model": name,
        "upstreamDefault": "claude-haiku-5-5@high",
        "scope": "Local selected-case evaluation; no official leaderboard submission",
    }


def update_report(job, manifest, facts, checks):
    path = job / "fact-audit.json"
    audit = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    audit.update(
        {
            "mode": "Canonical facts and checks from local upstream grading",
            "facts": facts,
            "checks": {
                "scores": {item.name: item.score for item in checks},
                "explanations": {item.name: item.explanation for item in checks},
            },
        }
    )
    path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(
        job,
        manifest["provider"] + "/" + manifest["model"],
        graded=False,
        harness_exit_code=manifest.get("harnessExitCode"),
    )


def main():
    import yaml
    from grading.facts import resolve_fact
    from grading.models import Problem
    from grading.transcript_parser import parse_transcript
    from grading.verifier import grade, write_outputs
    from o11y_bench.regrade_stack import running_regrade_stack

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jobs", nargs="+", type=Path)
    parser.add_argument("--config", type=Path, default=ROOT / "config.toml")
    args = parser.parse_args()
    with args.config.open("rb") as source:
        model, context = configure_judge(tomllib.load(source))
    for path in args.jobs:
        job = path.resolve()
        if not job.is_relative_to(ROOT / "jobs"):
            raise ValueError("job must be under this workspace's jobs directory")
        manifest = json.loads((job / "opencluster-manifest.json").read_text(encoding="utf-8"))
        if manifest["benchmarkCommit"] != BENCH_COMMIT:
            raise ValueError("job must use the pinned benchmark")
        (logs,) = job.glob("*/agent")
        capture = json.loads((logs / "artifacts/tool-results.json").read_text(encoding="utf-8"))
        if not capture.get("complete"):
            raise ValueError("incomplete evidence capture; inspect artifacts before grading")
        task = ROOT / ".work/tasks" / manifest["case"]
        problem = Problem(
            **yaml.safe_load((task / "tests/problem.yaml").read_text(encoding="utf-8"))
        )
        transcript = parse_transcript(logs)
        os.environ["O11Y_SCENARIO_TIME_ISO"] = manifest["scenarioTime"]
        os.environ["O11Y_STACK_GOMAXPROCS"] = "2"
        print("GRADING", job.name, flush=True)
        with running_regrade_stack(
            task_dir=task,
            trial_dir=job / "grading-replay",
            scenario_time_iso=manifest["scenarioTime"],
        ) as ctx:
            result = grade(problem, transcript, model, ctx=ctx)
            facts = []
            for criterion in problem.rubric:
                if criterion.fact is None:
                    continue
                fact = resolve_fact(
                    criterion.fact,
                    ctx,
                    result.truth,
                    answer=transcript.final_answer(),
                    example=problem.trace_example,
                )
                facts.append({"criterion": criterion.criterion, "evidence": asdict(fact)})
        write_outputs(job / "local-grading", result)
        (job / "grading-context.json").write_text(
            json.dumps(
                {
                    **context,
                    "benchmarkCommit": BENCH_COMMIT,
                    "scenarioTime": manifest["scenarioTime"],
                    "answerSource": str(logs.relative_to(job) / "trajectory.json"),
                    "agentRerun": False,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        update_report(job, manifest, facts, result.checks)
        print("VERDICT", manifest["case"], result.status, result.score, flush=True)


if __name__ == "__main__":
    main()
