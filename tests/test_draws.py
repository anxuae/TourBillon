# -*- coding: UTF-8 -*-

"""Unit tests for the async draw algorithms (deterministic, genetic, random)."""

import asyncio

import pytest

from conftest import make_stats
from tourbillon.core import cst, draws
from tourbillon.core.draws import common
from tourbillon.core.exception import DrawError, DrawImpossibleError


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
    weakest = common.order_by_strength(stats_odd, weakest_first=True)[0]
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


def test_bye_minimizes_count_per_team():
    # Teams 1 and 2 already had a BYE, team 3 never did: team 3 is picked
    # even though it is the strongest, to minimize BYEs per team.
    stats = make_stats({1: (0, 0, 1), 2: (1, 0, 1), 3: (10, 3, 0)})
    assert draws.select_bye_teams(stats, 2) == [3]


def test_bye_reused_only_when_all_already_bye():
    # Every team has been BYE once: pick again, weakest first.
    stats = make_stats({1: (0, 0, 1), 2: (1, 0, 1), 3: (10, 3, 1)})
    weakest = common.order_by_strength(stats, weakest_first=True)[0]
    assert draws.select_bye_teams(stats, 2) == [weakest]


def test_bye_first_round_tie_picks_lowest_team_id():
    # No round played yet: every team has identical stats, tie-break uses team id.
    stats = make_stats({1: (0, 0, 0), 2: (0, 0, 0), 3: (0, 0, 0)})
    assert draws.select_bye_teams(stats, 2) == [1]


def test_bye_random_algorithm_uses_seeded_randomness():
    stats = make_stats({1: (0, 0, 0), 2: (0, 0, 0), 3: (0, 0, 0)})
    byes_a = draws.select_bye_teams(stats, 2, algorithm="random", config={"seed": 1})
    byes_b = draws.select_bye_teams(stats, 2, algorithm="random", config={"seed": 1})
    byes_c = draws.select_bye_teams(stats, 2, algorithm="random", config={"seed": 5})
    assert byes_a == byes_b
    assert byes_a != byes_c


def test_bye_random_algorithm_can_differ_from_deterministic():
    stats = make_stats({1: (0, 0, 0), 2: (0, 0, 0), 3: (0, 0, 0)})
    deterministic_bye = draws.select_bye_teams(stats, 2)
    random_bye = draws.select_bye_teams(stats, 2, algorithm="random", config={"seed": 0})
    assert deterministic_bye == [1]
    assert random_bye != deterministic_bye


def test_bye_random_prefers_lowest_bye_count():
    stats = make_stats({1: (0, 0, 2), 2: (0, 0, 0), 3: (0, 0, 0)})
    byes = draws.select_bye_teams(stats, 2, algorithm="random", config={"seed": 1})
    assert byes[0] in [2, 3]


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
    stats[1][cst.STAT_OPPONENTS] = [2]
    stats[2][cst.STAT_OPPONENTS] = [1]
    stats[1][cst.STAT_MATCHES] = [[1, 2]]
    stats[2][cst.STAT_MATCHES] = [[1, 2]]

    matches = await draws.generate(name, 2, stats, config={"max_disparity": 2})
    assert [1, 2] not in matches


@pytest.mark.parametrize("name", ["deterministic", "genetic"])
async def test_swiss_impossible_raises(name):
    # 4 teams, all met each other already, rematch not allowed -> impossible.
    stats = make_stats({n: (n, 0, 0) for n in range(1, 5)})
    everyone = [1, 2, 3, 4]
    for n in everyone:
        stats[n][cst.STAT_OPPONENTS] = [x for x in everyone if x != n]
        stats[n][cst.STAT_MATCHES] = [sorted([n, x]) for x in everyone if x != n]
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
    stats = trb4e1j.statistics()
    teams_by_match = trb4e1j.teams_by_match

    byes = draws.select_bye_teams(stats, teams_by_match)
    matches = await draws.generate(
        draws.DEFAULT_DRAW, teams_by_match, stats, bye_teams=byes
    )

    flat = sorted(num for match in matches for num in match)
    expected = sorted(n for n in stats if n not in byes)
    assert flat == expected
    assert all(len(match) == teams_by_match for match in matches)


# --------------------------------------------------------------------------- #
# Deterministic replay of a real tournament, round after round
# --------------------------------------------------------------------------- #
#
# We cannot expect the deterministic draw to reproduce the *exact* historical
# opponents: the first round of the archived tournament was drawn at random
# (no history, every team equal) and the legacy pairing algorithm differs from
# the current one. So we skip the first round and replay from round 2 onwards.
# What we *can* guarantee is that, when fed with the real
# statistics accumulated before each round, the deterministic draw:
#   * pairs every playing team exactly once (complete partition),
#   * never rematches teams that already met in the real tournament,
#   * keeps the win disparity of each match within the configured limit,
#   * is reproducible: the very same statistics always yield the very same
#     opponents.

async def test_deterministic_replays_real_tournament(trb4e1j):
    teams_by_match = trb4e1j.teams_by_match
    max_disparity = draws.default_config("deterministic")["max_disparity"]

    # Skip the first round: it was drawn at random (no history, every team
    # equal), so it cannot be reproduced deterministically. Replay from round 2.
    for number in range(2, trb4e1j.nb_rounds() + 1):
        played = trb4e1j.round(number)

        # Statistics as they stood *before* this round was drawn.
        stats = trb4e1j.statistics(round_limit=number - 1)
        forced_byes = sorted(team.id for team in played.byes())
        byes = draws.select_bye_teams(stats, teams_by_match, forced=forced_byes)

        matches = await draws.generate(
            "deterministic", teams_by_match, stats, bye_teams=byes
        )

        # Complete partition of every playing team.
        flat = sorted(num for match in matches for num in match)
        expected = sorted(num for num in stats if num not in byes)
        assert flat == expected
        assert all(len(match) == teams_by_match for match in matches)

        # No rematch against the real accumulated history.
        for match in matches:
            assert not common.has_already_played(stats, match)

        # Win disparity kept within the configured limit.
        for match in matches:
            assert common.disparity(stats, match) <= max_disparity

        # Same statistics -> same opponents (deterministic and reproducible).
        again = await draws.generate(
            "deterministic", teams_by_match, stats, bye_teams=byes
        )
        assert matches == again

