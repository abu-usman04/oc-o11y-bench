import json
import threading
import time
import unittest
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from opencluster_bench.runtime import API, investigate, trajectory


@contextmanager
def application(*, status="concluded", delay=0, outcome="succeeded"):
    requests = []
    conclusion = {
        "id": "investigation-1",
        "status": status,
        "summary": "5xx share is 2%.",
        "conclusionStatus": "answered",
        "findings": [{"statement": "2%", "runRefs": [1]}],
        "usage": {"inputTokens": 120, "outputTokens": 30},
        "createdAt": "2026-10-28T10:00:00Z",
        "concludedAt": "2026-10-28T10:00:02Z",
        "runs": [
            {
                "ordinal": 1,
                "tool": "prometheus_query",
                "arguments": {"query": "test"},
                "outcome": outcome,
                "summary": "retained value=0.02",
                "sources": ["prometheus:source-1:instant"],
                "truncated": False,
                "windowFrom": "2026-10-28T09:00:00Z",
                "windowUntil": "2026-10-28T10:00:00Z",
                "startedAt": "2026-10-28T10:00:00Z",
                "finishedAt": "2026-10-28T10:00:01Z",
            }
        ],
    }

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.respond()

        def do_POST(self):
            self.respond()

        def respond(self):
            size = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(size)) if size else None
            requests.append((self.command, self.path, dict(self.headers), body))
            if self.command == "GET":
                time.sleep(delay)
            self.send_response(200)
            if self.path.endswith("/bootstrap"):
                self.send_header(
                    "Set-Cookie", "__Host-oc_session=session-secret; Path=/; Secure; HttpOnly"
                )
                reply = {"bootstrapped": True}
            elif self.path.endswith("/conversations"):
                reply = {"id": "conversation-1", "turn": {"investigationId": "investigation-1"}}
            elif self.path == "/api/v1/integrations":
                reply = {"integration": {"id": body["type"]}}
            elif self.path.endswith("/verify"):
                reply = {
                    "status": "verified",
                    "toolAvailability": [{"tool": "query", "available": True}],
                }
            else:
                reply = conclusion
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            try:
                self.wfile.write(json.dumps(reply).encode())
            except BrokenPipeError, ConnectionResetError, ConnectionAbortedError:
                pass

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield API(f"http://127.0.0.1:{server.server_port}"), requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


