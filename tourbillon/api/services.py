# -*- coding: UTF-8 -*-

"""Business orchestration between the core domain and the API layer.

This module bridges the (legacy, French) ``core`` package to the English DTOs
and handles persistence (YAML) and draw execution. It keeps ``core`` fully
independent from FastAPI.
"""

import os.path as osp
from datetime import datetime

from ..core import cst, tournament as core_tournament
from ..core import draws
from . import schemas


# --------------------------------------------------------------------------- #
# Tournament lifecycle
# --------------------------------------------------------------------------- #
def create_tournament(state, params):
    """Create a fresh tournament using the given (or default) parameters."""
    defaults = state.settings.new_tournament_defaults()
    trn = core_tournament.Tournament(
        teams_by_match=params.teams_by_match or defaults["teams_by_match"],
        points_by_match=params.points_by_match or defaults["points_by_match"],
        players_by_team=params.players_by_team or defaults["players_by_team"],
    )
    state.tournament = trn
    state.filename = None
    return trn


def load_tournament(state, filename):
    """Load a tournament from a YAML file (retro-compatible)."""
    trn = core_tournament.load(filename)
    state.tournament = trn
    state.filename = filename
    return trn


def save_tournament(state, filename=None):
    """Persist the current tournament to a YAML file."""
    trn = state.require_tournament()
    if filename is None:
        filename = state.filename
    if filename is None:
        name = f"tournament_{datetime.now():%Y-%m-%d_%H%M%S}.yml"
        filename = osp.join(state.settings.save_dir, name)
    core_tournament.dump(trn, filename)
    state.filename = filename
    return filename


def auto_save(state):
    """Persist the tournament if auto-save is enabled."""
    if state.settings.auto_save:
        save_tournament(state)


# --------------------------------------------------------------------------- #
# Serialization helpers
# --------------------------------------------------------------------------- #
def tournament_dto(state):
    """Return the current tournament as a :class:`schemas.TournamentDTO`."""
    trn = state.require_tournament()
    return schemas.TournamentDTO(
        status=trn.status,
        teams_by_match=trn.teams_by_match,
        points_by_match=trn.points_by_match,
        players_by_team=trn.players_by_team,
        nb_teams=trn.nb_teams(),
        nb_rounds=trn.nb_rounds(),
        filename=state.filename,
    )


def team_dto(team):
    """Return a :class:`schemas.TeamDTO` for a core team."""
    return schemas.TeamDTO(
        number=team.id,
        joker=team.joker,
        players=[
            schemas.PlayerDTO(firstname=p.firstname, lastname=p.lastname)
            for p in team.players()
        ],
        status=team.status,
        points=team.points(),
        wins=team.wins(),
        byes=team.byes(),
    )


def round_dto(trn, rnd):
    """Return a :class:`schemas.RoundDTO` for a core round."""
    matches = []
    for match in rnd.matches():
        points = {}
        location = None
        finished = True
        for num in match:
            result = trn.team(num).result(rnd.number)
            points[num] = result.points
            location = result.location
            if result.status == cst.MATCH_IN_PROGRESS:
                finished = False
        matches.append(
            schemas.MatchDTO(
                location=location,
                teams=list(match),
                points=points,
                finished=finished,
            )
        )
    byes = [team.id for team in rnd.byes()]
    return schemas.RoundDTO(
        number=rnd.number,
        status=rnd.status,
        matches=matches,
        byes=byes,
    )


def ranking_dto(trn):
    """Return the ranking as a list of :class:`schemas.RankEntryDTO`."""
    entries = []
    for team, rank in trn.ranking():
        entries.append(
            schemas.RankEntryDTO(
                rank=rank,
                team=team.id,
                wins=team.wins(),
                points=team.points(),
            )
        )
    return entries


# --------------------------------------------------------------------------- #
# Teams
# --------------------------------------------------------------------------- #
def list_teams(state):
    """Return every team of the current tournament as DTOs."""
    trn = state.require_tournament()
    return [team_dto(team) for team in sorted(trn.teams())]


def add_team(state, payload):
    """Register a new team (and its players)."""
    trn = state.require_tournament()
    team = trn.add_team(payload.number)
    for player in payload.players:
        team.add_player(player.firstname, player.lastname)
    auto_save(state)
    return team_dto(team)


def delete_team(state, number):
    """Remove a team from the current tournament."""
    trn = state.require_tournament()
    trn.remove_team(number)
    auto_save(state)


# --------------------------------------------------------------------------- #
# Rounds and draws
# --------------------------------------------------------------------------- #
def list_rounds(state):
    """Return every round of the current tournament as DTOs."""
    trn = state.require_tournament()
    return [round_dto(trn, rnd) for rnd in trn.rounds()]


def get_round(state, number):
    """Return a single round as a DTO."""
    trn = state.require_tournament()
    return round_dto(trn, trn.round(number))


async def create_round(state, request, on_progress=None):
    """Create a new round by running a draw and starting it.

    :param state: application state
    :param request: :class:`schemas.DrawRequest`
    :param on_progress: optional async callback ``async (percent, message)``
    :return: the created round as a DTO
    """
    trn = state.require_tournament()
    algorithm = request.algorithm or state.settings.default_draw

    stats = trn.statistics()
    byes = draws.select_bye_teams(stats, trn.teams_by_match, forced=request.bye_teams)

    # Effective options: algorithm defaults < saved user settings < request.
    config = state.settings.draw_config(algorithm)
    if request.config:
        config.update(request.config)

    matches = await draws.generate(
        algorithm,
        trn.teams_by_match,
        stats,
        bye_teams=byes,
        config=config,
        on_progress=on_progress,
    )

    rnd = trn.add_round()
    locations = trn.locations()
    match_map = {locations[i]: match for i, match in enumerate(matches)}
    rnd.start(match_map, byes=byes)
    auto_save(state)
    return round_dto(trn, rnd)


def set_match_result(state, round_number, result):
    """Register the score of a match in a round."""
    trn = state.require_tournament()
    rnd = trn.round(round_number)
    rnd.add_result({int(k): int(v) for k, v in result.points.items()}, datetime.now())
    auto_save(state)
    return round_dto(trn, rnd)


# --------------------------------------------------------------------------- #
# Draws metadata
# --------------------------------------------------------------------------- #
def list_draws(state):
    """Return the metadata of every available draw algorithm.

    Each entry exposes the algorithm's built-in ``default`` options and the
    effective ``config`` currently held by the settings.
    """
    infos = []
    for info in draws.available():
        info["config"] = state.settings.draw_config(info["name"])
        infos.append(schemas.DrawInfoDTO(**info))
    return infos


# --------------------------------------------------------------------------- #
# Settings
# --------------------------------------------------------------------------- #
def get_settings(state):
    """Return the current application settings as a plain dictionary."""
    return state.settings.as_dict()


def update_settings(state, values):
    """Update the application settings and persist them to disk.

    The update goes through the settings module (single source of truth):
    unknown keys are ignored and the ``draws`` section is merged per option.

    :param state: application state
    :param values: mapping of settings to update
    :return: the updated settings as a plain dictionary
    """
    state.settings.update(values)
    state.settings.save()
    return state.settings.as_dict()
