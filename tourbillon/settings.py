# -*- coding: UTF-8 -*-

"""Unified application settings (single source of truth).

Replaces the legacy ``config.py`` (wxPython-coupled ``.ini`` parser). The
configuration is split into two backend domains (the third domain, the web UI
preferences, lives in the frontend and is not handled here):

1. **Server / API**: host, port, save directory, auto-save.
2. **Business / tournament**: default values used when creating a new tournament
   and the default draw algorithm.

A single :class:`Settings` class reads, writes, loads and saves a simple YAML
file (keys and values in English, primitive types only). Values can be
overridden by environment variables prefixed with ``TOURBILLON_``. Draw options
are not stored here: they are exposed through the draws registry (see
``GET /api/draws``).
"""

import os
import os.path as osp
import sys

import yaml

from .core import draws

# Default settings (primitive types only).
DEFAULTS = {
    # Server / API domain.
    "host": "127.0.0.1",
    "port": 8000,
    "save_dir": osp.expanduser("~/TourBillon"),
    "auto_save": True,
    # Business / tournament domain (defaults for a new tournament).
    "players_by_team": 2,
    "points_by_match": 12,
    "teams_by_match": 2,
    "rank_by_wins": True,
    "rank_by_joker": True,
    "rank_by_duration": False,
    "default_draw": draws.DEFAULT_DRAW,
}

# Mapping env var -> (key, cast function).
ENV = {
    "TOURBILLON_HOST": ("host", str),
    "TOURBILLON_PORT": ("port", int),
    "TOURBILLON_SAVE_DIR": ("save_dir", str),
    "TOURBILLON_AUTO_SAVE": ("auto_save", lambda v: v.lower() in ("1", "true", "yes")),
}


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
        super().__setattr__("_data", dict(DEFAULTS))
        if values:
            self.update(values)
        os.makedirs(self._data["save_dir"], exist_ok=True)

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
        """Update several settings at once (unknown keys are ignored)."""
        for key, value in values.items():
            if key in DEFAULTS:
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

        :param path: optional path to a YAML settings file
        """
        values = {}
        if path and osp.isfile(path):
            with open(path, "r", encoding="utf-8") as fp:
                loaded = yaml.safe_load(fp) or {}
            values.update({k: v for k, v in loaded.items() if k in DEFAULTS})

        for env_name, (key, cast) in ENV.items():
            if env_name in os.environ:
                values[key] = cast(os.environ[env_name])

        return cls(values, path=path)

    def save(self, path=None):
        """Save the current settings to a YAML file.

        :param path: optional destination path (defaults to the loaded path)
        """
        target = path or self.path
        if target is None:
            raise ValueError("No settings file path provided")
        directory = osp.dirname(osp.abspath(target))
        os.makedirs(directory, exist_ok=True)
        with open(target, "w", encoding="utf-8") as fp:
            yaml.safe_dump(self._data, fp, default_flow_style=False, sort_keys=True)
        super().__setattr__("path", target)
        return target

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def new_tournament_defaults(self):
        """Return the default parameters used to create a new tournament."""
        return {
            "teams_by_match": self._data["teams_by_match"],
            "points_by_match": self._data["points_by_match"],
            "players_by_team": self._data["players_by_team"],
            "default_draw": self._data["default_draw"],
        }

    def as_dict(self):
        """Return the settings as a plain dictionary."""
        return dict(self._data)
