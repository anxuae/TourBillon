# -*- coding: UTF-8 -*-

"""Unit tests for the async draw algorithms (deterministic, genetic, random)."""

import asyncio

import pytest

from tourbillon.core import cst, draws
from tourbillon.core.draws import common
from tourbillon.core.exception import DrawError, DrawImpossibleError


def make_stats(specs):
    """Build a ``stats`` mapping from a compact spec.

    :param specs: dict ``{team_number: (points, victories, byes)}``
    :return: statistics mapping compatible with the draws
    """
    stats = {}
    ordered = sorted(
        specs.items(),
        key=lambda kv: (kv[1][1] + kv[1][2], kv[1][0]),
        reverse=True,
    )
    ranking = {num: i + 1 for i, (num, _) in enumerate(ordered)}
    for num, (points, victories, byes) in specs.items():
        stats[num] = {
            cst.STAT_POINTS: points,
            cst.STAT_VICTOIRES: victories,
            cst.STAT_CHAPEAUX: byes,
            cst.STAT_ADVERSAIRES: [],
            cst.STAT_MANCHES: [],
            cst.STAT_PLACE: ranking[num],
        }
    return stats


@pytest.fixture
def stats_even():
    """8 teams, all distinct strengths, no history."""
    return make_stats({n: (n * 3, n % 4, 0) for n in range(1, 9)})


@pytest.fixture
def stats_odd():
    """7 teams (an odd number -> one BYE needed for pairs)."""
    return make_stats({n: (n * 3, n % 3, 0) for n in range(1, 8)})


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #

def test_registry_contains_three_draws():
    assert set(draws.DRAWS) == {"deterministic", "genetic", "random"}


def test_default_draw_is_deterministic():
    assert draws.DEFAULT_DRAW == "deterministic"


def test_available_metadata():
    meta = {d["name"]: d for d in draws.available()}
    assert set(meta) == {"deterministic", "genetic", "random"}
    for entry in meta.values():
        assert isinstance(entry["description"], str)
        assert isinstance(entry["default"], dict)


def test_default_config_is_a_copy():
    cfg = draws.default_config("deterministic")
    cfg["max_disparity"] = 999
    assert draws.default_config("deterministic")["max_disparity"] != 999


def test_generate_unknown_draw_raises():
    with pytest.raises(DrawError):
        asyncio.run(draws.generate("nope", 2, {}))


# --------------------------------------------------------------------------- #
# BYE selection
# --------------------------------------------------------------------------- #

def test_no_bye_when_even(stats_even):
    assert draws.select_bye_teams(stats_even, 2) == []


def test_one_bye_when_odd(stats_odd):
    byes = draws.select_bye_teams(stats_odd, 2)
    assert len(byes) == 1
    weakest = common.order_by_weakness(stats_odd)[0]
    assert byes[0] == weakest


def test_bye_prefers_teams_never_bye():
    # Team 1 is the weakest but already had a BYE; team 2 should be chosen.
    stats = make_stats({1: (0, 0, 1), 2: (1, 0, 0), 3: (10, 3, 0)})
    assert draws.select_bye_teams(stats, 2) == [2]


def test_forced_bye_validated():
    stats = make_stats({n: (n, 0, 0) for n in range(1, 4)})
    assert draws.select_bye_teams(stats, 2, forced=[3]) == [3]
    with pytest.raises(DrawError):
        draws.select_bye_teams(stats, 2, forced=[1, 2])  # wrong count
    with pytest.raises(DrawError):
        draws.select_bye_teams(stats, 2, forced=[99])  # unknown team


# --------------------------------------------------------------------------- #
# Common draw guarantees (parametrized over every algorithm)
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name", ["deterministic", "genetic", "random"])
async def test_draw_partitions_all_playing_teams(name, stats_even):
    matches = await draws.generate(name, 2, stats_even)
    flat = sorted(num for match in matches for num in match)
    assert flat == list(range(1, 9))
    assert all(len(match) == 2 for match in matches)


