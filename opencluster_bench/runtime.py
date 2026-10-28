"""Run the real application through its public HTTP API; no model or Tool execution here."""

import base64
import http.client
import json
import os
import re
import secrets
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import quote, urlsplit

MAX_RESPONSE_BYTES = 4 * 1024 * 1024


class API:
    def __init__(self, base_url="http://localhost:8081"):
        address = urlsplit(base_url)
        if address.scheme != "http" or address.hostname not in ("localhost", "127.0.0.1"):
            raise ValueError("the adapter API must be a local HTTP endpoint")
        if address.path or address.query or address.fragment or address.username:
            raise ValueError("the adapter API must be a local origin")
        self.base_url = base_url
        self.host = address.hostname
        self.port = address.port or 80
        self.cookie = ""

    def request(self, method, path, body=None, *, authorization="", timeout=20):
        headers = {"Origin": self.base_url}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if self.cookie:
            headers["Cookie"] = self.cookie
        if authorization:
            headers["Authorization"] = authorization
        connection = http.client.HTTPConnection(self.host, self.port, timeout=timeout)
        try:
            connection.request(
                method, "/api/v1" + path, json.dumps(body) if body is not None else None, headers
            )
            response = connection.getresponse()
            data = response.read(MAX_RESPONSE_BYTES + 1)
            if len(data) > MAX_RESPONSE_BYTES:
                raise RuntimeError("application response exceeded the adapter limit")
            if not 200 <= response.status < 300:
                raise RuntimeError(f"application {method} {path}: HTTP {response.status}")
            cookie = SimpleCookie()
            for name, value in response.getheaders():
                if name.lower() == "set-cookie":
                    cookie.load(value)
            if "__Host-oc_session" in cookie:
                # The application issues a Secure cookie on localhost. Python's generic
                # cookie jar rejects HTTP localhost; forward it only to this fixed origin.
                self.cookie = "__Host-oc_session=" + cookie["__Host-oc_session"].value
            return json.loads(data) if data else {}
        finally:
            connection.close()

    def bootstrap(self, token, password):
        self.request(
            "POST",
            "/auth/local/bootstrap",
            {
                "organizationName": "Benchmark",
                "email": "benchmark@example.test",
                "password": password,
            },
            authorization="Bearer " + token,
        )
        if not self.cookie:
            raise RuntimeError("bootstrap did not issue a session")

    def verify_integrations(self, urls):
        verified = {}
        for kind, url in urls.items():
            configuration = {"url": url}
            if kind in ("loki", "tempo"):
                configuration["auth"] = "bearer"
            created = self.request(
                "POST",
                "/integrations",
                {
                    "type": kind,
                    "name": kind.title(),
                    "configuration": configuration,
                },
            )["integration"]
            view = self.request("POST", f"/integrations/{created['id']}/verify", {})
            tools = view.get("toolAvailability", [])
            if (
                view.get("status") != "verified"
                or not tools
                or not all(tool["available"] for tool in tools)
            ):
                raise RuntimeError(f"{kind} query access was not verified")
            verified[kind] = view
        return verified


def investigate(api, instruction, start, end, *, timeout=540, poll_interval=1):
    started = time.monotonic()
    opened = api.request(
        "POST",
        "/conversations",
        {
            "subject": "Observability benchmark",
            "message": instruction,
            "windowFrom": start,
            "windowUntil": end,
        },
    )
    turn = opened.get("turn")
    if not turn or not turn.get("investigationId"):
        raise RuntimeError("Conversation did not open an Investigation")
    investigation_id = turn["investigationId"]
    deadline = started + timeout
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            api.request("POST", f"/investigations/{investigation_id}/cancel", {}, timeout=5)
            result = api.request("GET", f"/investigations/{investigation_id}", timeout=5)
            result["adapterTimedOut"] = True
            result["adapterElapsedSeconds"] = time.monotonic() - started
            return result
        try:
            result = api.request(
                "GET", f"/investigations/{investigation_id}", timeout=min(20, remaining)
            )
        except TimeoutError:
            continue
        if result.get("status") in ("concluded", "failed", "cancelled"):
            result["adapterElapsedSeconds"] = time.monotonic() - started
            return result
        time.sleep(min(poll_interval, max(0, deadline - time.monotonic())))


