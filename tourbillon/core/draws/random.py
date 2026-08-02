# -*- coding: UTF-8 -*-

"""Random draw (does NOT apply the Swiss-system rules).

Teams are paired purely at random. Useful for tests, demos or a first round
where no history exists yet. The ``seed`` option makes the result reproducible.
"""

import random

NAME = "random"
DESCRIPTION = "Random pairing (no Swiss rules)"
DEFAULT = {
    "seed": None,
}


async def generate_draw(teams_by_match, stats, bye_teams=(), config=None, on_progress=None):
    """Generate a random draw ignoring the Swiss-system rules.

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

    rng = random.Random(cfg["seed"])

    if on_progress:
        await on_progress(20.0, "Shuffling teams")

    teams = [num for num in stats if num not in set(bye_teams)]
    rng.shuffle(teams)

    matches = [
        sorted(teams[i:i + teams_by_match])
        for i in range(0, len(teams), teams_by_match)
    ]
    matches.sort()

    if on_progress:
        await on_progress(100.0, "Draw completed")

    return matches
