# -*- coding: UTF-8 -*-

"""Draw algorithms registry.

Each draw is a module exposing:

* ``NAME`` (str): unique identifier of the algorithm;
* ``DESCRIPTION`` (str): short human readable description;
* ``DEFAULT`` (dict): default configuration options;
* ``generate_draw`` (coroutine): the async pairing function.

All algorithms share the same signature::

    async def generate_draw(teams_by_match, stats, bye_teams=(),
                            config=None, on_progress=None) -> list

They return a list of matches, each match being a sorted list of team numbers.
The ``deterministic`` and ``genetic`` draws enforce the Swiss-system rules
(no rematch, ``max_disparity`` limit); ``random`` ignores them.
"""

from . import common, deterministic, genetic, random
from ..exception import DrawError, DrawImpossibleError

MODULES = (deterministic, genetic, random)

# Registry: draw name -> module.
DRAWS = {module.NAME: module for module in MODULES}

# Default algorithm (deterministic and reproducible).
DEFAULT_DRAW = deterministic.NAME


def available():
    """Return the metadata of every registered draw.

    :return: list of dict ``{name, description, default}``
    """
    return [
        {
            "name": module.NAME,
            "description": module.DESCRIPTION,
            "default": dict(module.DEFAULT),
        }
        for module in MODULES
    ]


def default_config(name):
    """Return a copy of the default configuration of a draw."""
    if name not in DRAWS:
        raise DrawError(f"Unknown draw name '{name}'")
    return dict(DRAWS[name].DEFAULT)


async def generate(name, teams_by_match, stats, bye_teams=(), config=None, on_progress=None):
    """Run the draw ``name`` and return the list of generated matches.

    :param name: algorithm identifier (see :data:`DRAWS`)
    :param teams_by_match: number of teams gathered in a single match
    :param stats: statistics mapping (see :mod:`common`)
    :param bye_teams: teams already set as BYE (excluded from pairing)
    :param config: draw options (merged over the algorithm defaults)
    :param on_progress: optional async callback ``async (percent, message)``
    :return: list of matches, each a sorted list of team numbers
    """
    if name not in DRAWS:
        raise DrawError(f"Unknown draw name '{name}'")
    return await DRAWS[name].generate_draw(
        teams_by_match, stats, bye_teams=bye_teams, config=config, on_progress=on_progress
    )


def select_bye_teams(stats, teams_by_match, forced=(), algorithm=None, config=None):
    """Return the team numbers to set as BYE for the next round.

    Convenience re-export of :func:`common.select_bye_teams`.
    """
    if algorithm == random.NAME:
        seed = None
        if isinstance(config, dict):
            seed = config.get("seed")
        return common.select_bye_teams_random(
            stats,
            teams_by_match,
            forced=forced,
            seed=seed,
        )
    return common.select_bye_teams(stats, teams_by_match, forced=forced)
