#!/usr/bin/env python3
"""Short automated tests for find_ids.py (stdlib only)."""
import os
import subprocess
import sys
import tempfile
import unittest

import find_ids


SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "find_ids.py")


def _write(path, data, mode="wb"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode) as fh:
        fh.write(data)


class FindIdsTests(unittest.TestCase):
    def test_load_terms_crlf_blanks_duplicates(self):
        with tempfile.TemporaryDirectory() as td:
            terms_path = os.path.join(td, "terms.txt")
            _write(terms_path, b"TERM_A\r\n\r\nTERM_B\r\nTERM_A\r\n  TERM_C  \r\n\r\n")
            self.assertEqual(find_ids.load_terms(terms_path), ["TERM_A", "TERM_B", "TERM_C"])

    def test_chunk_boundary_match(self):
        term = "BOUNDARYTOKEN"
        payload = b"xxxx" + term.encode("utf-8") + b"yyyy"
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "split.bin")
            _write(path, payload)
            found = find_ids.scan_file(
                path,
                (term.encode("utf-8"),),
                overlap=len(term) - 1,
                chunk_size=8,
            )
            self.assertEqual(found, {term.encode("utf-8")})

    def test_unreadable_file_skipped(self):
        found = find_ids.scan_file(
            os.path.join("no_such_dir", "missing.bin"),
            (b"TERM_A",),
            overlap=5,
        )
        self.assertEqual(found, set())

    def test_cli_order_counts_and_no_paths(self):
        with tempfile.TemporaryDirectory() as td:
            terms_path = os.path.join(td, "terms.txt")
            _write(terms_path, b"TERM_A\r\nTERM_B\r\nTERM_C\r\nTERM_MISSING\r\nTERM_A\r\n")

            root = os.path.join(td, "tree")
            _write(os.path.join(root, "nested", "one.txt"), b"prefix TERM_A suffix\n")
            _write(os.path.join(root, "two.txt"), b"TERM_B and TERM_A\n")
            _write(os.path.join(root, "three.txt"), b"only TERM_C here\n")
            _write(os.path.join(root, "empty.txt"), b"")
            # filename contains a term, content does not
            _write(os.path.join(root, "TERM_MISSING.txt"), b"nothing relevant\n")

            out_path = os.path.join(td, "found.txt")
            proc = subprocess.run(
                [sys.executable, SCRIPT, terms_path, root, "-t", "4", "-o", out_path],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with open(out_path, encoding="utf-8") as fh:
                result = fh.read()
            self.assertEqual(result, "TERM_A\nTERM_B\nTERM_C\n")
            self.assertNotIn(root, result)
            self.assertNotIn("one.txt", result)
            self.assertNotIn("nested", result)
            self.assertNotIn(root, proc.stdout)
            self.assertNotIn(root, proc.stderr)

            proc = subprocess.run(
                [sys.executable, SCRIPT, terms_path, root, "--counts", "-t", "2"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout, "TERM_A\t2\nTERM_B\t1\nTERM_C\t1\n")
            self.assertNotIn("one.txt", proc.stdout)
            self.assertNotIn(root, proc.stdout)


if __name__ == "__main__":
    unittest.main()
