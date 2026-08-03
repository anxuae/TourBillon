# -*- coding: UTF-8 -*-

"""Static assets bundled with TourBillon (non-code resources).

Currently holds the ASCII-art banner written at the top of YAML tournament save
files. Kept out of ``core`` so the domain package stays code-only.
"""

from pathlib import Path

import tourbillon

ASSETS_DIR = Path(__file__).resolve().parent
BANNER_FILE = ASSETS_DIR / "banner.txt"


def path(*names):
    """Return the absolute path of an asset file."""
    return str(ASSETS_DIR.joinpath(*names))


def banner():
    """Return the banner as an ASCII-art comment block."""
    with open(BANNER_FILE, encoding="utf-8") as fp:
        lines = fp.readlines()
    text = "#" + "#".join(lines)
    return text.format(version=tourbillon.__version__)
