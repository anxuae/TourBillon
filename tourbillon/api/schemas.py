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


class TeamCreate(BaseModel):
    number: int | None = None
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


class TournamentDTO(BaseModel):
    status: str
    teams_by_match: int
    points_by_match: int
    players_by_team: int
    nb_teams: int
    nb_rounds: int
    filename: str | None


class TournamentCreate(BaseModel):
    teams_by_match: int | None = None
    points_by_match: int | None = None
    players_by_team: int | None = None


class DrawInfoDTO(BaseModel):
    name: str
    description: str
    default: dict
    config: dict


class DrawRequest(BaseModel):
    algorithm: str | None = None
    config: dict | None = None
    bye_teams: list[int] = []


class MatchResult(BaseModel):
    points: dict[int, int]


class SettingsDTO(BaseModel):
    host: str
    port: int
    save_dir: str
    auto_save: bool
    players_by_team: int
    points_by_match: int
    teams_by_match: int
    rank_by_wins: bool
    rank_by_joker: bool
    rank_by_duration: bool
    default_draw: str
    draws: dict


class SettingsUpdate(BaseModel):
    host: str | None = None
    port: int | None = None
    save_dir: str | None = None
    auto_save: bool | None = None
    players_by_team: int | None = None
    points_by_match: int | None = None
    teams_by_match: int | None = None
    rank_by_wins: bool | None = None
    rank_by_joker: bool | None = None
    rank_by_duration: bool | None = None
    default_draw: str | None = None
    draws: dict | None = None
