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

from . import common
from ..exception import DrawImpossibleError

NAME = "deterministic"
DESCRIPTION = "Deterministic Swiss pairing (cost matrix + backtracking)"
DEFAULT = {
    "max_disparity": 2,
    "allow_rematch": False,
    "win_weight": 100,
}


def _build(order, stats, teams_by_match, max_disparity, allow_rematch, tracker=None):
    """Backtracking search returning a list of valid matches or ``None``.

    ``order`` is the list of team numbers sorted from the weakest to the
    strongest so that the weakest teams are paired first (they have the fewest
    valid partners).

    ``tracker`` is an optional callable invoked with the number of teams still
    to pair, used to report progress.
    """
    if tracker:
        tracker(len(order))

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
        tail = _build(remaining, stats, teams_by_match, max_disparity, allow_rematch, tracker)
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

    report = common.progress_reporter(on_progress)
    report(5.0, "Building strength vector", force=True)

    # Order teams by strength; the weakest are paired first because they have
    # the fewest valid partners under the disparity constraint.
    order_weakest = common.order_by_strength(playing, weakest_first=True)

    report(30.0, "Searching for a valid pairing", force=True)

    total = len(order_weakest)
    # Backtracking has no monotonic counter, so report the deepest pairing ever
    # reached: it never goes backwards when the search unwinds.
    deepest = {'paired': 0}

    def tracker(remaining):
        paired = total - remaining
        if total <= 0 or paired <= deepest['paired']:
            return
        deepest['paired'] = paired
        report(
            30.0 + 65.0 * paired / total,
            f"Pairing teams ({paired}/{total})",
        )

    # Run the CPU-bound backtracking off the event loop.
    matches = await asyncio.to_thread(
        _build, order_weakest, playing, teams_by_match, max_disparity, allow_rematch, tracker
    )

    if matches is None:
        raise DrawImpossibleError(
            "No valid pairing found. Increase 'max_disparity' or allow rematches."
        )

    matches.sort()

    # Let the reports scheduled from the worker thread run before the final one,
    # so progress is always delivered in increasing order.
    await asyncio.sleep(0)
    if on_progress:
        await on_progress(100.0, "Draw completed")

    return matches
