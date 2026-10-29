"""Readable benchmark answers, evidence and execution diagnostics; no generated verdicts."""

import json
import re
from datetime import datetime
from html import escape
from pathlib import Path


def _block(value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    return "\n".join("    " + line for line in text.splitlines())


def _cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def _read(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _outcome(run):
    if run["outcome"] != "succeeded":
        return "failed / not executed" if "not executed" in run.get("error", "") else "failed"
    if re.search(r"empty:|: 0 (series|names|log excerpts|traces)", run.get("summary", "")):
        return "succeeded, empty"
    return "succeeded, limited" if run.get("truncated") else "succeeded"


def _investigation(lines, question, result, artifacts, capture, audit_lines, public_file):
    runs = result.get("runs", [])
    observations = {
        entry["ordinal"]: entry
        for entry in capture.get("toolResults", [])
        if entry["investigationId"] == result["id"]
    }
    clipped = {
        ordinal
        for ordinal, entry in observations.items()
        if re.search(r"\[cut at \d+ bytes\]$", entry.get("content", ""))
    }
    trace_details = {}
    for ordinal, entry in observations.items():
        try:
            payload = json.loads(entry.get("content", "").partition("\nCONTENT: ")[2])
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict) or not payload.get("traceId"):
            continue
        root = next((span for span in payload.get("spans", []) if not span.get("parentId")), None)
        if root:
            trace_details[payload["traceId"]] = (
                f"{root['operation']} - {root['durationNanos'] / 1e9:.3f} s "
                f"(root service {root['service']}; Tool Run #{ordinal})"
            )
    failed = sum(run["outcome"] != "succeeded" for run in runs)
    limited = sum(bool(run.get("truncated")) for run in runs)
    seen: dict[str, int] = {}
    duplicate_ordinals = []
    for run in runs:
        identity = json.dumps(
            [run.get("integrationId"), run["tool"], run.get("arguments", {})], sort_keys=True
        )
        if identity in seen:
            duplicate_ordinals.append(f"#{run['ordinal']} repeats #{seen[identity]}")
        else:
            seen[identity] = run["ordinal"]
    usage = result.get("usage", {})
    elapsed = result.get("adapterElapsedSeconds")
    lines.extend(
        [
            "",
            "## Answer",
            "",
            "\n".join(
                "> " + line
                for line in escape(
                    result.get("summary") or "No answer was produced.", quote=False
                ).splitlines()
            ),
            "",
            "### Question",
            "",
            _block(question),
            "",
            f"Investigation: **{result['status']}**; Agent-claimed assessment: "
            f"**{result.get('conclusionStatus', 'unavailable')}**.",
            f"Tool attempts: **{len(runs)}**, including **{failed} failed/blocked** "
            f"and **{limited} limited**.",
            "Read budget: **30** (unchanged); stopped by: **"
            + result.get(
                "stoppedBy",
                "Agent conclusion" if result["status"] == "concluded" else "unavailable",
            )
            + "**.",
            f"Tokens: {usage.get('inputTokens', 'unavailable')} input / "
            f"{usage.get('outputTokens', 'unavailable')} output.",
            f"Agent elapsed: {elapsed:.1f} seconds."
            if elapsed is not None
            else "Agent elapsed: unavailable.",
            "Exact repeated requests: " + ("; ".join(duplicate_ordinals) or "none") + ".",
            "Model-observation clipping: "
            + (
                ", ".join(f"#{n}" for n in sorted(clipped))
                + ". These observations were cut by the Agent before provider submission; "
                "capture preserves that exact bounded input."
                if clipped
                else "none detected."
            ),
        ]
    )
    if result.get("error"):
        lines.extend(["", "**Investigation failure:**", "", _block(result["error"])])
    lines.extend(["", "### Trace examples in the answer", ""])
    answer_text = (
        (result.get("summary") or "")
        + "\n"
        + "\n".join(finding["statement"] for finding in result.get("findings") or [])
    )
    trace_ids = list(dict.fromkeys(re.findall(r"\b[0-9a-fA-F]{32}\b", answer_text)))
    if trace_ids:
        for identifier in trace_ids:
            detail = trace_details.get(identifier)
            lines.append("- `" + identifier + "`" + (" - " + detail if detail else ""))
        lines.append(
            "These IDs were stated by the Agent; IDs appearing only in Tool search output "
            "are not added here."
        )
    elif re.search(r"trace\s*id", question, re.I):
        lines.append("**No trace ID was included in the Agent answer despite the request.**")
    else:
        lines.append("No trace example was stated or requested.")
    lines.extend(audit_lines)
    lines.extend(["", "### Findings and uncertainty", ""])
    for finding in result.get("findings") or []:
        refs = ", ".join(f"[#{n}](#run-{result['id']}-{n})" for n in finding.get("runRefs", []))
        lines.append(
            f"- **{finding.get('kind', 'observation')}**: {finding['statement']} "
            f"({refs or 'no cited reads'})"
        )
    for limitation in result.get("limitations") or []:
        lines.append("- **Limitation**: " + limitation["statement"])
    for hypothesis in result.get("hypotheses") or []:
        lines.append(
            f"- **Hypothesis ({hypothesis.get('status', 'unresolved')})**: "
            f"{hypothesis['statement']}"
        )
    for action in result.get("actions") or []:
        lines.append(f"- **Next diagnostic step**: {action['title']}. {action['verification']}")
    lines.extend(
        [
            "",
            "### Tool attempts",
            "",
            "| Run | Tool | Outcome | Purpose |",
            "| --- | --- | --- | --- |",
        ]
    )
    for run in runs:
        n = run["ordinal"]
        outcome = _outcome(run) + ("; model observation clipped" if n in clipped else "")
        lines.append(
            f"| [#{n}](#run-{result['id']}-{n}) | {_cell(run['tool'])} | {outcome} | "
            f"{_cell(run.get('purpose', ''))} |"
        )
    lines.extend(
        [
            "",
            "### Where these files came from",
            "",
            f"Control-plane endpoint: `GET /api/v1/investigations/{result['id']}` "
            "supplies the public Conclusion and Tool Run records.",
            "`adapterElapsedSeconds` is added by this benchmark adapter. "
            "It is not backend telemetry.",
            "Integration configuration comes from `POST /api/v1/integrations/{id}/verify`.",
            "`backend.log` is the OpenCluster process log, not queried Loki log data.",
            "`trajectory.json` is reconstructed ATIF; it contains the Agent's recorded answer "
            "and observations, not private reasoning.",
            f"[Public result]({(artifacts / public_file).as_posix()}) · "
            f"[Actual Tool observations and HTTP metadata]"
            f"({(artifacts / 'tool-results.json').as_posix()}) · "
            f"[Application log]({(artifacts / 'backend.log').as_posix()})",
            "",
            "An instant Prometheus read has one evaluation timestamp. A selector such as `[60m]` "
            "reads the preceding hour; equal evaluation bounds do not mean an empty lookback.",
            "Public execution timestamps are rounded to seconds by the pinned API. Equal "
            "start/finish values do not prove zero duration. Captured HTTP timestamps retain "
            "subsecond precision; their elapsed interval measures time to response headers.",
        ]
    )
    for run in runs:
        n = run["ordinal"]
        observation = observations.get(n)
        lines.extend(
            [
                "",
                f'<a id="run-{result["id"]}-{n}"></a>',
                f"### Tool Run {n}",
                "",
                f"**{run['tool']}** — {run.get('purpose', '')}",
            ]
        )
        if run.get("windowFrom"):
            label = (
                "Evaluation at"
                if run.get("arguments", {}).get("mode") == "instant"
                else "Read window"
            )
            lines.append(
                f"{label}: {run['windowFrom']}"
                + (
                    ""
                    if label == "Evaluation at"
                    else " to " + run.get("windowUntil", "unavailable")
                )
            )
        lines.extend(["", "Arguments:", "", _block(run.get("arguments", {})), ""])
        lines.append(run.get("error") or run.get("summary") or "No result summary.")
        if run.get("sources"):
            labels = []
            for reference in run["sources"][:3]:
                parts = reference.split(":", 3)
                resource = parts[2] if len(parts) > 2 else "result"
                label = parts[0].title() + " " + resource
                if len(parts) == 4:
                    label += " `" + parts[3] + "`"
                labels.append(label)
            lines.append("Sources: " + "; ".join(labels) + ".")
            if len(run["sources"]) > 3:
                lines.append(
                    f"Plus {len(run['sources']) - 3} other sources. "
                    "Full stable references are in the public result."
                )
        if not observation:
            lines.append(
                "**Actual observation unavailable.** This attempt cannot be audited "
                "from its summary alone."
            )
            continue
        for request in observation.get("requests", []):
            lines.extend(
                [
                    "",
                    f"Endpoint: **{request['method']} {request['path']}** "
                    f"- HTTP {request.get('status', 'unavailable')}.",
                ]
            )
            if request.get("origin"):
                lines.append("Configured source: `" + request["origin"] + "`.")
            if request.get("startedAt") and request.get("headersAt"):
                started = datetime.fromisoformat(request["startedAt"].replace("Z", "+00:00"))
                headers = datetime.fromisoformat(request["headersAt"].replace("Z", "+00:00"))
                duration = (headers - started).total_seconds() * 1000
                lines.append(
                    f"HTTP timing: {request['startedAt']} to {request['headersAt']}; "
                    f"{duration:.3f} ms to response headers."
                )
            lines.extend(
                ["", "Actual request parameters:", "", _block(request.get("parameters", {}))]
            )
        if not observation.get("requests"):
            lines.append(
                "Endpoint association: " + observation.get("requestStatus", "unavailable") + "."
            )
        content = observation.get("content", "")
        if n in clipped:
            lines.append(
                "**Model observation clipped before provider submission.** "
                "This is separate from source limits and recording completeness."
            )
        lines.extend(
            [
                "",
                "Actual observation submitted to the provider adapter:",
                "",
                _block(content[:1800]),
            ]
        )
        if len(content) > 1800:
            lines.append(
                "Display excerpt only; the complete bounded observation "
                "is retained in tool-results.json."
            )


def write_report(job_dir: Path, model: str, *, graded: bool, harness_exit_code: int) -> Path:
    trial_stats = _read(job_dir / "result.json", {}).get("stats", {})
    lines = [
        "# OpenCluster benchmark assessment",
        "",
        "Model: " + model,
        "",
        "Grading requested; see unchanged upstream verifier artifacts."
        if graded
        else "**Ungraded: no LLM judge verdict or benchmark pass score.**",
        f"Harbor process exit code: {harness_exit_code}",
        f"Harbor trial errors: {trial_stats.get('n_errored_trials', 'unavailable')}",
        "Execution completion, answer correctness and benchmark grading are separate outcomes.",
    ]
    audit = _read(job_dir / "fact-audit.json", {})
    audit_lines = []
    if audit:
        audit_lines.extend(
            [
                "",
                "## Independent checks",
                "",
                "Canonical facts were read from the original benchmark stack at this run's "
                "scenario clock. They are independent evidence, not a judge verdict.",
            ]
        )
        for name, score in audit.get("checks", {}).get("scores", {}).items():
            audit_lines.append(
                f"- Deterministic check: **{'passed' if score == 1 else 'failed'}** — {name}."
            )
        for note in audit.get("engineeringReview", []):
            audit_lines.append("- **Engineering review (not an upstream judge verdict)**: " + note)
        for fact in audit.get("facts", []):
            evidence = fact["evidence"]
            audit_lines.extend(
                [
                    "",
                    "**" + fact["criterion"] + "**",
                    "",
                    _block((evidence.get("error") or evidence["summary"])[:1800]),
                ]
            )
        audit_lines.append(
            "Fact displays are excerpts. "
            "[Full canonical queries and returned data](fact-audit.json)"
        )
    for logs in sorted(job_dir.glob("*/agent")):
        artifacts = logs / "artifacts"
        capture = _read(artifacts / "tool-results.json", {})
        if not capture.get("complete"):
            lines.extend(
                [
                    "",
                    "**Evidence capture incomplete or unavailable.**",
                    _block(capture.get("errors", ["No observation capture was exported."])),
                ]
            )
        smoke = _read(artifacts / "smoke.json", {})
        entries = smoke.get("results", [])
        if not entries and (artifacts / "investigation.json").exists():
            entries = [
                {
                    "question": (logs / "instruction.txt").read_text(encoding="utf-8"),
                    "result": _read(artifacts / "investigation.json", {}),
                }
            ]
        for entry in entries:
            _investigation(
                lines,
                entry["question"],
                entry["result"],
                artifacts.relative_to(job_dir),
                capture,
                audit_lines,
                "smoke.json" if smoke else "investigation.json",
            )
        failure = _read(artifacts / "failure.json", {})
        if failure:
            lines.extend(["", "## Execution failure", "", _block(failure)])
    path = job_dir / "opencluster-result.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
