from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


PLATFORM = Path(__file__).resolve().parents[1]


class CliLauncherTests(unittest.TestCase):
    def test_source_launcher_prints_platform_docs_path(self):
        completed = subprocess.run(
            [sys.executable, str(PLATFORM / "cli" / "sova.py"), "docs"],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(Path(completed.stdout.strip()), (PLATFORM / "docs" / "language-overview.md").resolve())


if __name__ == "__main__":
    unittest.main()
