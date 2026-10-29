"""Associate benchmark-only captures with public Tool Runs without inventing evidence."""

import json
import re
from datetime import datetime
from urllib.parse import urlsplit


def _time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def _matches(request, observation, run, integration):
    if run.get("error", "").startswith("not executed:"):
        return False
    if request["traceId"] != observation["traceId"]:
        return False
    try:
        if (
            not _time(observation["issuedAt"])
            <= _time(request["startedAt"])
            <= _time(observation["observedAt"])
        ):
            return False
    except KeyError, ValueError:
        return False
    address = urlsplit(integration.get("configuration", {}).get("url", ""))
    if request["origin"] != address.scheme + "://" + address.netloc:
        return False
    arguments = run.get("arguments") or {}
    tool = run["tool"]
    parameters = request.get("parameters", {})
    if tool == "prometheus_query":
        endpoint = "/api/v1/query" if arguments.get("mode") == "instant" else "/api/v1/query_range"
        parameter, query = "query", arguments.get("query")
    elif tool == "prometheus_discover_metrics":
        endpoint = "/api/v1/label/__name__/values"
        hint = re.sub(r"([\\.+*?()|\[\]{}^$])", r"\\\1", arguments.get("hint", ""))
        query = "{__name__=~" + json.dumps(".*" + hint + ".*")
        selector = arguments.get("selector", "")
        if selector and selector[1:-1].strip():
            query += "," + selector[1:-1]
        parameter, query = "match[]", query + "}"
    elif tool == "loki_query_logs":
        endpoint, parameter, query = "/loki/api/v1/query_range", "query", arguments.get("query")
    elif tool == "tempo_search_traces":
        endpoint, parameter, query = "/api/search", "q", arguments.get("query")
    elif tool == "tempo_get_trace":
        endpoint = "/api/v2/traces/" + arguments.get("traceId", "").lower().zfill(32)
        parameter, query = "", None
    else:
        return False
    if request["path"] != address.path.rstrip("/") + endpoint:
        return False
    if parameter and parameters.get(parameter) != [query]:
        return False
    if tool == "loki_query_logs":
        if parameters.get("direction") != [arguments.get("direction", "backward")]:
            return False
        if parameters.get("limit") != [str(arguments.get("limit", 100))]:
            return False
    elif tool == "tempo_search_traces":
        if parameters.get("limit") != [str(arguments.get("limit", 20))]:
            return False
    elif tool == "prometheus_query" and arguments.get("mode") == "range":
        # The returned effective step includes source-bound clamping, even in a cut observation.
        applied = re.search(r'(?<!\\)"stepSeconds"\s*:\s*(\d+)', observation["content"])
        expected_step = int(applied[1]) if applied else arguments.get("step")
        if expected_step is not None:
            try:
                if float(parameters.get("step", [""])[0]) != float(expected_step):
                    return False
            except ValueError, TypeError:
                return False
    for parameter, bound in (
        ("time", "windowUntil"),
        ("start", "windowFrom"),
        ("end", "windowUntil"),
    ):
        # Failed reads retain the Investigation window, not an applied source window.
        if run["outcome"] != "succeeded" or parameter not in parameters or bound not in run:
            continue
        try:
            observed = float(parameters[parameter][0])
            if tool == "loki_query_logs":
                observed /= 1e9
            if abs(observed - _time(run[bound])) > 0.001:
                return False
        except ValueError, TypeError:
            return False
    return True


def collect_results(capture_path, log_path, results, integrations):
    errors = []
    records = []
    if not capture_path.exists():
        errors.append("Observation capture file is missing.")
    elif capture_path.stat().st_size > 8 * 1024 * 1024 + 128 * 1024:
        errors.append("Capture exceeded its total bound.")
    else:
        for line in capture_path.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
                if record.get("kind") == "capture_error":
                    errors.append(record["error"])
                else:
                    records.append(record)
            except json.JSONDecodeError, AttributeError:
                errors.append("Capture contains an incomplete JSON record.")
    trace_ids = {}
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("trace_id") and entry.get("investigation_id"):
                trace_ids[entry["trace_id"]] = entry["investigation_id"]
    runs = {
        (result["id"], run["ordinal"]): run for result in results for run in result.get("runs", [])
    }
    installations = {value["id"]: value for value in integrations.values()}
    requests = [record for record in records if record["kind"] == "request"]
    observations: dict[tuple[str, int], dict] = {}
    owners: dict[int, list] = {}
    for record in records:
        if record["kind"] != "observation":
            continue
        investigation = trace_ids.get(record["traceId"])
        if not investigation:
            errors.append(
                "Captured trace has no structured-log link to an Investigation: "
                + record["traceId"]
            )
            continue
        header = re.match(r"^\[run (\d+)\] (\S+) ([^\n]+)", record["content"])
        if not header:
            errors.append("Observation has no native Tool Run header.")
            continue
        key = investigation, int(header[1])
        run = runs.get(key)
        try:
            arguments = json.loads(header[3]) or {}
        except json.JSONDecodeError:
            arguments = None
        if not run or run["tool"] != header[2] or arguments != (run.get("arguments") or {}):
            errors.append(f"Captured observation does not match the public Tool Run: {key}")
            continue
        if key in observations:
            if observations[key]["content"] != record["content"]:
                errors.append(f"Conflicting observations for Tool Run {key}")
            continue
        indices = [
            index
            for index, request in enumerate(requests)
            if _matches(request, record, run, installations.get(run.get("integrationId"), {}))
        ]
        observation = {
            **record,
            "investigationId": investigation,
            "ordinal": run["ordinal"],
            "requests": [requests[index] for index in indices],
            "requestStatus": "matched"
            if indices
            else "No source request recorded (rejected or not executed before HTTP)",
        }
        observations[key] = observation
        for index in indices:
            owners.setdefault(index, []).append(key)
        if not indices and run["outcome"] == "succeeded":
            observation["requestStatus"] = "unmatched"
            errors.append(f"No unambiguous endpoint metadata for successful Tool Run {key}")
    for index, matched in owners.items():
        if len(matched) > 1:
            errors.append(f"Endpoint metadata is ambiguous between Tool Runs {matched}")
            for key in matched:
                observations[key]["requests"].remove(requests[index])
                observations[key]["requestStatus"] = "ambiguous"
        if requests[index].get("parameterError"):
            errors.append(requests[index]["parameterError"])
    for key in runs.keys() - observations.keys():
        errors.append(f"Actual observation is missing for Tool Run {key}")
    return {
        "complete": not errors,
        "errors": errors,
        "provenance": (
            "Bounded Tool observations as submitted to the real provider adapter; "
            "HTTP read metadata from the benchmark recorder. "
            "No private model reasoning or headers."
        ),
        "toolResults": list(observations.values()),
        "unmatchedRequests": [
            request for index, request in enumerate(requests) if index not in owners
        ],
    }
