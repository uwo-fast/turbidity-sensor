#!/usr/bin/env python3
"""Tests for tools/capture_serial.py and tools/summarize_capture.py.

The capture tests drive the real script through a pseudo-terminal standing in
for the board's serial port.
"""
import os
import pathlib
import signal
import subprocess
import sys
import tempfile
import time
import unittest

TOOLS = pathlib.Path(__file__).resolve().parents[1] / "tools"
CAPTURE = TOOLS / "capture_serial.py"
SUMMARIZE = TOOLS / "summarize_capture.py"
HEADER = "timestamp_ms,sensor,adc_counts,raw_mv"


class CaptureSerialTest(unittest.TestCase):
    def setUp(self):
        self.master, slave = os.openpty()
        self.port = os.ttyname(slave)
        self.slave = slave
        self.workdir = tempfile.TemporaryDirectory()
        # A folder that does not exist yet: the capture tool must create it.
        self.output = pathlib.Path(self.workdir.name) / "2026-01-01" / "capture.csv"

    def tearDown(self):
        os.close(self.master)
        os.close(self.slave)
        self.workdir.cleanup()

    def run_capture(self, chunks, *extra_args):
        process = subprocess.Popen(
            [sys.executable, str(CAPTURE), "--port", self.port, "--output", str(self.output), *extra_args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # The script flushes pending input when it opens the port; give it time to.
        time.sleep(0.5)
        for chunk in chunks:
            os.write(self.master, chunk)
            time.sleep(0.05)
        _, stderr = process.communicate(timeout=15)
        return process.returncode, stderr

    def test_discards_preamble_and_truncated_last_line(self):
        code, stderr = self.run_capture(
            [
                b"0,tsw10,5",  # tail of a line from before the reset
                b"\r\n" + HEADER.encode() + b"\r\n",
                b"100,tsw10,850.25,4155.518\r\n",
                b"200,tsw10,849.",
                b"75,4153.076\r\n",
                b"300,tsw10,8",  # cut off when the capture ends
            ],
            "--duration",
            "1.0",
        )
        self.assertEqual(code, 0, stderr)
        self.assertEqual(
            self.output.read_bytes().decode(),
            HEADER + "\n100,tsw10,850.25,4155.518\n200,tsw10,849.75,4153.076\n",
        )
        self.assertIn("captured 2 rows", stderr)

    def test_ctrl_c_keeps_captured_rows(self):
        process = subprocess.Popen(
            [sys.executable, str(CAPTURE), "--port", self.port, "--output", str(self.output)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        time.sleep(0.5)
        os.write(self.master, HEADER.encode() + b"\r\n100,tsw10,850.25,4155.518\r\n")
        time.sleep(0.5)
        process.send_signal(signal.SIGINT)
        _, stderr = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 0, stderr)
        self.assertIn("captured 1 rows", stderr)
        self.assertEqual(self.output.read_bytes().decode(), HEADER + "\n100,tsw10,850.25,4155.518\n")

    def test_stops_on_board_reset(self):
        code, stderr = self.run_capture(
            [
                HEADER.encode() + b"\r\n",
                b"100,tsw10,850.25,4155.518\r\n",
                HEADER.encode() + b"\r\n",
            ],
            "--duration",
            "5.0",
        )
        self.assertEqual(code, 1)
        self.assertIn("reset mid-capture after 1 rows", stderr)
        self.assertEqual(self.output.read_bytes().decode(), HEADER + "\n100,tsw10,850.25,4155.518\n")

    def test_fails_without_header(self):
        code, stderr = self.run_capture([b"garbage\r\n"], "--header-timeout", "1.0")
        self.assertEqual(code, 1)
        self.assertIn("no CSV header", stderr)


class SummarizeCaptureTest(unittest.TestCase):
    def setUp(self):
        self.workdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.workdir.cleanup()

    def write(self, name, text):
        path = pathlib.Path(self.workdir.name) / name
        path.write_text(text)
        return str(path)

    def run_summarize(self, *paths):
        return subprocess.run(
            [sys.executable, str(SUMMARIZE), *paths], capture_output=True, text=True, check=False
        )

    def test_reports_statistics_per_signal_column(self):
        path = self.write(
            "clear.csv",
            "timestamp_ms,sensor,adc_counts,raw_mv,estimated_ntu\n"
            "1000,tsw10,850,4150.0,0\n"
            "1500,tsw10,852,4160.0,0\n"
            "2000,tsw10,854,4170.0,0\n",
        )
        result = self.run_summarize(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "file,column,n,duration_s,mean,std,min,max",
                f"{path},adc_counts,3,1.0,852.000,2.000,850.000,854.000",
                f"{path},raw_mv,3,1.0,4160.000,10.000,4150.000,4170.000",
            ],
        )

    def test_reports_each_channel_of_a_multichannel_log(self):
        path = self.write(
            "multi.csv",
            "timestamp_ms,vcc_mv,adc_counts_a0,adc_counts_a1\n"
            "0,5010,800,700\n"
            "100,5012,802,704\n",
        )
        result = self.run_summarize(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            [line.split(",")[1] for line in result.stdout.splitlines()[1:]],
            ["vcc_mv", "adc_counts_a0", "adc_counts_a1"],
        )

    def test_normalizes_each_channel_against_its_own_references(self):
        dark = self.write("dark.csv", "timestamp_ms,adc_counts_a0,adc_counts_a1\n0,50,20\n100,50,20\n")
        clear = self.write("clear.csv", "timestamp_ms,adc_counts_a0,adc_counts_a1\n0,850,620\n100,850,620\n")
        sample = self.write("sample.csv", "timestamp_ms,vcc_mv,adc_counts_a0,adc_counts_a1\n0,5000,450,170\n100,5000,450,170\n")
        result = self.run_summarize("--dark", dark, "--clear", clear, sample)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "file,column,n,duration_s,mean,std,min,max,transmittance,attenuation",
                f"{sample},vcc_mv,2,0.1,5000.000,0.000,5000.000,5000.000,,",
                f"{sample},adc_counts_a0,2,0.1,450.000,0.000,450.000,450.000,0.5000,0.6931",
                f"{sample},adc_counts_a1,2,0.1,170.000,0.000,170.000,170.000,0.2500,1.3863",
            ],
        )

    def test_rejects_clear_reference_not_above_dark(self):
        dark = self.write("dark.csv", "timestamp_ms,adc_counts\n0,500\n")
        clear = self.write("clear.csv", "timestamp_ms,adc_counts\n0,500\n")
        sample = self.write("sample.csv", "timestamp_ms,adc_counts\n0,400\n")
        result = self.run_summarize("--dark", dark, "--clear", clear, sample)
        self.assertEqual(result.returncode, 1)
        self.assertIn("adc_counts: clear reference is not above dark", result.stderr)

    def test_rejects_reference_missing_a_channel(self):
        dark = self.write("dark.csv", "timestamp_ms,adc_counts_a0\n0,50\n")
        clear = self.write("clear.csv", "timestamp_ms,adc_counts_a0,adc_counts_a1\n0,850,800\n")
        sample = self.write("sample.csv", "timestamp_ms,adc_counts_a0,adc_counts_a1\n0,450,400\n")
        result = self.run_summarize("--dark", dark, "--clear", clear, sample)
        self.assertEqual(result.returncode, 1)
        self.assertIn("dark.csv has no adc_counts_a1 column", result.stderr)

    def test_requires_dark_and_clear_together(self):
        dark = self.write("dark.csv", "timestamp_ms,adc_counts\n0,50\n")
        sample = self.write("sample.csv", "timestamp_ms,adc_counts\n0,400\n")
        result = self.run_summarize("--dark", dark, sample)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--dark and --clear go together", result.stderr)

    def test_warns_when_clear_reference_is_near_full_scale(self):
        dark = self.write("dark.csv", "timestamp_ms,adc_counts\n0,10\n")
        clear = self.write("clear.csv", "timestamp_ms,adc_counts\n0,1000\n")
        sample = self.write("sample.csv", "timestamp_ms,adc_counts\n0,900\n")
        result = self.run_summarize("--dark", dark, "--clear", clear, sample)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("adc_counts: clear reference 1000.0 counts is near full scale", result.stderr)

    def test_rejects_malformed_row(self):
        path = self.write("bad.csv", "timestamp_ms,raw_mv\n1000,4150\n1500,oops\n")
        result = self.run_summarize(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("bad.csv:3: malformed row", result.stderr)

    def test_rejects_file_without_rows(self):
        path = self.write("empty.csv", "timestamp_ms,raw_mv\n")
        result = self.run_summarize(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("no data rows", result.stderr)


if __name__ == "__main__":
    unittest.main()
