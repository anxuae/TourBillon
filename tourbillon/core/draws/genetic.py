# -*- coding: UTF-8 -*-

"""Genetic draw applying the Swiss-system rules.

A heuristic search used when the solution space is too large for an exhaustive
approach. A population of candidate draws evolves through selection, crossover
and mutation. The fitness rewards balanced matches (small point spread) and
penalizes rule violations (rematches, disparity above ``max_disparity``).

The search is seeded so the result is reproducible in tests. If the best
candidate still violates the hard constraints, :class:`DrawImpossibleError` is
raised.
"""

import asyncio
import random

from . import common
from ..exception import DrawImpossibleError

NAME = "genetic"
DESCRIPTION = "Genetic Swiss pairing (population based heuristic)"
DEFAULT = {
    "max_disparity": 2,
    "allow_rematch": False,
    "win_weight": 100,
    "population": 60,
    "generations": 500,
    "crossover_rate": 0.9,
    "mutation_rate": 0.2,
    "seed": None,
    "rematch_penalty": 100000,
    "disparity_penalty": 100000,
}


def _chunk(order, teams_by_match):
    """Split an ordered list of team numbers into matches."""
    return [order[i:i + teams_by_match] for i in range(0, len(order), teams_by_match)]


def _fitness(draw, stats, max_disparity, allow_rematch, cfg):
    """Return the fitness of a draw (lower is better)."""
    win_weight = float(cfg["win_weight"])
    score = 0.0
    for match in draw:
        # Combined strength (wins first, then points) mirrors the deterministic
        # draw: a match is better when its teams are close in strength.
        strength = [
            stats[num][common.cst.STAT_POINTS] + win_weight * common.wins(stats[num])
            for num in match
        ]
        score += max(strength) - min(strength)
        if common.disparity(stats, match) > max_disparity:
            score += cfg["disparity_penalty"]
        if not allow_rematch:
            score += cfg["rematch_penalty"] * common.rematch_pairs(stats, match)
    return score


def _is_valid(draw, stats, max_disparity, allow_rematch):
    return all(
        common.is_match_valid(stats, match, max_disparity, allow_rematch)
        for match in draw
    )


def _search(stats, teams_by_match, max_disparity, allow_rematch, cfg):
    """Run the genetic search (CPU-bound, executed in a worker thread)."""
    rng = random.Random(cfg["seed"])
    population_size = int(cfg["population"])
    generations = int(cfg["generations"])
    crossover_rate = float(cfg["crossover_rate"])
    mutation_rate = float(cfg["mutation_rate"])

    # Seed the population with the strength ordering plus random shuffles.
    base = common.order_by_strength(stats)
    population = [list(base)]
    for _ in range(population_size - 1):
        individual = list(base)
        rng.shuffle(individual)
        population.append(individual)

    def parametrized_fitness(individual):
        return _fitness(_chunk(individual, teams_by_match), stats,
                        max_disparity, allow_rematch, cfg)

    for _ in range(generations):
        population.sort(key=parametrized_fitness)
        if parametrized_fitness(population[0]) == 0.0:
            break

        # Elitism: keep the best half, breed the rest.
        survivors = population[: max(2, population_size // 2)]
        children = []
        while len(survivors) + len(children) < population_size:
            parent_a = rng.choice(survivors)
            parent_b = rng.choice(survivors)
            # Crossover happens only with probability ``crossover_rate``;
            # otherwise the child is a direct copy of a parent.
            if rng.random() < crossover_rate:
                child = _crossover(parent_a, parent_b, rng)
            else:
                child = list(parent_a)
            if rng.random() < mutation_rate:
                _mutate(child, rng)
            children.append(child)
        population = survivors + children

    population.sort(key=parametrized_fitness)
    best = population[0]
    return _chunk(best, teams_by_match)


def _crossover(parent_a, parent_b, rng):
    """Order crossover (OX) preserving a valid permutation of team numbers."""
    size = len(parent_a)
    if size < 2:
        return list(parent_a)
    start, end = sorted(rng.sample(range(size), 2))
    child = [None] * size
    child[start:end] = parent_a[start:end]
    taken = set(parent_a[start:end])
    fill = [num for num in parent_b if num not in taken]
    idx = 0
    for i in range(size):
        if child[i] is None:
            child[i] = fill[idx]
            idx += 1
    return child


def _mutate(individual, rng):
    """Swap two teams in place."""
    if len(individual) < 2:
        return
    i, j = rng.sample(range(len(individual)), 2)
    individual[i], individual[j] = individual[j], individual[i]


async def generate_draw(teams_by_match, stats, bye_teams=(), config=None, on_progress=None):
    """Generate a Swiss draw using a genetic heuristic.

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

    playing = {num: stats[num] for num in stats if num not in set(bye_teams)}

    if on_progress:
        await on_progress(10.0, "Evolving candidate draws")

    draw = await asyncio.to_thread(
        _search, playing, teams_by_match, max_disparity, allow_rematch, cfg
    )

    if not _is_valid(draw, playing, max_disparity, allow_rematch):
        raise DrawImpossibleError(
            "No valid pairing found. Increase 'max_disparity' or allow rematches."
        )

    matches = sorted(sorted(match) for match in draw)

    if on_progress:
        await on_progress(100.0, "Draw completed")

    return matches
