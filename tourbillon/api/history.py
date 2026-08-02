# -*- coding: UTF-8 -*-

"""Cross-tournament history aggregation.

Loads every save file from the save directory (retro-compatible with the legacy
YAML files) and computes per-player statistics across the editions.
"""

import glob
import os.path as osp

from ..core import tournament as core_tournament


def _iter_save_files(save_dir):
    """Yield every tournament save file path found in ``save_dir``."""
    for pattern in ("*.yml", "*.trb"):
        yield from sorted(glob.glob(osp.join(save_dir, pattern)))


def _year_of(trn, path):
    """Return the tournament year (from its start date, else the filename)."""
    try:
        return trn.debut.year
    except Exception:
        return osp.splitext(osp.basename(path))[0]


def list_tournaments(save_dir):
    """Return metadata for every save file (sorted by year)."""
    result = []
    for path in _iter_save_files(save_dir):
        try:
            trn = core_tournament.load(path)
        except Exception:
            continue
        result.append(
            {
                "filename": osp.basename(path),
                "year": _year_of(trn, path),
                "nb_teams": trn.nb_equipes(),
                "nb_rounds": trn.nb_parties(),
            }
        )
    return result


def _player_name(player):
    """Return a stable display name for a player."""
    return f"{player.prenom} {player.nom}".strip()


def aggregate_players(save_dir):
    """Return aggregated statistics per player across every edition."""
    players = {}
    for path in _iter_save_files(save_dir):
        try:
            trn = core_tournament.load(path)
        except Exception:
            continue
        year = _year_of(trn, path)
        ranking = dict(trn.classement())
        for team in trn.equipes():
            place = ranking.get(team)
            for player in team.joueurs():
                name = _player_name(player)
                entry = players.setdefault(
                    name,
                    {"name": name, "participations": 0, "victories": 0,
                     "points": 0, "best_place": None, "years": []},
                )
                entry["participations"] += 1
                entry["victories"] += team.victoires()
                entry["points"] += team.points()
                if place is not None:
                    if entry["best_place"] is None or place < entry["best_place"]:
                        entry["best_place"] = place
                entry["years"].append(year)
    return sorted(players.values(), key=lambda e: e["name"])


def player_detail(save_dir, name):
    """Return the year-by-year detail of a single player, or ``None``."""
    detail = None
    for path in _iter_save_files(save_dir):
        try:
            trn = core_tournament.load(path)
        except Exception:
            continue
        year = _year_of(trn, path)
        ranking = dict(trn.classement())
        for team in trn.equipes():
            for player in team.joueurs():
                if _player_name(player) == name:
                    if detail is None:
                        detail = {"name": name, "editions": []}
                    detail["editions"].append(
                        {
                            "year": year,
                            "team": team.numero,
                            "place": ranking.get(team),
                            "victories": team.victoires(),
                            "points": team.points(),
                        }
                    )
    return detail
