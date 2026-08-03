# -*- coding: UTF-8 -*-

"""TourBillon est le logiciel officiel de la billonnière utilisé pour
le tournoi de Billon qui a lieu chaque année à Floyon, le premier dimanche d'août."""

from importlib.metadata import PackageNotFoundError, version as _package_version

__long_name__ = "TourBillon"

# Single source of truth: the version is declared in ``pyproject.toml`` and read
# back from the installed package metadata. When running from a source tree that
# is not installed, fall back to a development marker.
try:
    __version__ = _package_version("tourbillon")
except PackageNotFoundError:  # pragma: no cover - only when not installed
    __version__ = "0.0.0+dev"
