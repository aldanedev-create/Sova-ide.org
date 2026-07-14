# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

root = Path(SPECPATH).parents[1]
a = Analysis([str(root / "cli" / "shell.py")], pathex=[str(root)], hiddenimports=["sova_engine", "novadev.standard_library"])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="sova-shell", console=True, icon=str(root / "installer" / "windows" / "assets" / "sova.ico"))
