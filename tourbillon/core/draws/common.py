# -*- coding: UTF-8 -*-

"""Pure helper functions shared by the draw algorithms.

The ``stats`` mapping consumed by the draws is the one produced by
:meth:`tourbillon.core.tournament.Tournament.statistics`. Each entry is keyed
by the team number and holds the following fields (see ``core.cst``):

    {
        team_number: {
            cst.STAT_POINTS:     int,   # cumulated points
            cst.STAT_WINS:       int,   # number of wins
            cst.STAT_BYES:       int,   # number of byes (count as a win)
            cst.STAT_OPPONENTS:  list,  # opponents already met (team ids)
            cst.STAT_MATCHES:    list,  # matches already played (sorted team ids)
        },
        ...
    }

Only primitive Python types are used across this module.
"""

from itertools import combinations
import random

from .. import cst
from ..exception import DrawError


def bye_count(nb_teams, teams_by_match):
    """Return the number of teams that must be set as BYE for a round.

    :param nb_teams: number of registered teams
    :param teams_by_match: number of teams gathered in a single match
    """
    if teams_by_match < 2:
        raise DrawError("A match must gather at least 2 teams")
    if nb_teams < teams_by_match:
        raise DrawError(
            f"Not enough teams (teams: {nb_teams}, required per match: {teams_by_match})"
        )
    return nb_teams % teams_by_match


def wins(team_stats):
    """Return the number of wins of a team (match wins plus byes)."""
    return team_stats[cst.STAT_WINS] + team_stats[cst.STAT_BYES]


def order_by_strength(stats, weakest_first=False):
    """Return the team ids ordered:

    - from the strongest to the weakest if ``weakest_first`` is ``False`` (default), or
    - from the weakest to the strongest if ``weakest_first`` is ``True``.

    Teams are compared by:

    1) wins,
    2) points,
    3) truncated Buchholz,
    4) goal average,
    5) team id (to keep the result fully deterministic).

    ``stats`` entries that do not provide the optional tie-break fields are
    considered with a default value of ``0`` for those fields.
    """
    return sorted(
        stats.keys(),
        key=lambda num: (
            wins(stats[num]),
            stats[num][cst.STAT_POINTS],
            stats[num].get(cst.STAT_BUCHHOLZ, 0),
            stats[num].get(cst.STAT_GOAL_AVERAGE, 0),
            num,
        ),
        reverse=not weakest_first,
    )


def _prepare_bye_selection(stats, teams_by_match, forced=()):
    """Validate BYE selection inputs and normalize forced teams.

    :return: tuple ``(count, forced_or_none)`` where ``forced_or_none`` is
             ``None`` when no forced BYE is provided.
    """
    count = bye_count(len(stats), teams_by_match)
    forced = list(forced)

    if not forced:
        return count, None

    if len(forced) != count:
        raise DrawError(
            f"Wrong number of BYE teams (given: {len(forced)}, expected: {count})"
        )
    for num in forced:
        if num not in stats:
            raise DrawError(f"Unknown BYE team n°{num}")
    return count, sorted(forced)


def select_bye_teams(stats, teams_by_match, forced=()):
    """Return the list of team ids to set as BYE for the next round.

    The number of BYEs per team is minimized: teams that were BYE the fewest
    times are chosen first (weakest first to break ties). A team is therefore
    only picked again once every other team has been BYE at least as often. If
    some teams are given through ``forced`` they are used as-is (after
    validation).

    :param stats: statistics mapping (see module docstring)
    :param teams_by_match: number of teams gathered in a single match
    :param forced: optional list of team ids to force as BYE
    """
    count, forced_teams = _prepare_bye_selection(stats, teams_by_match, forced=forced)

    if forced_teams is not None:
        return forced_teams

    if count == 0:
        return []

    # Minimize the number of BYEs per team: pick teams with the fewest BYEs
    # first, weakest first to break ties. A team already BYE is only chosen
    # again once every remaining team has been BYE at least as often.
    candidates = order_by_strength(stats, weakest_first=True)
    ordered = sorted(candidates, key=lambda num: stats[num][cst.STAT_BYES])

    return sorted(ordered[:count])


def select_bye_teams_random(stats, teams_by_match, forced=(), seed=None):
    """Return the list of team ids to set as BYE using random selection.

    If ``forced`` is provided, validation and output are identical to
    :func:`select_bye_teams`.

    :param stats: statistics mapping (see module docstring)
    :param teams_by_match: number of teams gathered in a single match
    :param forced: optional list of team ids to force as BYE
    :param seed: optional random seed
    """
    count, forced_teams = _prepare_bye_selection(stats, teams_by_match, forced=forced)

    if forced_teams is not None:
        return forced_teams

    if count == 0:
        return []

    rng = random.Random(seed)
    pool = list(stats.keys())
    selected = []

    while len(selected) < count:
        min_byes = min(stats[num][cst.STAT_BYES] for num in pool)
        tier = [num for num in pool if stats[num][cst.STAT_BYES] == min_byes]
        remaining = count - len(selected)
        if len(tier) <= remaining:
            picked = tier
        else:
            picked = rng.sample(tier, remaining)
        selected.extend(picked)
        pool = [num for num in pool if num not in picked]

    return sorted(selected)


def has_already_played(stats, match):
    """Return ``True`` if the exact match was already played by these teams."""
    match = sorted(match)
    for num in match:
        if match in stats[num][cst.STAT_MATCHES]:
            return True
    return False


def rematch_pairs(stats, match):
    """Return the number of pairwise encounters already played within a match."""
    count = 0
    for a, b in combinations(sorted(match), 2):
        count += stats[b][cst.STAT_OPPONENTS].count(a)
    return count


def disparity(stats, match):
    """Return the win gap between the strongest and weakest team of a match."""
    values = [wins(stats[num]) for num in match]
    return max(values) - min(values)


def is_match_valid(stats, match, max_disparity, allow_rematch):
    """Return ``True`` if a match satisfies the Swiss constraints."""
    if not allow_rematch and has_already_played(stats, match):
        return False
    if disparity(stats, match) > max_disparity:
        return False
    return True
