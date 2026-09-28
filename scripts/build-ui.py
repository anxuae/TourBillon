#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Poetry build hook: bundle the built Vue frontend into the Python package.

Poetry calls :func:`build` (see ``[tool.poetry.build]`` in ``pyproject.toml``)
before collecting the files listed in ``include``. This script builds the
``tourbillon-ui`` frontend (if needed) and copies the resulting static assets
into ``tourbillon/static/dist`` so they get bundled inside the sdist/wheel and
served in production by :mod:`tourbillon.api.app` (see ``PACKAGE_WEB_DIR``).
"""

import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "tourbillon-ui"
FRONTEND_BUILD_DIR = FRONTEND_DIR / "dist"
PACKAGE_STATIC_DIR = ROOT_DIR / "tourbillon" / "static" / "dist"


def build_frontend():
    """Run ``npm install`` and ``npm run build`` in the frontend folder."""
    npm = shutil.which("npm")
    if npm is None:
        print("build_frontend: npm not found on PATH, skipping frontend build")
        return
    print("build_frontend: installing frontend dependencies...")
    subprocess.run([npm, "install"], cwd=FRONTEND_DIR, check=True)
    print("build_frontend: building frontend...")
    subprocess.run([npm, "run", "build"], cwd=FRONTEND_DIR, check=True)


def copy_frontend():
    """Copy the built frontend assets into the package static folder."""
    if not FRONTEND_BUILD_DIR.is_dir():
        print("build_frontend: no built frontend found, skipping copy")
        return
    if PACKAGE_STATIC_DIR.exists():
        shutil.rmtree(PACKAGE_STATIC_DIR)
    PACKAGE_STATIC_DIR.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(FRONTEND_BUILD_DIR, PACKAGE_STATIC_DIR)
    print(f"build_frontend: copied {FRONTEND_BUILD_DIR} -> {PACKAGE_STATIC_DIR}")


def build(setup_kwargs=None):
    """Entry point called by Poetry before packaging (sdist and wheel)."""
    if FRONTEND_DIR.is_dir() and not FRONTEND_BUILD_DIR.is_dir():
        build_frontend()
    copy_frontend()
    return setup_kwargs


if __name__ == "__main__":
    build()
