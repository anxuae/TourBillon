# -*- coding: UTF-8 -*-

"""Business orchestration between the core domain and the API layer.

This module bridges the (legacy, French) ``core`` package to the English DTOs
and handles persistence (YAML) and draw execution. It keeps ``core`` fully
independent from FastAPI.
"""

import re
from datetime import datetime
from pathlib import Path

from ..core import cst, tournament as core_tournament
from ..core import draws
from . import schemas


# --------------------------------------------------------------------------- #
# Tournament lifecycle
# --------------------------------------------------------------------------- #
def create_tournament(state, params):
    """Create a fresh tournament using the given parameters.

    The per-tournament parameters are provided by the request; any omitted
    value falls back to the ``core.Tournament`` built-in defaults (they are no
    longer stored in the settings).
    """
    kwargs = {}
    if params.teams_by_match:
        kwargs["teams_by_match"] = params.teams_by_match
    if params.points_by_match:
        kwargs["points_by_match"] = params.points_by_match
    if params.players_by_team:
        kwargs["players_by_team"] = params.players_by_team
    trn = core_tournament.Tournament(**kwargs)
    state.tournament = trn
    # The title (if any) is only used to name the save file; the core model
    # does not carry it. Any following save/auto-save reuses this path.
    state.filename = _title_to_filename(state, params.title)
    return trn


def _title_to_filename(state, title):
    """Turn a tournament title into a save file path, or ``None``.

    The title is sanitized into a safe base name (kept letters, digits, dash,
    underscore and dots; other runs become a single underscore) and resolved
    against the save directory with a ``.yml`` extension.
    """
    if not title or not title.strip():
        return None
    safe = re.sub(r"[^\w.-]+", "_", title.strip()).strip("._")
    if not safe:
        return None
    if not safe.lower().endswith((".yml", ".yaml")):
        safe += ".yml"
    return str(Path(state.settings.save_dir) / safe)


def load_tournament(state, filename):
    """Load a tournament from a YAML file (retro-compatible).

    A bare file name (no directory) is resolved against the save directory so
    the frontend can load a file listed by ``/api/history/tournaments``.
    """
    path = Path(filename)
    if path.parent == Path("."):
        path = Path(state.settings.save_dir) / path
    trn = core_tournament.load(str(path))
    state.tournament = trn
    state.filename = str(path)
    return trn


def upload_tournament(state, filename, content, overwrite=False):
    """Save an uploaded YAML file into the save dir, then load it.

    The file is stored under the save directory using its base name only (any
    directory component is stripped). If a file with the same name already
    exists and ``overwrite`` is false, a :class:`FileExistsError` is raised so
    the caller can ask the user for confirmation.

    :param state: application state
    :param filename: original file name of the upload
    :param content: raw file bytes
    :param overwrite: allow replacing an existing file
    :return: the loaded tournament
    """
    name = Path(filename).name
    if Path(name).suffix.lower() not in (".yml", ".yaml"):
        raise ValueError("Only .yml or .yaml save files are accepted")

    target = Path(state.settings.save_dir) / name
    if target.exists() and not overwrite:
        raise FileExistsError(name)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return load_tournament(state, name)


def save_tournament(state, filename=None):
    """Persist the current tournament to a YAML file."""
    trn = state.require_tournament()
    if filename is None:
        filename = state.filename
    if filename is None:
        name = f"tournament_{datetime.now():%Y-%m-%d_%H%M%S}.yml"
        filename = str(Path(state.settings.save_dir) / name)
    core_tournament.dump(trn, filename)
    state.filename = filename
    return filename


def delete_tournament_file(state):
    """Delete the save file bound to the current tournament.

    The file must exist and be located inside the configured save directory.
    After deletion, the current tournament is unloaded.
    """
    state.require_tournament()
    if not state.filename:
        raise ValueError("Current tournament has no save file")

    target = Path(state.filename).resolve()
    save_dir = Path(state.settings.save_dir).resolve()

    if target.parent != save_dir:
        raise ValueError("Cannot delete a file outside the save directory")
    if not target.exists() or not target.is_file():
        raise FileNotFoundError(str(target))

    target.unlink()
    state.tournament = None
    state.filename = None
    return str(target)


