from __future__ import annotations

"""Publish locally built Windows artifacts into the static website tree."""

import hashlib
import json
import shutil
import sys
from datetime import date
from pathlib import Path


PLATFORM = Path(__file__).resolve().parents[1]
RELEASE = PLATFORM / "release"
PUBLIC = PLATFORM / "website" / "public"
DOWNLOADS = PUBLIC / "downloads"
MANIFEST = PUBLIC / "releases" / "latest.json"
if str(PLATFORM) not in sys.path:
    sys.path.insert(0, str(PLATFORM))

from sova_engine.version import __version__ as VERSION


def artifact(filename: str) -> dict[str, object]:
    source = RELEASE / filename
    if not source.is_file():
        raise SystemExit(f"Release artifact is missing: {source}")
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, DOWNLOADS / filename)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    return {
        "filename": filename,
        "url": f"/downloads/{filename}",
        "sha256": digest,
        "size": source.stat().st_size,
        "available": True,
    }


def main() -> int:
    payload = {
        "version": VERSION,
        "released_at": date.today().isoformat(),
        "status": "available-unsigned",
        "checksums": {
            "filename": "SHA256SUMS.txt",
            "url": "/downloads/SHA256SUMS.txt",
        },
        "windows": {
            "installer": artifact(f"SovaSetup-x64-{VERSION}.exe"),
            "portable": artifact(f"SovaPortable-x64-{VERSION}.zip"),
        },
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    checksum_lines = [
        f'{payload["windows"][kind]["sha256"]}  {payload["windows"][kind]["filename"]}'
        for kind in ("installer", "portable")
    ]
    checksum_text = "\n".join(checksum_lines) + "\n"
    (RELEASE / "SHA256SUMS.txt").write_text(checksum_text, encoding="ascii")
    (DOWNLOADS / "SHA256SUMS.txt").write_text(checksum_text, encoding="ascii")
    print(f"Published Sova {VERSION} downloads and {MANIFEST.relative_to(PLATFORM)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
