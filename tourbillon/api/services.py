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

# Status translation (legacy French constants -> stable English API values).
_TOURNAMENT_STATUS = {
    cst.T_INSCRIPTION: "registration",
    cst.T_ATTEND_TIRAGE: "awaiting_draw",
    cst.T_PARTIE_EN_COURS: "round_in_progress",
}
_ROUND_STATUS = {
    cst.P_ATTEND_TIRAGE: "awaiting_draw",
    cst.P_EN_COURS: "in_progress",
    cst.P_COMPLETE: "complete",
    cst.P_TERMINEE: "finished",
}
_TEAM_STATUS = {
    cst.E_INCOMPLETE: "incomplete",
    cst.E_ATTEND_TIRAGE: "awaiting_draw",
    cst.E_EN_COURS: "in_progress",
}


# --------------------------------------------------------------------------- #
# Tournament lifecycle
# --------------------------------------------------------------------------- #
def create_tournament(state, params):
    """Create a fresh tournament using the given (or default) parameters."""
    defaults = state.settings.new_tournament_defaults()
    trn = core_tournament.Tournament(
        equipes_par_manche=params.teams_by_match or defaults["teams_by_match"],
        points_par_manche=params.points_by_match or defaults["points_by_match"],
        joueurs_par_equipe=params.players_by_team or defaults["players_by_team"],
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
        status=_TOURNAMENT_STATUS.get(trn.statut, trn.statut),
        teams_by_match=trn.equipes_par_manche,
        points_by_match=trn.points_par_manche,
        players_by_team=trn.joueurs_par_equipe,
        nb_teams=trn.nb_equipes(),
        nb_rounds=trn.nb_parties(),
        filename=state.filename,
    )


def team_dto(team):
    """Return a :class:`schemas.TeamDTO` for a core team."""
    return schemas.TeamDTO(
        number=team.numero,
        joker=team.joker,
        players=[
            schemas.PlayerDTO(firstname=p.prenom, lastname=p.nom)
            for p in team.joueurs()
        ],
        status=_TEAM_STATUS.get(team.statut, team.statut),
        points=team.points(),
        victories=team.victoires(),
        byes=team.chapeaux(),
    )


def round_dto(trn, rnd):
    """Return a :class:`schemas.RoundDTO` for a core round."""
    matches = []
    for match in rnd.manches():
        points = {}
        location = None
        finished = True
        for num in match:
            result = trn.equipe(num).resultat(rnd.numero)
            points[num] = result.points
            location = result.location
            if result.statut == cst.M_EN_COURS:
                finished = False
        matches.append(
            schemas.MatchDTO(
                location=location,
                teams=list(match),
                points=points,
                finished=finished,
            )
        )
    byes = [team.numero for team in rnd.chapeaux()]
    return schemas.RoundDTO(
        number=rnd.numero,
        status=_ROUND_STATUS.get(rnd.statut, rnd.statut),
        matches=matches,
        byes=byes,
    )


def ranking_dto(trn):
    """Return the ranking as a list of :class:`schemas.RankEntryDTO`."""
    entries = []
    for team, place in trn.classement():
        entries.append(
            schemas.RankEntryDTO(
                place=place,
                team=team.numero,
                victories=team.victoires(),
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
    return [team_dto(team) for team in sorted(trn.equipes())]


def add_team(state, payload):
    """Register a new team (and its players)."""
    trn = state.require_tournament()
    team = trn.ajout_equipe(payload.number)
    for player in payload.players:
        team.ajout_joueur(player.firstname, player.lastname, trn.debut)
    auto_save(state)
    return team_dto(team)


def delete_team(state, number):
    """Remove a team from the current tournament."""
    trn = state.require_tournament()
    trn.suppr_equipe(number)
    auto_save(state)


# --------------------------------------------------------------------------- #
# Rounds and draws
# --------------------------------------------------------------------------- #
def list_rounds(state):
    """Return every round of the current tournament as DTOs."""
    trn = state.require_tournament()
    return [round_dto(trn, rnd) for rnd in trn.parties()]


def get_round(state, number):
    """Return a single round as a DTO."""
    trn = state.require_tournament()
    return round_dto(trn, trn.partie(number))


async def create_round(state, request, on_progress=None):
    """Create a new round by running a draw and starting it.

    :param state: application state
    :param request: :class:`schemas.DrawRequest`
    :param on_progress: optional async callback ``async (percent, message)``
    :return: the created round as a DTO
    """
    trn = state.require_tournament()
    algorithm = request.algorithm or state.settings.default_draw

    stats = trn.statistiques()
    byes = draws.select_bye_teams(stats, trn.equipes_par_manche, forced=request.bye_teams)

    matches = await draws.generate(
        algorithm,
        trn.equipes_par_manche,
        stats,
        bye_teams=byes,
        config=request.config,
        on_progress=on_progress,
    )

    rnd = trn.ajout_partie()
    locations = trn.locations()
    match_map = {locations[i]: match for i, match in enumerate(matches)}
    rnd.start(match_map, byes=byes)
    auto_save(state)
    return round_dto(trn, rnd)


def set_match_result(state, round_number, result):
    """Register the score of a match in a round."""
    trn = state.require_tournament()
    rnd = trn.partie(round_number)
    rnd.add_result({int(k): int(v) for k, v in result.points.items()}, datetime.now())
    auto_save(state)
    return round_dto(trn, rnd)


# --------------------------------------------------------------------------- #
# Draws metadata
# --------------------------------------------------------------------------- #
def list_draws():
    """Return the metadata of every available draw algorithm."""
    return [schemas.DrawInfoDTO(**info) for info in draws.available()]
