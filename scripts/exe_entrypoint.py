#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""PyInstaller entry script for the ``tourbillon.exe`` build.

PyInstaller executes its ``Analysis`` entry script as a standalone top-level
module (not as part of the ``tourbillon`` package), which breaks the relative
imports used in ``tourbillon/__main__.py``. Importing ``tourbillon`` here
first, before calling ``run()``, keeps the package context intact.
"""

import sys

from tourbillon.__main__ import run

if __name__ == "__main__":
    try:
        run()
    except Exception:
        # Frozen exe: keep the console window open so the traceback is readable.
        if getattr(sys, "frozen", False):
            import traceback
            traceback.print_exc()
            input("\nTourBillon crashed. Press Enter to close this window...")
            sys.exit(1)
        raise
