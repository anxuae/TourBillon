# -*- coding: UTF-8 -*-

"""Tests for the unified Settings class (single source of truth)."""

import os

import pytest

from tourbillon.settings import Settings, DEFAULTS


def test_defaults(tmp_path):
    settings = Settings({"save_dir": str(tmp_path)})
    assert settings.host == DEFAULTS["host"]
    assert settings.teams_by_match == DEFAULTS["teams_by_match"]
    assert settings.default_draw == "deterministic"


def test_attribute_read_write(tmp_path):
    settings = Settings({"save_dir": str(tmp_path)})
    settings.port = 9000
    assert settings.port == 9000
    assert settings.get("port") == 9000


def test_set_unknown_key_raises(tmp_path):
    settings = Settings({"save_dir": str(tmp_path)})
    with pytest.raises(KeyError):
        settings.set("unknown", 1)


def test_update_ignores_unknown_keys(tmp_path):
    settings = Settings({"save_dir": str(tmp_path)})
    settings.update({"port": 1234, "nope": "x"})
    assert settings.port == 1234
    assert not hasattr(settings, "nope") or settings.get("nope") is None


def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "settings.yml")
    settings = Settings({"save_dir": str(tmp_path), "port": 4242}, path=path)
    settings.teams_by_match = 3
    settings.save()

    assert os.path.isfile(path)
    reloaded = Settings.load(path)
    assert reloaded.port == 4242
    assert reloaded.teams_by_match == 3


def test_save_without_path_uses_save_dir(tmp_path):
    # Without an explicit path, settings are written to <save_dir>/settings.yml
    # so custom options (e.g. draw overrides) are always persisted.
    settings = Settings({"save_dir": str(tmp_path)})
    target = settings.save()
    assert target == os.path.join(str(tmp_path), "settings.yml")
    assert os.path.isfile(target)


def test_draw_config_defaults(tmp_path):
    # Draw options start from each algorithm's built-in DEFAULT.
    settings = Settings({"save_dir": str(tmp_path)})
    assert settings.draw_config("genetic")["max_disparity"] == 2


def test_draw_config_loaded_from_file(tmp_path):
    # A settings file enriches the defaults per algorithm and per option;
    # unknown options are ignored, missing ones keep their default.
    path = str(tmp_path / "settings.yml")
    settings = Settings(
        {"save_dir": str(tmp_path),
         "draws": {"genetic": {"max_disparity": 5, "bogus": 1}}},
        path=path,
    )
    effective = settings.draw_config("genetic")
    assert effective["max_disparity"] == 5
    assert "bogus" not in effective
    assert effective["mutation_rate"] == 0.2  # untouched option keeps its default

    # The values survive a save/load round-trip.
    settings.save()
    reloaded = Settings.load(path)
    assert reloaded.draw_config("genetic")["max_disparity"] == 5


def test_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("TOURBILLON_PORT", "5555")
    monkeypatch.setenv("TOURBILLON_SAVE_DIR", str(tmp_path))
    settings = Settings.load()
    assert settings.port == 5555
    assert settings.save_dir == str(tmp_path)


def test_new_tournament_defaults(tmp_path):
    settings = Settings({"save_dir": str(tmp_path), "teams_by_match": 4})
    defaults = settings.new_tournament_defaults()
    assert defaults["teams_by_match"] == 4
    assert defaults["default_draw"] == "deterministic"


def test_as_dict_is_a_copy(tmp_path):
    settings = Settings({"save_dir": str(tmp_path)})
    data = settings.as_dict()
    data["port"] = -1
    assert settings.port != -1
