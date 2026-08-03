# -*- coding: UTF-8 -*-

"""Deterministic draw applying the Swiss-system rules.

Teams are paired by similar strength (wins then points). The algorithm builds a
pairwise cost matrix (accelerated with :mod:`numpy`) and then derives a valid
pairing through a deterministic backtracking search. The following constraints
are enforced:

* two teams do not meet twice (unless ``allow_rematch`` is set);
* the win gap inside a match never exceeds ``max_disparity``.

If no valid pairing exists, :class:`DrawImpossibleError` is raised so the
operator can increase ``max_disparity`` (or allow rematches).
"""

import asyncio
from itertools import combinations

import numpy as np

from . import common
from ..exception import DrawImpossibleError

NAME = "deterministic"
DESCRIPTION = "Deterministic Swiss pairing (cost matrix + backtracking)"
DEFAULT = {
    "max_disparity": 1,
    "allow_rematch": False,
    "win_weight": 1000,
}


def _cost_vector(stats, teams, win_weight):
    """Return a numpy strength vector aligned with ``teams`` (weakest first)."""
    points = np.array([stats[num][common.cst.STAT_POINTS] for num in teams], dtype=float)
    wins = np.array([common.wins(stats[num]) for num in teams], dtype=float)
    return points + win_weight * wins


def _build(order, stats, teams_by_match, max_disparity, allow_rematch):
    """Backtracking search returning a list of valid matches or ``None``.

    ``order`` is the list of team numbers sorted from the weakest to the
    strongest so that the weakest teams are paired first (they have the fewest
    valid partners).
    """
    if not order:
        return []

    anchor = order[0]
    rest = order[1:]

    # Try every combination of partners for the anchor team, closest in
    # strength first (i.e. following the ``order`` sequence).
    for partners in combinations(rest, teams_by_match - 1):
        match = [anchor] + list(partners)
        if not common.is_match_valid(stats, match, max_disparity, allow_rematch):
            continue
        remaining = [num for num in rest if num not in partners]
        tail = _build(remaining, stats, teams_by_match, max_disparity, allow_rematch)
        if tail is not None:
            return [sorted(match)] + tail

    return None


async def generate_draw(teams_by_match, stats, bye_teams=(), config=None, on_progress=None):
    """Generate a deterministic Swiss draw.

    :param teams_by_match: number of teams gathered in a single match
    :param stats: statistics mapping (see :mod:`common`)
    :param bye_teams: teams already set as BYE (excluded from pairing)
    :param config: draw options (see ``DEFAULT``)
    :param on_progress: optional async callback ``async (percent, message)``
    :return: list of matches, each a sorted list of team numbers
    """
    cfg = dict(DEFAULT)
    if config:
        cfg.update(config)

    max_disparity = int(cfg["max_disparity"])
    allow_rematch = bool(cfg["allow_rematch"])
    win_weight = float(cfg["win_weight"])

    playing = {num: stats[num] for num in stats if num not in set(bye_teams)}

    if on_progress:
        await on_progress(5.0, "Building strength vector")

    # Order teams by strength; the weakest are paired first because they have
    # the fewest valid partners under the disparity constraint.
    order_strong = common.order_by_strength(playing)
    strength = _cost_vector(playing, order_strong, win_weight)
    # Weakest first (numpy argsort keeps the computation vectorized/fast).
    weakest_first = [order_strong[i] for i in np.argsort(strength, kind="stable")]

    if on_progress:
        await on_progress(30.0, "Searching for a valid pairing")

    # Run the CPU-bound backtracking off the event loop.
    matches = await asyncio.to_thread(
        _build, weakest_first, playing, teams_by_match, max_disparity, allow_rematch
    )

    if matches is None:
        raise DrawImpossibleError(
            "No valid pairing found. Increase 'max_disparity' or allow rematches."
        )

    matches.sort()

    if on_progress:
        await on_progress(100.0, "Draw completed")

    return matches
