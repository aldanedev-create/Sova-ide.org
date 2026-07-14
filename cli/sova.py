from __future__ import annotations

import sys
from pathlib import Path

if not getattr(sys, "frozen", False):
    platform_root = Path(__file__).resolve().parents[1]
    if str(platform_root) not in sys.path:
        sys.path.insert(0, str(platform_root))

from sova_engine.cli import main


if __name__ == "__main__":
    executable = Path(sys.executable if getattr(sys, "frozen", False) else __file__).stem.lower()
    aliases = {"sovafmt": "format", "sovalint": "lint", "sova-doc": "docs"}
    arguments = [aliases[executable], *sys.argv[1:]] if executable in aliases else sys.argv[1:]
    raise SystemExit(main(arguments))