def get_display_view(state):
    """Return the currently selected display view."""
    return {"view": state.display_view}


def set_display_view(state, view):
    """Update the shared display view and broadcast it to connected clients."""
    allowed = {"display-teams", "display-rankings", "display-round"}
    if view not in allowed:
        raise ValueError(f"Unknown display view '{view}'")
    state.display_view = view
    return {"view": state.display_view}


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
        changed=trn.changed,
        auto_save=state.settings.auto_save,
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
            if location is None and result.location is not None:
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


def ranking_dto(state, trn, round_limit=None):
    """Return the ranking as a list of :class:`schemas.RankEntryDTO`."""
    entries = []
    for team, rank in trn.ranking(
        with_wins=state.settings.rank_by_wins,
        with_joker=state.settings.rank_by_joker,
        with_buchholz=state.settings.rank_by_buchholz,
        with_goal_avg=state.settings.rank_by_goal_avg,
        round_limit=round_limit,
    ):
        entries.append(
            schemas.RankEntryDTO(
                rank=rank,
                team=team.id,
                wins=team.wins(round_limit),
                points=team.points(round_limit),
                joker=team.joker,
                buchholz=team.buchholz_truncated(round_limit),
                goal_average=team.goal_average(round_limit),
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
    team = trn.add_team(payload.number, payload.joker)
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
    """Create a new round either from a draft or by running a draw.

    :param state: application state
    :param request: :class:`schemas.RoundCreateDTO`
    :param on_progress: optional async callback ``async (percent, message)``
    :return: the created round as a DTO
    """
    trn = state.require_tournament()

    if request.matches:
        matches = []
        used = []
        for match in request.matches:
            clean = [team_id for team_id in match if team_id is not None]
            if clean and len(clean) != trn.teams_by_match:
                raise ValueError(f"Each match must contain exactly {trn.teams_by_match} teams")
            if clean:
                matches.append(clean)
                used.extend(clean)

        used.extend(request.byes)
        used.extend(request.forfeits)

        if len(used) != len(set(used)):
            raise ValueError("A team is assigned multiple times")

        all_teams = set([team.id for team in trn.teams()])
        used_set = set(used)

        missing = sorted(all_teams - used_set)
        if missing:
            raise ValueError(f"Some teams are unassigned: {missing}")

        extras = sorted(used_set - all_teams)
        if extras:
            raise ValueError(f"Unknown teams in draft: {extras}")

        byes = request.byes
    else:
        algorithm = request.algorithm or state.settings.default_draw

        stats = trn.statistics()

        # Effective options: algorithm defaults < saved user settings < request.
        config = state.settings.draw_config(algorithm)
        if request.config:
            config.update(request.config)

        byes = draws.select_bye_teams(
            stats,
            trn.teams_by_match,
            forced=request.bye_teams,
            algorithm=algorithm,
            config=config,
        )

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
    if len(matches) > len(locations):
        raise ValueError("Too many matches for available locations")

    match_map = {locations[i]: match for i, match in enumerate(matches)}
    rnd.start(match_map, byes=byes)
    auto_save(state)
    return round_dto(trn, rnd)


def _team_metric(team, round_limit=None, opponents=None):
    wins = team.wins(round_limit) + team.byes(round_limit)
    points = team.points(round_limit)
    joker = team.joker
    buchholz = team.buchholz_truncated(round_limit)
    goal_average = team.goal_average(round_limit)

    return {
        "team": team.id,
        "wins": wins,
        "points": points,
        "joker": joker,
        "buchholz": buchholz,
        "goal_average": goal_average,
        "opponents": sorted(set([int(team_id) for team_id in (opponents or [])])),
        "power_score": team.power(round_limit),
    }


def _match_violations(match, stats, max_disparity):
    violations = []
    win_values = [stats[num][cst.STAT_WINS] for num in match]
    disparity = max(win_values) - min(win_values) if win_values else 0

    if max_disparity is not None and disparity > max_disparity:
        violations.append(f"disparity>{max_disparity}")

    rematch_pairs = 0
    total_pairs = 0
    for index, team_id in enumerate(match):
        previous_opponents = set(stats[team_id][cst.STAT_OPPONENTS])
        for opponent in match[index + 1 :]:
            total_pairs += 1
            if opponent in previous_opponents:
                rematch_pairs += 1

    if rematch_pairs > 0:
        violations.append("rematch")

    if total_pairs > 0 and rematch_pairs == total_pairs:
        violations.append("full_rematch")

    return sorted(set(violations))


def _rematch_pairs(match, stats):
    pairs = []
    for index, team_id in enumerate(match):
        previous_opponents = set(stats[team_id][cst.STAT_OPPONENTS])
        for opponent in match[index + 1 :]:
            if opponent in previous_opponents:
                pairs.append([team_id, opponent])
    return pairs


async def preview_draw(state, request, on_progress=None):
    """Run a draw preview without creating a round."""
    trn = state.require_tournament()
    algorithm = request.algorithm or state.settings.default_draw

    stats = trn.statistics()

    config = state.settings.draw_config(algorithm)
    if request.config:
        config.update(request.config)

    byes = draws.select_bye_teams(
        stats,
        trn.teams_by_match,
        forced=request.bye_teams,
        algorithm=algorithm,
        config=config,
    )

    proposed_matches = await draws.generate(
        algorithm,
        trn.teams_by_match,
        stats,
        bye_teams=byes,
        config=config,
        on_progress=on_progress,
    )

    locations = trn.locations()
    preview_matches = []
    alerts = []
    max_disparity = config.get("max_disparity") if isinstance(config, dict) else None

    for index, match in enumerate(proposed_matches):
        metrics = [
            _team_metric(
                trn.team(num),
                opponents=stats[num][cst.STAT_OPPONENTS],
            )
            for num in match
        ]
        group_wins = max([metric["wins"] for metric in metrics]) if metrics else 0
        violations = _match_violations(match, stats, max_disparity)
        rematch_pairs = _rematch_pairs(match, stats)

        quality = 100
        if "rematch" in violations:
            quality -= 40
        disparity_items = [item for item in violations if item.startswith("disparity>")]
        if disparity_items:
            quality -= 30

        quality = max(0, quality)
        match_id = f"m{index + 1}"

        for code in violations:
            alerts.append(
                {
                    "code": code,
                    "severity": "warning",
                    "message": f"Match {index + 1}: {code}",
                    "match_id": match_id,
                }
            )

        preview_matches.append(
            {
                "id": match_id,
                "location": locations[index] if index < len(locations) else None,
                "teams": list(match),
                "group_wins": group_wins,
                "quality": quality,
                "violations": violations,
                "rematch_pairs": rematch_pairs,
                "team_metrics": metrics,
            }
        )

    assigned = set()
    for match in proposed_matches:
        assigned.update(match)
    assigned.update(byes)

    all_teams = set([team.id for team in trn.teams()])
    forfeits = sorted(all_teams - assigned)

    return schemas.DrawPreviewDTO(
        algorithm=algorithm,
        matches=preview_matches,
        byes=sorted(byes),
        forfeits=forfeits,
        unassigned=[],
        alerts=alerts,
        can_create=True,
    )


def set_match_result(state, round_number, result):
    """Register the score of a match in a round."""
    trn = state.require_tournament()
    rnd = trn.round(round_number)
    rnd.add_result({int(k): int(v) for k, v in result.points.items()}, datetime.now())
    auto_save(state)
    return round_dto(trn, rnd)


def delete_round(state, number):
    """Delete a round from the current tournament."""
    trn = state.require_tournament()
    trn.remove_round(number)
    auto_save(state)


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
