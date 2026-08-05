# -*- coding: UTF-8 -*-

"""Unified application settings (single source of truth).

Replaces the legacy ``config.py`` (wxPython-coupled ``.ini`` parser). The
configuration is split into three backend domains (the web UI preferences live
in the frontend and are not handled here):

1. **Server / API**: host, port, save directory, auto-save.
2. **Business / tournament**: cross-tournament preferences (ranking tie-breakers
   and the default draw algorithm). The per-tournament parameters (teams per
   match, points per match, players per team) are chosen at tournament creation
   and are therefore NOT stored here.
3. **Draw options**: the per-algorithm options under the ``draws`` section.

A single :class:`Settings` class reads, writes, loads and saves a simple YAML
file (keys and values in English, primitive types only). The file lives in the
platform-specific user configuration directory (e.g. ``~/.config/tourbillon``
on Linux), independent from ``save_dir``. Values can be overridden by
environment variables prefixed with ``TOURBILLON_``. Each draw's options are
initialized from the algorithm's built-in ``DEFAULT`` and, when a settings file
exists, enriched with the saved values. The settings are loaded once at startup
and saved once at shutdown: nothing else mutates them.
"""

import os
import sys
from pathlib import Path

import yaml

from .core import draws

# Application name used to build the platform-specific configuration directory.
APP_NAME = "tourbillon"

# Environment variable used to pass the settings file path to the application
# factory when uvicorn reloads the app from an import string (``--reload``
# requires an import string, so the app cannot receive the already-built
# ``Settings`` instance directly). See ``tourbillon.__main__`` and
# ``tourbillon.api.app.create_app_from_env``.
SETTINGS_PATH_ENV = "TOURBILLON_SETTINGS_PATH"

# Base name of the settings file stored in the user configuration directory.
DEFAULT_SETTINGS_NAME = "settings.yml"


def config_dir():
    """Return the platform-specific user configuration directory.

    - Windows: ``%APPDATA%\\tourbillon``
    - macOS: ``~/Library/Application Support/tourbillon``
    - Linux / other: ``$XDG_CONFIG_HOME/tourbillon`` (defaults to
      ``~/.config/tourbillon``)

    The settings file lives here so it is independent from ``save_dir``:
    changing the save directory never loses the settings.
    """
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")
    return Path(base) / APP_NAME


def default_settings_path():
    """Return the default settings file path in the user config directory."""
    return config_dir() / DEFAULT_SETTINGS_NAME


# Grouping of the flat scalar keys into YAML sections for persistence. In memory
# the values stay flat (attribute access, e.g. ``settings.host``); on disk they
# are written under these sections for readability. The ``draws`` mapping is
# already nested and written as its own section.
SECTIONS = {
    "general": ("host", "port", "save_dir", "auto_save"),
    "tournament": (
        "rank_by_wins", "rank_by_joker", "rank_by_duration", "default_draw",
    ),
}

# Default settings (primitive types only).
DEFAULTS = {
    # Server / API domain.
    "host": "127.0.0.1",
    "port": 8000,
    "save_dir": str(Path.home() / "TourBillon"),
    "auto_save": True,
    # Business / tournament domain. The per-tournament parameters (teams per
    # match, points per match, players per team) are NOT stored here: they are
    # chosen when creating a tournament. Only cross-tournament preferences live
    # here (ranking tie-breakers and the default draw algorithm).
    "rank_by_wins": True,
    "rank_by_joker": True,
    "rank_by_duration": False,
    "default_draw": draws.DEFAULT_DRAW,
    # Draw options domain: the effective options of every algorithm, seeded
    # from each algorithm's built-in ``DEFAULT``. Shape: ``{draw_name: {...}}``.
    "draws": {name: draws.default_config(name) for name in draws.DRAWS},
}

# Mapping env var -> (key, cast function).
ENV = {
    "TOURBILLON_HOST": ("host", str),
    "TOURBILLON_PORT": ("port", int),
    "TOURBILLON_SAVE_DIR": ("save_dir", str),
    "TOURBILLON_AUTO_SAVE": ("auto_save", lambda v: v.lower() in ("1", "true", "yes")),
}


def _flatten(loaded):
    """Flatten a sectioned YAML mapping into the flat settings shape.

    Also accepts a legacy flat mapping (keys at top level) for backward
    compatibility. Unknown keys are ignored.
    """
    values = {}
    for section, keys in SECTIONS.items():
        chunk = loaded.get(section, {})
        if isinstance(chunk, dict):
            values.update({k: chunk[k] for k in keys if k in chunk})
    if isinstance(loaded.get("draws"), dict):
        values["draws"] = loaded["draws"]
    # Legacy flat files: pick up any known key sitting at the top level.
    values.update({k: v for k, v in loaded.items() if k in DEFAULTS})
    return values


