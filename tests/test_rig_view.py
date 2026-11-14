#!/usr/bin/env python3
"""Tests for rig/pi/view_server.py over real HTTP, and the page's logic in rig/pi/view/view.js."""
import hashlib
import http.client
import json
import os
import pathlib
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest

RIG_DIR = pathlib.Path(__file__).resolve().parents[1] / "rig" / "pi"
sys.path.insert(0, str(RIG_DIR))

import view_server  # noqa: E402

HEADER = "time_utc,burst,clock_synced,channel,burst_rows,sample_level,sample_rows,sample_std,air_level,verdict\n"
ROW_OK = "2026-11-05T19:00:00.000+00:00,1,1,a2,925,850.5,400,0.3,438.0,ok\n"
ROW_BAD = "2026-11-05T19:15:00.000+00:00,2,1,a2,925,301.0,10,5.6,438.0,thin\n"
ROW_ABORTED = "2026-11-05T19:30:00.000+00:00,3,1,a2,40,,0,,,aborted\n"


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.source = pathlib.Path(self.dir.name) / "summary.csv"
        (pathlib.Path(self.dir.name) / "secret.txt").write_text("not for the page")
        self.source.write_text(HEADER + ROW_OK)
        self.server = subprocess.Popen(
            [sys.executable, str(RIG_DIR / "view_server.py"), "--source", str(self.source), "--port", "0", "--interval", "0.1"],
            stdout=subprocess.PIPE,
            text=True,
            cwd=self.dir.name,  # beside secret.txt, so a server that served paths would reach it
        )
        self.addCleanup(self.server.wait)
        self.addCleanup(self.server.kill)
        self.addCleanup(self.server.stdout.close)
        line = self.server.stdout.readline()
        match = re.search(r"http://([\d.]+):(\d+)/", line)
        self.assertIsNotNone(match, line)
        self.host, self.port = match.group(1), int(match.group(2))

    def request(self, path, method="GET"):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        connection.request(method, path)
        response = connection.getresponse()
        body = response.read()
        connection.close()
        return response, body

    def wait_for_copy(self, text):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            response, body = self.request("/summary.csv")
            if response.status == 200 and body.decode() == text:
                return
            time.sleep(0.02)
        self.fail(f"copy never read {text!r}")

    def test_listens_on_this_computer_only(self):
        self.assertEqual(self.host, "127.0.0.1")
        listening = pathlib.Path("/proc/net/tcp").read_text()
        self.assertIn(f"0100007F:{self.port:04X}", listening)
        self.assertNotIn(f"00000000:{self.port:04X}", listening)

    def test_serves_the_page_and_its_own_files(self):
        for path, kind in (("/", "text/html"), ("/view.js", "text/javascript"), ("/view.css", "text/css")):
            with self.subTest(path):
                response, _ = self.request(path)
                self.assertEqual(response.status, 200)
                self.assertIn(kind, response.getheader("Content-Type"))
                self.assertEqual(response.getheader("Cache-Control"), "no-store")

    def test_the_page_may_not_load_from_or_talk_to_anywhere_else(self):
        response, _ = self.request("/")
        policy = response.getheader("Content-Security-Policy")
        self.assertIn("default-src 'none'", policy)
        self.assertIn("connect-src 'self'", policy)

    def test_serves_only_its_named_files(self):
        for path in (
            "/secret.txt", "/../secret.txt", "/%2e%2e/secret.txt", "//etc/passwd", "/view/", "/view_server.py",
            "/rig.toml", "/summary.csv.tmp", "/../rig.toml", "/index.html",
        ):
            with self.subTest(path):
                self.assertEqual(self.request(path)[0].status, 404)

    def test_refuses_anything_but_reading(self):
        for method in ("POST", "PUT", "DELETE", "PATCH"):
            with self.subTest(method):
                self.assertEqual(self.request("/summary.csv", method)[0].status, 501)

    def test_the_copy_follows_the_original(self):
        self.wait_for_copy(HEADER + ROW_OK)
        with open(self.source, "a", encoding="ascii") as log:
            log.write(ROW_BAD)
        self.wait_for_copy(HEADER + ROW_OK + ROW_BAD)

    def test_the_original_is_not_changed(self):
        before = (hashlib.sha256(self.source.read_bytes()).hexdigest(), self.source.stat().st_mtime_ns)
        self.wait_for_copy(HEADER + ROW_OK)
        time.sleep(0.3)
        self.assertEqual((hashlib.sha256(self.source.read_bytes()).hexdigest(), self.source.stat().st_mtime_ns), before)

    def test_a_missing_original_keeps_the_last_copy(self):
        self.wait_for_copy(HEADER + ROW_OK)
        self.source.unlink()
        time.sleep(0.3)
        response, body = self.request("/summary.csv")
        self.assertEqual(response.status, 200)
        self.assertEqual(body.decode(), HEADER + ROW_OK)
        self.assertIsNone(self.server.poll())

    def test_stops_cleanly(self):
        self.server.send_signal(signal.SIGTERM)
        self.assertEqual(self.server.wait(timeout=5), 0)