def trajectory(instruction, result, model):
    steps = [{"step_id": 1, "source": "user", "message": instruction}]
    for run in result.get("runs", []):
        call_id = "run-" + str(run["ordinal"])
        recorded = {key: value for key, value in run.items() if key != "arguments"}
        recorded["contentAvailability"] = "Full Tool-result content is not persisted."
        steps.append(
            {
                "step_id": len(steps) + 1,
                "source": "agent",
                "message": "(tool use)",
                "timestamp": run["startedAt"],
                "tool_calls": [
                    {
                        "tool_call_id": call_id,
                        "function_name": run["tool"],
                        "arguments": run.get("arguments", {}),
                    }
                ],
                "observation": {
                    "results": [
                        {
                            "source_call_id": call_id,
                            "extra": {"is_error": run["outcome"] != "succeeded"},
                            "content": json.dumps(recorded, ensure_ascii=False),
                        }
                    ]
                },
                "extra": {"reconstructedFrom": "durable Tool Run", "ordinal": run["ordinal"]},
            }
        )
    conclusion_keys = (
        "status",
        "conclusionStatus",
        "summary",
        "impact",
        "findings",
        "hypotheses",
        "actions",
        "limitations",
        "stoppedBy",
        "error",
        "adapterTimedOut",
    )
    conclusion = {key: result[key] for key in conclusion_keys if key in result}
    steps.append(
        {
            "step_id": len(steps) + 1,
            "source": "agent",
            "message": json.dumps(conclusion, ensure_ascii=False),
        }
    )
    usage = result.get("usage", {})
    metrics = {}
    for source, target in (
        ("inputTokens", "total_prompt_tokens"),
        ("outputTokens", "total_completion_tokens"),
    ):
        if source in usage:
            metrics[target] = usage[source]
    return {
        "schema_version": "ATIF-v1.7",
        "session_id": result["id"],
        "agent": {
            "name": "opencluster",
            "version": os.environ.get("OC_BENCH_COMMIT", "unknown"),
            "model_name": model,
        },
        "steps": steps,
        "final_metrics": metrics,
        "extra": {
            "reconstructedFrom": "public Investigation and durable Tool Runs",
            "privateReasoningAvailable": False,
            "fullToolResultsAvailable": False,
            "originalModelCallIdsAvailable": False,
            "elapsedSeconds": result.get("adapterElapsedSeconds"),
        },
    }


def smoke_checks(results):
    patterns = {
        "prometheus_query": r": [1-9]\d* series, [1-9]\d* samples;",
        "loki_query_logs": r": [1-9]\d* log excerpts,",
        "tempo_search_traces": r": [1-9]\d* traces,",
        "tempo_get_trace": r", [1-9]\d* spans;",
    }
    checks = {tool: False for tool in patterns}
    for item in results:
        for run in item["result"].get("runs", []):
            tool = run["tool"]
            if tool in patterns and run["outcome"] == "succeeded" and run.get("sources"):
                checks[tool] |= bool(re.search(patterns[tool], run.get("summary", "")))
    return checks