class AdapterTest(unittest.TestCase):
    def test_integrations_use_normal_creation_verification_and_availability(self):
        with application() as (api, requests):
            api.bootstrap("bootstrap-secret", "temporary strong admin password")
            verified = api.verify_integrations(
                {
                    "prometheus": "http://stack:9090",
                    "loki": "http://stack:3100",
                    "tempo": "http://stack:3200",
                }
            )
        self.assertEqual(set(verified), {"prometheus", "loki", "tempo"})
        created = [r[3] for r in requests if r[1] == "/api/v1/integrations"]
        self.assertEqual(
            created[1]["configuration"], {"url": "http://stack:3100", "auth": "bearer"}
        )
        self.assertEqual(
            created[2]["configuration"], {"url": "http://stack:3200", "auth": "bearer"}
        )
        self.assertEqual(sum(r[1].endswith("/verify") for r in requests), 3)

    def test_read_deadline_still_cancels_and_collects_the_investigation(self):
        with application(status="running", delay=0.1) as (api, requests):
            result = investigate(
                api, "Question", "2026-10-28T09:00:00Z", "2026-10-28T10:00:00Z", timeout=0.02
            )
        self.assertEqual(result["id"], "investigation-1")
        self.assertTrue(result["adapterTimedOut"])
        self.assertTrue(any(r[1].endswith("/cancel") for r in requests))

    def test_timeout_cancels_collects_and_reports_elapsed_time(self):
        with application(status="running") as (api, requests):
            result = investigate(
                api, "Question", "2026-10-28T09:00:00Z", "2026-10-28T10:00:00Z", timeout=0
            )
        self.assertTrue(result["adapterTimedOut"])
        self.assertGreaterEqual(result["adapterElapsedSeconds"], 0)
        self.assertTrue(any(r[1].endswith("/investigation-1/cancel") for r in requests))
        self.assertTrue(
            json.loads(trajectory("Question", result, "model")["steps"][-1]["message"])[
                "adapterTimedOut"
            ]
        )

    def test_prepared_case_keeps_upstream_question_and_grader(self):
        import tomllib
        from pathlib import Path
        from tempfile import TemporaryDirectory

        from opencluster_bench.__main__ import prepare_task

        root = Path(__file__).resolve().parents[1]
        upstream = root / "upstream" / "o11y-bench"
        with TemporaryDirectory() as directory:
            task = prepare_task(upstream, Path(directory), "promql-error-rate")
            metadata = tomllib.loads((task / "task.toml").read_text())
            self.assertNotIn("mcp_servers", metadata["environment"])
            self.assertEqual(metadata["verifier"]["timeout_sec"], 600)
            self.assertIn("full 60-minute window", (task / "instruction.md").read_text())
            for name in ("judge.py", "verifier.py", "checks.py", "facts.py"):
                self.assertEqual(
                    (task / "tests" / "grading" / name).read_bytes(),
                    (upstream / "grading" / name).read_bytes(),
                )
            self.assertEqual(
                (task / "environment" / "docker-compose.yaml").read_bytes(),
                (upstream / "environment" / "docker-compose.yaml").read_bytes(),
            )

    def test_failed_tool_runs_remain_errors_for_the_upstream_grader(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        from grading.transcript_parser import parse_transcript
        from harbor.models.trajectories import Trajectory

        with application(status="failed", outcome="failed") as (api, _):
            result = investigate(
                api, "Question", "2026-10-28T09:00:00Z", "2026-10-28T10:00:00Z", timeout=2
            )
        document = trajectory("Question", result, "test/model")
        Trajectory.model_validate(document)
        with TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "trajectory.json").write_text(json.dumps(document))
            transcript = parse_transcript(path)
        failures = [
            item for message in transcript.messages for item in (message.tool_results or [])
        ]
        self.assertTrue(failures[0].is_error)
        self.assertEqual(json.loads(transcript.final_answer())["status"], "failed")

    def test_bounded_diagnostics_do_not_export_a_cut_credential(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        from opencluster_bench.runtime import redacted_log

        secret = "api-key-that-must-never-be-exported"
        with TemporaryDirectory() as directory:
            path = Path(directory) / "backend.log"
            path.write_text("prefix-" * 20 + secret + "x" * 50, encoding="utf-8")
            exported = redacted_log(path, [secret], limit=60)
        self.assertNotIn("exported", exported)
        self.assertNotIn(secret, exported)
        self.assertLessEqual(len(exported), 60)

    def test_ungraded_report_keeps_findings_and_every_tool_attempt(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory

        from opencluster_bench.report import write_report

        with application() as (api, _):
            result = investigate(
                api,
                "What overall share returned 5xx?",
                "2026-10-28T09:00:00Z",
                "2026-10-28T10:00:00Z",
                timeout=2,
            )
        result["runs"].append(
            {
                "ordinal": 2,
                "tool": "tempo_get_trace",
                "arguments": {"traceId": "0123"},
                "outcome": "failed",
                "error": "Trace not available",
                "truncated": True,
            }
        )
        with TemporaryDirectory() as directory:
            job = Path(directory)
            logs = job / "trial-1" / "agent"
            logs.mkdir(parents=True)
            (logs / "instruction.txt").write_text("What overall share returned 5xx?")
            (logs / "investigation.json").write_text(json.dumps(result))
            report = write_report(job, "z-ai/glm-5.1", graded=False).read_text(encoding="utf-8")
        for expected in (
            "Ungraded",
            "What overall share returned 5xx?",
            "5xx share is 2%.",
            "Findings",
            '"runRefs"',
            "Tool Run 1",
            "prometheus_query",
            "Tool Run 2",
            "tempo_get_trace",
            "Trace not available",
            '"truncated": true',
            "2026-10-28T10:00:01Z",
            '"inputTokens": 120',
            "Full Tool-result content is not persisted",
        ):
            self.assertIn(expected, report)

    def test_no_grade_cli_does_not_require_a_judge_key(self):
        import subprocess
        import sys
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            config = Path(directory) / "config.toml"
            config.write_text(
                '[model]\nprovider="openrouter"\nname="z-ai/glm-5.1"\n'
                'api_key="test-only-never-sent"\n[run]\ncontrolplane_commit="invalid"\n',
                encoding="utf-8",
            )
            command = [
                sys.executable,
                "-m",
                "opencluster_bench",
                "promql-error-rate",
                "--config",
                str(config),
            ]
            ungraded = subprocess.run([*command, "--no-grade"], capture_output=True, text=True)
            graded = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(ungraded.returncode, 1)
        self.assertIn("controlplane_commit must be a full Git commit SHA", ungraded.stderr)
        self.assertIn("fill grading.anthropic_api_key", graded.stderr)

    def test_exact_question_window_session_and_honest_public_trajectory(self):
        with application() as (api, requests):
            api.bootstrap("bootstrap-secret", "temporary strong admin password")
            result = investigate(
                api,
                "What overall share returned 5xx?",
                "2026-10-28T09:00:00Z",
                "2026-10-28T10:00:00Z",
                timeout=2,
            )
        submitted = next(r for r in requests if r[1].endswith("/conversations"))
        self.assertEqual(
            submitted[3],
            {
                "subject": "Observability benchmark",
                "message": "What overall share returned 5xx?",
                "windowFrom": "2026-10-28T09:00:00Z",
                "windowUntil": "2026-10-28T10:00:00Z",
            },
        )
        self.assertEqual(submitted[2]["Cookie"], "__Host-oc_session=session-secret")
        self.assertEqual(submitted[2]["Origin"], api.base_url)
        exported = trajectory("What overall share returned 5xx?", result, "test/model")
        self.assertEqual(exported["final_metrics"]["total_prompt_tokens"], 120)
        self.assertEqual(exported["final_metrics"]["total_completion_tokens"], 30)
        final = exported["steps"][-1]
        self.assertEqual(json.loads(final["message"])["summary"], "5xx share is 2%.")
        self.assertNotIn("tool_calls", final)
        observation = exported["steps"][1]["observation"]["results"][0]["content"]
        self.assertIn("retained value=0.02", observation)
        self.assertIn("not persisted", observation)
        self.assertNotIn("session-secret", json.dumps(exported))


if __name__ == "__main__":
    unittest.main()