class NoDataYetTest(unittest.TestCase):
    def test_no_summary_yet_is_a_404_not_a_crash(self):
        with tempfile.TemporaryDirectory() as folder:
            server = subprocess.Popen(
                [sys.executable, str(RIG_DIR / "view_server.py"), "--source", f"{folder}/summary.csv", "--port", "0"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            try:
                port = int(re.search(r":(\d+)/", server.stdout.readline()).group(1))
                connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                connection.request("GET", "/summary.csv")
                self.assertEqual(connection.getresponse().status, 404)
                connection.close()
            finally:
                server.kill()
                server.wait()
                server.stdout.close()


class CopyTest(unittest.TestCase):
    def test_the_copy_holds_the_last_good_read(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "source"
            latest = view_server.Latest()
            self.assertIsNone(latest.content)
            source.write_text("one")
            view_server.copy_once(source, latest)
            self.assertEqual(latest.content, b"one")
            source.unlink()
            with self.assertRaises(OSError):
                view_server.copy_once(source, latest)
            self.assertEqual(latest.content, b"one")


class CleanFailureTest(unittest.TestCase):
    """What happens around the server: a taken port, and what it leaves behind."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.tmp = pathlib.Path(self.dir.name) / "tmp"
        self.tmp.mkdir()
        self.source = pathlib.Path(self.dir.name) / "summary.csv"
        self.source.write_text(HEADER + ROW_OK)
        self.env = {**os.environ, "TMPDIR": str(self.tmp)}

    def command(self, port):
        return [sys.executable, str(RIG_DIR / "view_server.py"), "--source", str(self.source), "--port", str(port), "--interval", "0.05"]

    def test_a_taken_port_says_so_in_one_line(self):
        with socket.socket() as taken:
            taken.bind(("127.0.0.1", 0))
            taken.listen()
            result = subprocess.run(
                self.command(taken.getsockname()[1]), capture_output=True, text=True, timeout=10, env=self.env
            )
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("already in use", result.stderr)
        self.assertEqual(len(result.stderr.strip().splitlines()), 1, result.stderr)
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_it_writes_no_files_and_a_hard_kill_leaves_none(self):
        server = subprocess.Popen(self.command(0), stdout=subprocess.PIPE, text=True, env=self.env)
        self.addCleanup(server.stdout.close)
        self.addCleanup(server.wait)
        self.addCleanup(server.kill)
        port = int(re.search(r":(\d+)/", server.stdout.readline()).group(1))
        deadline = time.monotonic() + 5
        status = None
        while status != 200 and time.monotonic() < deadline:
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            connection.request("GET", "/summary.csv")
            response = connection.getresponse()
            response.read()
            status = response.status
            connection.close()
            time.sleep(0.02)
        self.assertEqual(status, 200)
        self.assertEqual(list(self.tmp.iterdir()), [])
        server.kill()
        server.wait()
        self.assertEqual(list(self.tmp.iterdir()), [])


NODE = shutil.which("node")
# Run in Node with no DOM: the file exports its logic when there is no document.
JS_RUNNER = """
const view = require(process.argv[1]);
const csv = process.argv[2];
const now = Date.parse(process.argv[3]);
const rows = view.parseSummary(csv);
console.log(JSON.stringify({
  count: rows.length,
  good: view.goodRows(rows).map((row) => row.still),
  verdicts: rows.map((row) => view.verdictLabel(row.verdict)),
  state: view.summarize(rows, now),
}));
"""


@unittest.skipUnless(NODE, "needs node")
class PageLogicTest(unittest.TestCase):
    def run_page(self, csv, now="2026-11-05T19:35:00Z"):
        output = subprocess.check_output(
            [NODE, "-e", JS_RUNNER, str(RIG_DIR / "view" / "view.js"), csv, now], text=True, env=dict(os.environ)
        )
        return json.loads(output)

    def test_no_rows(self):
        self.assertEqual(self.run_page("")["state"]["kind"], "none")
        self.assertEqual(self.run_page(HEADER)["state"]["kind"], "none")

    def test_a_good_last_cycle(self):
        result = self.run_page(HEADER + ROW_OK, now="2026-11-05T19:05:00Z")
        self.assertEqual(result["state"]["kind"], "good")
        self.assertEqual(result["good"], [850.5])

    def test_only_good_cycles_count_as_readings(self):
        result = self.run_page(HEADER + ROW_OK + ROW_BAD + ROW_ABORTED)
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["good"], [850.5])

    def test_a_flagged_last_cycle_says_check(self):
        result = self.run_page(HEADER + ROW_OK + ROW_BAD, now="2026-11-05T19:20:00Z")
        self.assertEqual(result["state"]["kind"], "check")
        self.assertIn("barely reached", result["state"]["title"])

    def test_old_data_says_not_updating_even_if_it_was_good(self):
        result = self.run_page(HEADER + ROW_OK, now="2026-11-05T20:00:00Z")
        self.assertEqual(result["state"]["kind"], "stale")

    def test_a_torn_last_line_is_ignored(self):
        result = self.run_page(HEADER + ROW_OK + "2026-11-05T19:15:00.000+00:00,2,1,a2", now="2026-11-05T19:05:00Z")
        self.assertEqual(result["count"], 1)

    def test_an_unknown_verdict_still_says_check(self):
        result = self.run_page(HEADER + ROW_OK.replace(",ok\n", ",something_new\n"), now="2026-11-05T19:05:00Z")
        self.assertEqual(result["state"]["kind"], "check")
        self.assertEqual(result["good"], [])

    def test_every_verdict_the_logger_can_write_has_a_label(self):
        source = (RIG_DIR / "rig.py").read_text()
        verdicts = set(re.findall(r'"(ok|thin|no_sample|no_motion|aborted)"', source))
        self.assertEqual(verdicts, {"ok", "thin", "no_sample", "no_motion", "aborted"})
        verdicts.discard("ok")
        csv = HEADER + "".join(ROW_OK.replace(",ok\n", f",{verdict}\n") for verdict in sorted(verdicts))
        for label in self.run_page(csv)["verdicts"]:
            self.assertNotRegex(label, r"[a-z]+_[a-z]+", label)


if __name__ == "__main__":
    unittest.main()