class Settings:
    """Single, typed application settings container.

    Provides read/write access to the configuration values and load/save
    helpers for a YAML settings file. This is the only place where application
    settings are defined.
    """

    def __init__(self, values=None, path=None):
        # ``_data`` and ``path`` are set through ``super().__setattr__`` to
        # bypass the custom ``__setattr__`` below.
        super().__setattr__("path", path)
        data = dict(DEFAULTS)
        # Deep-copy the nested draw overrides so instances never share it.
        data["draws"] = {name: dict(cfg) for name, cfg in DEFAULTS["draws"].items()}
        super().__setattr__("_data", data)
        if values:
            self.update(values)
        Path(self._data["save_dir"]).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Read / write access (attribute-style and explicit)
    # ------------------------------------------------------------------ #
    def get(self, key, default=None):
        """Return a setting value."""
        return self._data.get(key, default)

    def set(self, key, value):
        """Set a setting value (must be a known key)."""
        if key not in DEFAULTS:
            raise KeyError(f"Unknown setting '{key}'")
        self._data[key] = value

    def update(self, values):
        """Update several settings at once (unknown keys are ignored).

        Accepts the sectioned shape (``{section: {key: value}}`` plus the
        ``draws`` mapping) as well as a legacy flat mapping. The ``draws``
        section is merged per algorithm and per option so that missing options
        keep their built-in default.
        """
        flat = _flatten(values)
        for key, value in flat.items():
            if key == "draws" and isinstance(value, dict):
                for name, config in value.items():
                    if name in self._data["draws"] and isinstance(config, dict):
                        known = self._data["draws"][name]
                        known.update({k: v for k, v in config.items() if k in known})
            elif key in DEFAULTS:
                self._data[key] = value

    def __getattr__(self, name):
        # Called only when the attribute is not found through normal lookup.
        data = self.__dict__.get("_data", {})
        if name in data:
            return data[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in DEFAULTS:
            self._data[name] = value
        else:
            super().__setattr__(name, value)

    # ------------------------------------------------------------------ #
    # Load / save
    # ------------------------------------------------------------------ #
    @classmethod
    def load(cls, path=None):
        """Load settings from a YAML file and environment variables.

        :param path: optional path to a YAML settings file; defaults to the
            platform-specific user configuration file (see :func:`config_dir`)
        """
        path = path or str(default_settings_path())
        values = {}
        if path and Path(path).is_file():
            with open(path, "r", encoding="utf-8") as fp:
                loaded = yaml.safe_load(fp) or {}
            values.update(_flatten(loaded))

        for env_name, (key, cast) in ENV.items():
            if env_name in os.environ:
                values[key] = cast(os.environ[env_name])

        return cls(values, path=path)

    def save(self, path=None):
        """Save the current settings to a YAML file.

        If no path was ever provided, the settings are written to the
        platform-specific user configuration file (see :func:`config_dir`) so
        they are independent from ``save_dir``.

        :param path: optional destination path (defaults to the loaded path)
        """
        target = path or self.path or str(default_settings_path())
        Path(target).resolve().parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as fp:
            yaml.safe_dump(self._as_sections(), fp, default_flow_style=False, sort_keys=True)
        super().__setattr__("path", target)
        return target

    def _as_sections(self):
        """Return the settings grouped into YAML sections (for persistence)."""
        data = {
            section: {key: self._data[key] for key in keys}
            for section, keys in SECTIONS.items()
        }
        data["draws"] = {name: dict(cfg) for name, cfg in self._data["draws"].items()}
        return data

    # ------------------------------------------------------------------ #
    # Draw options (read-only accessor)
    # ------------------------------------------------------------------ #
    def draw_config(self, name):
        """Return a copy of the effective options of a draw.

        :param name: draw algorithm identifier
        :return: effective options mapping
        """
        return dict(self._data["draws"][name])

    def as_dict(self):
        """Return the settings grouped into sections (the public shape).

        The structure mirrors the persisted YAML: ``{section: {key: value}}``
        for the scalar sections plus a nested ``draws`` mapping. This is the
        single place that defines the settings sections, so consumers (API,
        frontend) never redeclare them.
        """
        return self._as_sections()
