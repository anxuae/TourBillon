# -*- coding: UTF-8 -*-

"""Cross-tournament history aggregation.

Loads every save file from the save directory (retro-compatible with the legacy
YAML files) and computes per-player statistics across the editions.
"""

from pathlib import Path

from ..core import tournament as core_tournament


def _iter_save_files(save_dir):
    """Yield every tournament save file path found in ``save_dir``."""
    save_dir = Path(save_dir)
    for pattern in ("*.yml", "*.trb"):
        yield from sorted(str(p) for p in save_dir.glob(pattern))


def _year_of(trn, path):
    """Return the tournament year (from its start date, else the filename)."""
    try:
        return trn.start_date.year
    except Exception:
        return Path(path).stem


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
    for path in _iter_save_files(save_dir):
        try:
            trn = core_tournament.load(path)
        except Exception:
            continue
        year = _year_of(trn, path)
        ranking = dict(
            trn.ranking(
                with_wins=with_wins,
                with_joker=with_joker,
                with_buchholz=with_buchholz,
                with_goal_avg=with_goal_avg,
            )
        )
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


def player_detail(save_dir, name, with_wins=True, with_joker=True, with_buchholz=True, with_goal_avg=True):
    """Return the year-by-year detail of a single player, or ``None``."""
    detail = None
    for path in _iter_save_files(save_dir):
        try:
            trn = core_tournament.load(path)
        except Exception:
            continue
        year = _year_of(trn, path)
        ranking = dict(
            trn.ranking(
                with_wins=with_wins,
                with_joker=with_joker,
                with_buchholz=with_buchholz,
                with_goal_avg=with_goal_avg,
            )
        )
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