def main():
    instruction = Path("/app/instruction.txt").read_text()
    output = Path("/logs/agent")
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    smoke = os.environ.get("OC_BENCH_SMOKE") == "1"
    end = datetime.fromisoformat(os.environ["O11Y_SCENARIO_TIME_ISO"].replace("Z", "+00:00"))
    hours = 24 if smoke else int(os.environ.get("OC_BENCH_WINDOW_HOURS", "24"))
    start = (end - timedelta(hours=hours)).isoformat()
    until = end.isoformat()
    known_secrets: list[str] = []
    process = None
    result = None
    exit_code = 1

    def write_json(name, value):
        text = json.dumps(value, ensure_ascii=False, indent=2)
        for secret in known_secrets:
            text = text.replace(secret, "[redacted]")
        (output / name).write_text(text)

    def stop(_signal, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    with tempfile.TemporaryDirectory(prefix="opencluster-bench-") as directory:
        private = Path(directory)
        bootstrap, password = secrets.token_urlsafe(40), secrets.token_urlsafe(40)
        seal = base64.b64encode(secrets.token_bytes(32)).decode()
        postgres_password = Path("/run/secrets/postgres_password").read_text()
        model_key = Path("/run/opencluster/model-key").read_text()
        known_secrets.extend([bootstrap, password, seal, postgres_password, model_key])
        for name, value in (
            ("bootstrap", bootstrap),
            ("seal", seal),
            (
                "dsn",
                "postgres://opencluster:"
                + quote(postgres_password, safe="")
                + "@postgres:5432/opencluster?sslmode=disable",
            ),
        ):
            path = private / name
            path.write_text(value)
            path.chmod(0o600)
        env = os.environ.copy()
        env.update(
            {
                "OC_SERVER_ADDRESS": "127.0.0.1:8081",
                "OC_PUBLIC_URL": "http://localhost:8081",
                "OC_DATABASE_DSN_FILE": str(private / "dsn"),
                "OC_BOOTSTRAP_TOKEN_FILE": str(private / "bootstrap"),
                "OC_ENCRYPTION_KEY_FILE": str(private / "seal"),
                "OC_AI_API_KEY_FILE": "/run/opencluster/model-key",
                "OC_AI_PROVIDER": os.environ["OC_BENCH_PROVIDER"],
                "OC_AI_MODEL": os.environ["OC_BENCH_MODEL"],
                "OC_INVESTIGATION_WORKERS": "1",
            }
        )
        log_path = private / "backend.log"
        try:
            with log_path.open("wb") as log:
                process = subprocess.Popen(
                    ["/app/controlplane"], env=env, stdout=log, stderr=subprocess.STDOUT
                )
            ready_deadline = time.monotonic() + 60
            while True:
                if process.poll() is not None:
                    raise RuntimeError("OpenCluster exited before readiness")
                connection = http.client.HTTPConnection("localhost", 8081, timeout=1)
                try:
                    connection.request("GET", "/readyz")
                    response = connection.getresponse()
                    if response.status == 200:
                        break
                except OSError:
                    pass
                finally:
                    connection.close()
                if time.monotonic() >= ready_deadline:
                    raise TimeoutError("OpenCluster readiness timed out")
                time.sleep(0.2)
            api = API()
            api.bootstrap(bootstrap, password)
            verified = api.verify_integrations(
                {
                    kind: os.environ[kind.upper() + "_URL"]
                    for kind in ("prometheus", "loki", "tempo")
                }
            )
            write_json("integrations.json", verified)
            if smoke:
                questions = (
                    "Use Prometheus to query count(http_requests_total) as an instant query. "
                    "Report whether it returned actual metric data.",
                    'Read a few Loki log excerpts matching {job=~".+"} in this window. '
                    "Report whether actual timestamped log lines were returned.",
                    "Search Tempo for a few traces using {} in this window. Retrieve one of the "
                    "returned trace IDs with tempo_get_trace. Report whether spans were returned.",
                )
                results = []
                for question in questions:
                    result = investigate(
                        api,
                        question,
                        start,
                        until,
                        timeout=min(150, max(0, 540 - (time.monotonic() - started))),
                    )
                    results.append({"question": question, "result": result})
                checks = smoke_checks(results)
                passed = all(checks.values()) and all(
                    item["result"]["status"] == "concluded"
                    and not item["result"].get("adapterTimedOut")
                    for item in results
                )
                write_json("smoke.json", {"passed": passed, "checks": checks, "results": results})
                instruction = questions[-1]
                exit_code = 0 if passed else 1
            else:
                result = investigate(
                    api,
                    instruction,
                    start,
                    until,
                    timeout=max(0, 540 - (time.monotonic() - started)),
                )
                exit_code = (
                    0
                    if result["status"] == "concluded" and not result.get("adapterTimedOut")
                    else 1
                )
            write_json("investigation.json", result)
            write_json(
                "trajectory.json",
                trajectory(
                    instruction,
                    result,
                    os.environ["OC_BENCH_PROVIDER"] + "/" + os.environ["OC_BENCH_MODEL"],
                ),
            )
        except (Exception, KeyboardInterrupt) as error:
            write_json("failure.json", {"error": type(error).__name__ + ": " + str(error)})
        finally:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            if log_path.exists():
                with log_path.open("rb") as source:
                    source.seek(max(0, log_path.stat().st_size - 65536))
                    log_tail = source.read().decode(errors="replace")
                for secret in known_secrets:
                    log_tail = log_tail.replace(secret, "[redacted]")
                (output / "backend.log").write_text(log_tail)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
