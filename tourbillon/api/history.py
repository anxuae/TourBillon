# -*- coding: UTF-8 -*-

"""Cross-tournament history aggregation.

Loads every save file from the save directory (retro-compatible with the legacy
YAML files) and computes per-player statistics across the editions.

Parsing a save file is expensive, so loaded tournaments are kept in a global
cache keyed by path and modification time. Every helper of this module goes
through :func:`load_tournament`, which means an edition is parsed only once and
reused by the streaming endpoint, the aggregation and the player detail.
"""

import threading
from pathlib import Path

from ..core import tournament as core_tournament

# Global cache: path -> (mtime, tournament). Guarded by a lock because FastAPI
# serves requests from a thread pool.
_CACHE = {}
_CACHE_LOCK = threading.Lock()


def clear_cache() -> None:
    """Drop every cached tournament (useful when the save dir changes)."""
    with _CACHE_LOCK:
        _CACHE.clear()


def load_tournament(path):
    """Return the tournament stored in ``path``, using the global cache.

    Returns ``None`` when the file is missing or cannot be parsed. The cache
    entry is invalidated as soon as the file modification time changes.
    """
    path = str(path)
    try:
        mtime = Path(path).stat().st_mtime
    except OSError:
        with _CACHE_LOCK:
            _CACHE.pop(path, None)
        return None

    with _CACHE_LOCK:
        cached = _CACHE.get(path)
    if cached is not None and cached[0] == mtime:
        return cached[1]

    try:
        trn = core_tournament.load(path)
    except Exception:  # pylint: disable=broad-except
        with _CACHE_LOCK:
            _CACHE.pop(path, None)
        return None

    with _CACHE_LOCK:
        _CACHE[path] = (mtime, trn)
    return trn

def _iter_tournaments(save_dir):
    """Yield ``(path, tournament)`` for every readable save file."""
    save_dir = Path(save_dir)
    for pattern in ("*.yml", "*.trb"):
        for path in sorted(str(p) for p in save_dir.glob(pattern)):
            trn = load_tournament(path)
            if trn is not None:
                yield path, trn


def _year_of(trn, path):
    """Return the tournament year (from its start date, else the filename)."""
    try:
        return trn.start_date.year
    except Exception:  # pylint: disable=broad-except
        return Path(path).stem


def _ranking_of(trn, with_wins, with_joker, with_buchholz, with_goal_avg):
    """Return the ranking of ``trn`` as a ``team -> rank`` mapping."""
    return dict(
        trn.ranking(
            with_wins=with_wins,
            with_joker=with_joker,
            with_buchholz=with_buchholz,
            with_goal_avg=with_goal_avg,
        )
    )


def list_tournaments(save_dir):
    """Return metadata for every save file (sorted by year)."""
    result = []
    for path, trn in _iter_tournaments(save_dir):
        result.append(
            {
                "filename": Path(path).name,
                "year": _year_of(trn, path),
                "nb_teams": trn.nb_teams(),
                "nb_rounds": trn.nb_rounds(),
                "modified": Path(path).stat().st_mtime,
            }
        )
    return result


def _player_name(player):
    """Return a stable display name for a player."""
    return f"{player.firstname} {player.lastname}".strip()


def aggregate_players(save_dir, with_wins=True, with_joker=True, with_buchholz=True, with_goal_avg=True):
    """Return aggregated statistics per player across every edition."""
    players = {}
    for path, trn in _iter_tournaments(save_dir):
        year = _year_of(trn, path)
        ranking = _ranking_of(trn, with_wins, with_joker, with_buchholz, with_goal_avg)
        for team in trn.teams():
            rank = ranking.get(team)
            for player in team.players():
                name = _player_name(player)
                entry = players.setdefault(
                    name,
                    {"name": name, "firstname": player.firstname,
                     "lastname": player.lastname, "participations": 0,
                     "wins": 0, "points": 0, "best_rank": None, "years": []},
                )
                entry["participations"] += 1
                entry["wins"] += team.wins()
                entry["points"] += team.points()
                if rank is not None:
                    if entry["best_rank"] is None or rank < entry["best_rank"]:
                        entry["best_rank"] = rank
                entry["years"].append(year)
    return sorted(players.values(), key=lambda e: e["name"])


def tournament_players(save_dir, filename, with_wins=True, with_joker=True,
                       with_buchholz=True, with_goal_avg=True):
    """Return the per-player statistics of a single save file.

    Used by the frontend to stream the history edition by edition instead of
    waiting for every file to be parsed.
    """
    path = Path(save_dir) / filename
    trn = load_tournament(path)
    if trn is None:
        return None
    year = _year_of(trn, str(path))
    ranking = _ranking_of(trn, with_wins, with_joker, with_buchholz, with_goal_avg)
    players = []
    for team in trn.teams():
        rank = ranking.get(team)
        for player in team.players():
            players.append(
                {
                    "name": _player_name(player),
                    "firstname": player.firstname,
                    "lastname": player.lastname,
                    "team": team.id,
                    "rank": rank,
                    "wins": team.wins(),
                    "points": team.points(),
                }
            )
    return {
        "filename": Path(path).name,
        "year": year,
        "nb_teams": trn.nb_teams(),
        "nb_rounds": trn.nb_rounds(),
        "players": players,
    }


def player_detail(save_dir, name, with_wins=True, with_joker=True, with_buchholz=True, with_goal_avg=True):
    """Return the year-by-year detail of a single player, or ``None``."""
    detail = None
    for path, trn in _iter_tournaments(save_dir):
        year = _year_of(trn, path)
        ranking = _ranking_of(trn, with_wins, with_joker, with_buchholz, with_goal_avg)
        for team in trn.teams():
            for player in team.players():
                if _player_name(player) == name:
                    if detail is None:
                        detail = {"name": name, "editions": []}
                    detail["editions"].append(
                        {
                            "year": year,
                            "team": team.id,
                            "rank": ranking.get(team),
                            "wins": team.wins(),
                            "points": team.points(),
                        }
                    )
    return detail
