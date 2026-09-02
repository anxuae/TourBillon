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
import unicodedata
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


def _fold_accents(text):
    """Return ``text`` without any diacritic (``é`` -> ``e``)."""
    decomposed = unicodedata.normalize("NFD", text or "")
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _capitalize(text):
    """Return ``text`` with each word starting with a capital letter.

    Names are typed by hand, so casing is unreliable. ``str.title()`` is not
    used because it lowercases letters after an apostrophe or a dash, which
    would break names such as ``O'Brien`` or ``Jean-Luc``.
    """
    text = " ".join((text or "").split())
    if not text:
        return ""
    result = []
    capitalize_next = True
    for char in text:
        result.append(char.upper() if capitalize_next else char.lower())
        capitalize_next = char in " -'"
    return "".join(result)


def _player_parts(player):
    """Return the ``(firstname, lastname)`` of a player, nicely capitalized."""
    return _capitalize(player.firstname), _capitalize(player.lastname)


def _player_name(player):
    """Return a stable display name for a player (capitalized, spaces folded)."""
    firstname, lastname = _player_parts(player)
    return f"{firstname} {lastname}".strip()


def _player_key(player):
    """Return the key used to merge duplicated entries.

    Ignores both the case and the accents so hand-typed variants such as
    ``Jose Gomez``, ``José Gómez`` and ``JOSE GOMEZ`` map to a single player.
    """
    return _fold_accents(_player_name(player)).casefold()


def _better_name(current, candidate):
    """Return the nicest of two spellings of the same name.

    Accented spellings are assumed to be the correct ones, so they win over
    their plain ASCII counterpart.
    """
    if not current:
        return candidate
    current_accents = current != _fold_accents(current)
    candidate_accents = candidate != _fold_accents(candidate)
    if candidate_accents and not current_accents:
        return candidate
    return current


def aggregate_players(save_dir, with_wins=True, with_joker=True, with_buchholz=True, with_goal_avg=True):
    """Return aggregated statistics per player across every edition.

    Entries are merged ignoring the case and the accents, so hand-typed
    variants such as ``jean DUPONT``, ``Jean Dupont`` and ``Jean Dupont`` count
    as a single player. The exposed name is the nicest spelling seen.
    """
    players = {}
    for path, trn in _iter_tournaments(save_dir):
        year = _year_of(trn, path)
        ranking = _ranking_of(trn, with_wins, with_joker, with_buchholz, with_goal_avg)
        for team in trn.teams():
            rank = ranking.get(team)
            for player in team.players():
                key = _player_key(player)
                if not key:
                    continue
                firstname, lastname = _player_parts(player)
                entry = players.setdefault(
                    key,
                    {"name": _player_name(player), "firstname": firstname,
                     "lastname": lastname, "participations": 0,
                     "wins": 0, "points": 0, "best_rank": None, "years": []},
                )
                entry["participations"] += 1
                entry["wins"] += team.wins()
                entry["points"] += team.points()
                # Keep the nicest spelling seen across the editions
                entry["firstname"] = _better_name(entry["firstname"], firstname)
                entry["lastname"] = _better_name(entry["lastname"], lastname)
                entry["name"] = f"{entry['firstname']} {entry['lastname']}".strip()
                if rank is not None:
                    if entry["best_rank"] is None or rank < entry["best_rank"]:
                        entry["best_rank"] = rank
                entry["years"].append(year)
    return sorted(players.values(), key=lambda e: e["name"])


def tournament_players(save_dir, filename, with_wins=True, with_joker=True,
                       with_buchholz=True, with_goal_avg=True):
    """Return the per-player statistics of a single save file.

    Used by the frontend to stream the history edition by edition instead of
    waiting for every file to be parsed. Names are capitalized so the frontend
    can merge them case-insensitively.
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
            firstname, lastname = _player_parts(player)
            players.append(
                {
                    "name": _player_name(player),
                    "firstname": firstname,
                    "lastname": lastname,
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
    """Return the year-by-year detail of a single player, or ``None``.

    The lookup ignores the case and the accents so a player typed differently
    across the editions is still found as a single person. Each edition keeps
    the ``raw_name`` exactly as stored in the save file, which makes wrong
    merges visible to the operator.
    """
    detail = None
    wanted = _fold_accents(_capitalize(name)).casefold()
    for path, trn in _iter_tournaments(save_dir):
        year = _year_of(trn, path)
        ranking = _ranking_of(trn, with_wins, with_joker, with_buchholz, with_goal_avg)
        for team in trn.teams():
            for player in team.players():
                if _player_key(player) == wanted:
                    if detail is None:
                        detail = {"name": _player_name(player), "editions": []}
                    else:
                        detail["name"] = _better_name(detail["name"], _player_name(player))
                    detail["editions"].append(
                        {
                            "year": year,
                            "team": team.id,
                            "rank": ranking.get(team),
                            "wins": team.wins(),
                            "points": team.points(),
                            # Untouched spelling found in the save file
                            "raw_name": f"{player.firstname} {player.lastname}".strip(),
                            "raw_firstname": player.firstname,
                            "raw_lastname": player.lastname,
                        }
                    )
    return detail
