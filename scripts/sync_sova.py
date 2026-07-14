from __future__ import annotations

"""Refresh deployable Sova mirrors from the canonical repository sources."""

import shutil
from pathlib import Path


PLATFORM = Path(__file__).resolve().parents[1]
REPOSITORY = PLATFORM.parent
SOVA = REPOSITORY / "sova"


def ignore_generated(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in {"__pycache__", ".pytest_cache"} or name.endswith(".pyc")}


def sync_tree(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise SystemExit(f"Canonical source directory is missing: {source}")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination, ignore=ignore_generated)
    print(f"synced {source.relative_to(REPOSITORY)} -> {destination.relative_to(REPOSITORY)}")


def main() -> int:
    sync_tree(SOVA / "sova_engine", PLATFORM / "sova_engine")
    sync_tree(SOVA / "docs", PLATFORM / "docs")
    sync_tree(SOVA / "examples", PLATFORM / "examples")

    novadev_target = PLATFORM / "novadev"
    novadev_target.mkdir(exist_ok=True)
    shutil.copy2(REPOSITORY / "novadev" / "standard_library.py", novadev_target / "standard_library.py")
    (novadev_target / "__init__.py").write_text(
        '"""Deployment copy of NovaDev\'s canonical library provider."""\n',
        encoding="utf-8",
    )
    print("synced novadev/standard_library.py -> sova-platform/novadev/standard_library.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
