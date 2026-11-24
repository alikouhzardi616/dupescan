import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from dupescan import main, scan_directory


class ScanDirectoryTests(unittest.TestCase):
    def test_finds_identical_files_and_computes_recoverable_bytes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "first.txt").write_bytes(b"same content")
            (root / "second.txt").write_bytes(b"same content")
            (root / "different.txt").write_bytes(b"different")

            report = scan_directory(root)

            self.assertEqual(report["scanned_files"], 3)
            self.assertEqual(report["duplicate_bytes"], len(b"same content"))
            self.assertEqual(len(report["duplicate_groups"]), 1)
            self.assertEqual(len(report["duplicate_groups"][0]["paths"]), 2)

    def test_minimum_size_filters_files_before_comparison(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "small-a.txt").write_bytes(b"x")
            (root / "small-b.txt").write_bytes(b"x")

            report = scan_directory(root, min_size=2)

            self.assertEqual(report["scanned_files"], 0)
            self.assertEqual(report["duplicate_groups"], [])

    def test_json_output_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main([temporary_directory, "--json"])

            self.assertEqual(result, 0)
            self.assertEqual(json.loads(output.getvalue())["scanned_files"], 0)


if __name__ == "__main__":
    unittest.main()
