# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: bundle TourBillon as a single Windows executable.

Usage (from the project root, frontend already built via ``scripts/build-ui.py``):

    poetry run pyinstaller scripts/build-exe.spec --noconfirm

The resulting ``tourbillon.exe`` is a self-contained onefile build: it embeds
the Python interpreter, all dependencies (FastAPI, uvicorn, numpy, PyYAML...)
and the static frontend assets (``tourbillon/static/dist``) and the YAML
banner (``tourbillon/assets/banner.txt``).
"""

from pathlib import Path

from PyInstaller.utils.hooks import collect_all

ROOT_DIR = Path(__file__).resolve().parent.parent
ICON_PATH = ROOT_DIR / "tourbillon-ui" / "src" / "assets" / "icon.ico"

datas = [
    (str(ROOT_DIR / "tourbillon" / "static" / "dist"), "tourbillon/static/dist"),
    (str(ROOT_DIR / "tourbillon" / "assets" / "banner.txt"), "tourbillon/assets"),
]
binaries = []
hiddenimports = []

# uvicorn[standard] optional dependencies (httptools, websockets, watchfiles...)
# are loaded dynamically and not always picked up by PyInstaller's static
# analysis, so pull them in explicitly.
for package in ("uvicorn", "fastapi", "pydantic"):
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports

a = Analysis(
    [str(ROOT_DIR / "tourbillon" / "__main__.py")],
    pathex=[str(ROOT_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="tourbillon",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon=str(ICON_PATH) if ICON_PATH.is_file() else None,
)
