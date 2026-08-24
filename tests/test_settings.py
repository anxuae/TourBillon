# -*- coding: UTF-8 -*-

"""Tests for the unified Settings class (single source of truth)."""

import pytest
from pathlib import Path

from tourbillon.settings import Settings, DEFAULTS


def test_defaults(tmp_path):
    settings = Settings({"save_dir": str(tmp_path)})
    assert settings.host == DEFAULTS["host"]
    assert settings.rank_by_wins == DEFAULTS["rank_by_wins"]
    assert settings.rank_by_buchholz == DEFAULTS["rank_by_buchholz"]
    assert settings.rank_by_goal_avg == DEFAULTS["rank_by_goal_avg"]
    assert settings.default_draw == "deterministic"
    assert settings.rotation_seconds == DEFAULTS["rotation_seconds"]


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
    settings.rank_by_joker = False
    settings.rank_by_buchholz = False
    settings.rank_by_goal_avg = False
    settings.save()

    assert Path(path).is_file()
    reloaded = Settings.load(path)
    assert reloaded.port == 4242
    assert reloaded.rank_by_joker is False
    assert reloaded.rank_by_buchholz is False
    assert reloaded.rank_by_goal_avg is False


def test_save_without_path_uses_config_dir(tmp_path, monkeypatch):
    # Without an explicit path, settings are written to the platform-specific
    # user configuration file, independent from save_dir (changing save_dir
    # never loses the settings).
    import tourbillon.settings as settings_mod

    config_file = tmp_path / "config" / "settings.yml"
    monkeypatch.setattr(settings_mod, "default_settings_path", lambda: config_file)

    settings = Settings({"save_dir": str(tmp_path)})
    target = settings.save()
    assert target == str(config_file)
    assert Path(target).is_file()


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


def test_as_dict_is_a_copy(tmp_path):
    settings = Settings({"save_dir": str(tmp_path)})
    data = settings.as_dict()
    data["general"]["port"] = -1
    assert settings.port != -1


def test_as_dict_contains_display_section(tmp_path):
    settings = Settings({"save_dir": str(tmp_path)})
    data = settings.as_dict()
    assert "display" in data
    assert data["display"]["rotation_seconds"] == settings.rotation_seconds


def test_rotation_seconds_accepts_small_value(tmp_path):
    settings = Settings({"save_dir": str(tmp_path)})
    settings.update({"display": {"rotation_seconds": 1}})
    assert settings.rotation_seconds == 1