@pytest.mark.parametrize("name", ["deterministic", "genetic", "random"])
async def test_draw_excludes_bye_teams(name, stats_odd):
    byes = draws.select_bye_teams(stats_odd, 2)
    matches = await draws.generate(name, 2, stats_odd, bye_teams=byes)
    flat = sorted(num for match in matches for num in match)
    expected = sorted(n for n in stats_odd if n not in byes)
    assert flat == expected


@pytest.mark.parametrize("name", ["deterministic", "genetic", "random"])
async def test_progress_callback_called(name, stats_even):
    events = []

    async def on_progress(percent, message):
        events.append((percent, message))

    await draws.generate(name, 2, stats_even, on_progress=on_progress)
    assert events
    assert events[-1][0] == 100.0
    assert all(0.0 <= p <= 100.0 for p, _ in events)


# --------------------------------------------------------------------------- #
# Swiss rules (deterministic & genetic only)
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name", ["deterministic", "genetic"])
async def test_swiss_respects_max_disparity(name):
    # Two clusters: teams 1-4 with 0 wins, teams 5-8 with 3 wins.
    specs = {n: (n, 0, 0) for n in range(1, 5)}
    specs.update({n: (n * 5, 3, 0) for n in range(5, 9)})
    stats = make_stats(specs)

    matches = await draws.generate(name, 2, stats, config={"max_disparity": 0})
    for match in matches:
        assert common.disparity(stats, match) == 0


@pytest.mark.parametrize("name", ["deterministic", "genetic"])
async def test_swiss_avoids_rematch(name):
    stats = make_stats({n: (n, 1, 0) for n in range(1, 5)})
    # Teams 1 & 2 have already played together.
    stats[1][cst.STAT_ADVERSAIRES] = [2]
    stats[2][cst.STAT_ADVERSAIRES] = [1]
    stats[1][cst.STAT_MANCHES] = [[1, 2]]
    stats[2][cst.STAT_MANCHES] = [[1, 2]]

    matches = await draws.generate(name, 2, stats, config={"max_disparity": 2})
    assert [1, 2] not in matches


@pytest.mark.parametrize("name", ["deterministic", "genetic"])
async def test_swiss_impossible_raises(name):
    # 4 teams, all met each other already, rematch not allowed -> impossible.
    stats = make_stats({n: (n, 0, 0) for n in range(1, 5)})
    everyone = [1, 2, 3, 4]
    for n in everyone:
        stats[n][cst.STAT_ADVERSAIRES] = [x for x in everyone if x != n]
        stats[n][cst.STAT_MANCHES] = [sorted([n, x]) for x in everyone if x != n]
    with pytest.raises(DrawImpossibleError):
        await draws.generate(
            name, 2, stats, config={"max_disparity": 5, "allow_rematch": False}
        )


async def test_deterministic_is_reproducible(stats_even):
    a = await draws.generate("deterministic", 2, stats_even)
    b = await draws.generate("deterministic", 2, stats_even)
    assert a == b


async def test_genetic_is_reproducible_with_seed(stats_even):
    a = await draws.generate("genetic", 2, stats_even, config={"seed": 42})
    b = await draws.generate("genetic", 2, stats_even, config={"seed": 42})
    assert a == b


async def test_random_is_reproducible_with_seed(stats_even):
    a = await draws.generate("random", 2, stats_even, config={"seed": 7})
    b = await draws.generate("random", 2, stats_even, config={"seed": 7})
    assert a == b


# --------------------------------------------------------------------------- #
# Integration with a real loaded tournament
# --------------------------------------------------------------------------- #

async def test_draw_on_loaded_tournament(trb4e1j):
    stats = trb4e1j.statistiques()
    teams_by_match = trb4e1j.equipes_par_manche

    byes = draws.select_bye_teams(stats, teams_by_match)
    matches = await draws.generate(
        draws.DEFAULT_DRAW, teams_by_match, stats, bye_teams=byes
    )

    flat = sorted(num for match in matches for num in match)
    expected = sorted(n for n in stats if n not in byes)
    assert flat == expected
    assert all(len(match) == teams_by_match for match in matches)
