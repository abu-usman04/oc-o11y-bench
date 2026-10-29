"""Render public Investigation records without another model or judge."""

import json
from pathlib import Path


def _block(value):
    text = json.dumps(value, ensure_ascii=False, indent=2)
    return "\n".join("    " + line for line in text.splitlines())


def write_report(job_dir: Path, model: str, *, graded: bool, harness_exit_code: int) -> Path:
    lines = [
        "# OpenCluster results",
        "",
        "Grading requested; see upstream verifier artifacts."
        if graded
        else "Ungraded: no benchmark correctness score was requested.",
        "",
        f"Harbor process exit code: {harness_exit_code}",
        "Harness failed; retained Investigation records follow."
        if harness_exit_code
        else "Harness completed. Answer correctness is separate from execution status.",
        "",
        "Model: " + model,
        "",
        "Full Tool-result content is not persisted. This report contains the public "
        "Conclusion and every durable Tool Run; private model reasoning is unavailable.",
    ]
    for logs in sorted(job_dir.glob("*/agent")):
        smoke = logs / "smoke.json"
        investigation = logs / "investigation.json"
        if smoke.exists():
            receipt = json.loads(smoke.read_text(encoding="utf-8"))
            entries = receipt["results"]
            lines.extend(["", "## Connectivity checks", "", _block(receipt["checks"])])
        elif investigation.exists():
            entries = [
                {
                    "question": (logs / "instruction.txt").read_text(encoding="utf-8"),
                    "result": json.loads(investigation.read_text(encoding="utf-8")),
                }
            ]
        else:
            entries = []
        for entry in entries:
            result = entry["result"]
            lines.extend(
                [
                    "",
                    "## Investigation " + result["id"],
                    "",
                    "### Question",
                    "",
                    _block(entry["question"]),
                    "",
                    "### Summary",
                    "",
                    _block(result.get("summary", "")),
                    "",
                    "### Findings",
                    "",
                    _block(result.get("findings", [])),
                    "",
                    "### Conclusion, timing and usage",
                    "",
                    _block(
                        {
                            key: value
                            for key, value in result.items()
                            if key not in ("summary", "findings", "runs")
                        }
                    ),
                ]
            )
            for run in result.get("runs", []):
                lines.extend(["", f"### Tool Run {run['ordinal']}: {run['tool']}", "", _block(run)])
        failure = logs / "failure.json"
        if failure.exists():
            lines.extend(
                [
                    "",
                    "## Execution failure",
                    "",
                    _block(json.loads(failure.read_text(encoding="utf-8"))),
                ]
            )
    path = job_dir / "opencluster-result.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
