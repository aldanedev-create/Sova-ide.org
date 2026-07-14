# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

root = Path(SPECPATH).parents[1]
a = Analysis(
    [str(root / "cli" / "sova.py")],
    pathex=[str(root)],
    # Docs are copied beside the executable by staging and portable packaging.
    # Bundling them here would expose only a transient one-file _MEI path.
    datas=[(str(root / "examples"), "examples")],
    hiddenimports=["sova_engine", "novadev.standard_library"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="sova",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=str(root / "installer" / "windows" / "assets" / "sova.ico"),
)
