# -*- coding: UTF-8 -*-

"""Static assets bundled with TourBillon (non-code resources).

Currently holds the ASCII-art banner written at the top of YAML tournament save
files. Kept out of ``core`` so the domain package stays code-only.
"""

import os.path as osp

import tourbillon

_ASSETS_DIR = osp.dirname(osp.abspath(__file__))
_BANNER_FILE = osp.join(_ASSETS_DIR, "banner.txt")


def path(*names):
    """Return the absolute path of an asset file."""
    return osp.join(_ASSETS_DIR, *names)


def banner():
    """Return the banner as an ASCII-art comment block."""
    with open(_BANNER_FILE, encoding="utf-8") as fp:
        lines = fp.readlines()
    text = "#" + "#".join(lines)
    return text.format(version="%s.%s.%s" % tourbillon.__version__)
