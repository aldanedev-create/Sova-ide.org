from __future__ import annotations

import sys
import unittest
from pathlib import Path


PLATFORM = Path(__file__).resolve().parents[1]
if str(PLATFORM) not in sys.path:
    sys.path.insert(0, str(PLATFORM))

from api._common import check_project, normalize_filename, run_project


class HostedApiTests(unittest.TestCase):
    def test_run_uses_the_sova_pipeline(self) -> None:
        result = run_project("main.sova", {"main.sova": 'let name = "Sova"\nprint("Hello {name}")'}, {})
        self.assertTrue(result["success"])
        self.assertEqual(result["stdout"], "Hello Sova\n")

    def test_multi_file_import(self) -> None:
        files = {
            "main.sova": "from tools import answer\nprint(answer())",
            "tools.sova": "export function answer() { return 42 }",
        }
        result = run_project("main.sova", files, {})
        self.assertTrue(result["success"])
        self.assertEqual(result["stdout"], "42\n")

    def test_online_shell_is_blocked(self) -> None:
        result = run_project("main.sova", {"main.sova": 'shell "echo blocked"'}, {})
        self.assertFalse(result["success"])
        self.assertIn("disabled", result["stderr"].lower())

    def test_online_local_files_are_blocked(self) -> None:
        result = run_project("main.sova", {"main.sova": 'print(Sova.Files.read("secret.txt"))'}, {})
        self.assertFalse(result["success"])
        self.assertIn("disabled", result["stderr"].lower())

    def test_runtime_limit_interrupts_loop(self) -> None:
        result = run_project("main.sova", {"main.sova": "while true { }"}, {"max_steps": 200})
        self.assertFalse(result["success"])
        self.assertIn("limit", result["stderr"].lower())

    def test_semantic_check_reports_structural_error(self) -> None:
        result = check_project("main.sova", {"main.sova": "return 4"})
        self.assertFalse(result["success"])
        self.assertTrue(result["diagnostics"])

    def test_project_path_traversal_is_rejected(self) -> None:
        with self.assertRaises(Exception):
            normalize_filename("../secret.sova")


if __name__ == "__main__":
    unittest.main()
