# -*- coding: UTF-8 -*-

"""Pydantic data-transfer objects exchanged with the web frontend."""

from pydantic import BaseModel


class PlayerDTO(BaseModel):
    firstname: str
    lastname: str


class TeamDTO(BaseModel):
    number: int
    joker: int
    players: list[PlayerDTO]
    status: str
    points: int
    wins: int
    byes: int


class TeamCreateDTO(BaseModel):
    number: int | None = None
    joker: int = 0
    players: list[PlayerDTO] = []


class MatchDTO(BaseModel):
    location: int | None
    teams: list[int]
    points: dict[int, int]
    finished: bool


class RoundDTO(BaseModel):
    number: int
    status: str
    matches: list[MatchDTO]
    byes: list[int]


class RankEntryDTO(BaseModel):
    rank: int
    team: int
    wins: int
    points: int
    joker: int
    buchholz: int
    goal_average: int


class TournamentDTO(BaseModel):
    status: str
    teams_by_match: int
    points_by_match: int
    players_by_team: int
    nb_teams: int
    nb_rounds: int
    filename: str | None
    changed: bool
    auto_save: bool


class TournamentCreateDTO(BaseModel):
    title: str | None = None
    teams_by_match: int | None = None
    points_by_match: int | None = None
    players_by_team: int | None = None


class TournamentLoadDTO(BaseModel):
    filename: str


class DrawInfoDTO(BaseModel):
    name: str
    description: str
    default: dict
    config: dict


class DrawRequestDTO(BaseModel):
    algorithm: str | None = None
    config: dict | None = None
    bye_teams: list[int] = []


class DrawTeamMetricDTO(BaseModel):
    team: int
    wins: int
    points: int
    joker: int
    buchholz: int
    goal_average: int
    opponents: list[int] = []
    power_score: float


class DrawMatchPreviewDTO(BaseModel):
    id: str
    location: int | None
    teams: list[int | None]
    group_wins: int
    quality: int
    violations: list[str]
    rematch_pairs: list[list[int]] = []
    team_metrics: list[DrawTeamMetricDTO]


class DrawAlertDTO(BaseModel):
    code: str
    severity: str
    message: str
    match_id: str | None = None


class DrawPreviewDTO(BaseModel):
    algorithm: str
    matches: list[DrawMatchPreviewDTO]
    byes: list[int]
    forfeits: list[int]
    unassigned: list[int]
    alerts: list[DrawAlertDTO]
    can_create: bool


class RoundCreateDTO(BaseModel):
    algorithm: str | None = None
    config: dict | None = None
    bye_teams: list[int] = []
    matches: list[list[int | None]] = []
    byes: list[int] = []
    forfeits: list[int] = []


class MatchResultDTO(BaseModel):
    points: dict[int, int]


class DisplayViewDTO(BaseModel):
    view: str


class SettingsDTO(BaseModel):
    # Settings grouped into sections (the sections are defined once in
    # tourbillon/settings.py and never redeclared here or in the frontend).
    general: dict
    tournament: dict
    display: dict
    draws: dict


class SettingsUpdateDTO(BaseModel):
    general: dict | None = None
    tournament: dict | None = None
    display: dict | None = None
    draws: dict | None = None
