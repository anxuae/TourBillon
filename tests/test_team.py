# -*- coding: UTF-8 -*-

import pytest
from datetime import timedelta

from tourbillon.core import cst, team, tournament
from tourbillon.core.exception import StatusError
from data import t2teams2players


def check_statistics(equ2jn1, opponents=[], points=0, wins=0, forfeits=0, rounds=0,
                     byes=0, average_score=0, min_score=0, max_score=0,
                     average_duration=timedelta(0), min_duration=timedelta(0),
                     max_duration=timedelta(0)):
    assert equ2jn1.opponent_ids() == opponents
    assert equ2jn1.points() == points
    assert equ2jn1.wins() == wins
    assert equ2jn1.forfeits() == forfeits
    assert equ2jn1.rounds() == rounds
    assert equ2jn1.byes() == byes
    assert equ2jn1.average_score() == average_score
    assert equ2jn1.min_score() == min_score
    assert equ2jn1.max_score() == max_score
    assert equ2jn1.average_duration() == average_duration
    assert equ2jn1.min_duration() == min_duration
    assert equ2jn1.max_duration() == max_duration


def test_empty_team_status(equ2jn1):
    assert equ2jn1.status == cst.TEAM_INCOMPLETE


def test_empty_team_nb_players(equ2jn1):
    assert len(equ2jn1.players()) == 0


@pytest.mark.parametrize('player', t2teams2players.PLAYERS_1)
def test_add_player(equ2jn1, player):
    equ2jn1.add_player(*player)


def test_complete_team_status(equ2jn1):
    assert equ2jn1.status == cst.TEAM_WAITING_DRAW


def test_complete_team_nb_players(equ2jn1):
    assert len(equ2jn1.players()) == t2teams2players.PLAYERS_BY_TEAM


def test_complete_team_statistics(equ2jn1):
    check_statistics(equ2jn1)


def test_add_rounds(equ2jn1):
    """Add each round one by one and check the accumulated statistics."""
    previous_stat = None
    for i, round_data in enumerate(t2teams2players.ROUNDS_1):
        stat_data = t2teams2players.STATS_1[i]
        in_progress = round_data['result'] not in (cst.FORFEIT, cst.BYE)

        # Status before adding the round
        assert equ2jn1.status == cst.TEAM_WAITING_DRAW

        # Add the round
        if in_progress:
            # The result is unknown and the match is in progress
            equ2jn1._add_round(round_data['start'], round_data['opponents'], None, 1)
            with pytest.raises(StatusError):
                equ2jn1._add_round(round_data['start'], round_data['opponents'], None, 1)
            assert equ2jn1.status == cst.TEAM_IN_PROGRESS
        else:
            equ2jn1._add_round(round_data['start'], round_data['opponents'], round_data['result'], 1)
            assert equ2jn1.status == cst.TEAM_WAITING_DRAW

        # Statistics before entering the result
        if in_progress:
            if previous_stat is None:
                check_statistics(equ2jn1, opponents=stat_data['opponents'],
                                 rounds=stat_data['rounds'])
            else:
                check_statistics(equ2jn1, opponents=stat_data['opponents'],
                                 points=previous_stat['points'],
                                 wins=previous_stat['wins'],
                                 forfeits=previous_stat['forfeits'],
                                 rounds=stat_data['rounds'],
                                 byes=previous_stat['byes'],
                                 average_score=previous_stat['average_score'],
                                 min_score=previous_stat['min_score'],
                                 max_score=previous_stat['max_score'],
                                 average_duration=previous_stat['average_duration'],
                                 min_duration=previous_stat['min_duration'],
                                 max_duration=previous_stat['max_duration'])
        else:
            check_statistics(equ2jn1, **stat_data)

        # Enter the result
        end = round_data['start'] + round_data['duration'] if in_progress else None
        with pytest.raises(ValueError):
            equ2jn1._modify_round(10, round_data['points'], round_data['result'], end)
        equ2jn1._modify_round(i + 1, round_data['points'], round_data['result'], end)

        # Statistics after entering the result
        check_statistics(equ2jn1, **stat_data)
        previous_stat = stat_data


def test_team_power_is_zero_for_empty_standalone_team():
    standalone = team.Team(
        tournament.Tournament(
            t2teams2players.TEAMS_BY_MATCH,
            t2teams2players.POINTS_BY_MATCH,
            t2teams2players.PLAYERS_BY_TEAM,
        ),
        1,
    )
    assert standalone.power() == 0.0


def test_team_power_uses_tournament_maxima(trb4e1j):
    teams = trb4e1j.teams()

    max_points = max([item.points() for item in teams], default=0)
    max_buchholz = max([item.buchholz_truncated() for item in teams], default=0)
    max_wins = max([item.wins() + item.byes() for item in teams], default=0)
    max_goal_average = max([item.goal_average() for item in teams], default=0)

    def normalized_ratio(value, maximum):
        if maximum <= 0:
            return 0.0
        return max(0.0, min(1.0, value / maximum))

    for item in teams:
        score = (
            normalized_ratio(item.points(), max_points) * 1.5
            + normalized_ratio(item.buchholz_truncated(), max_buchholz) * 1
            + normalized_ratio(item.wins() + item.byes(), max_wins) * 2
            + normalized_ratio(item.goal_average(), max_goal_average) * 0.5
        )
        expected = max(0.0, min(5.0, score))
        assert item.power() == round(expected, 2)


