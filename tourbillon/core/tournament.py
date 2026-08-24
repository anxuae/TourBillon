# -*- coding: UTF-8 -*-

"""Tournament class definition"""

import random
from datetime import datetime
from functools import partial, cmp_to_key
from pathlib import Path

import yaml

from . import cst
from .exception import FileError, StatusError, InconsistencyError
from .match import MatchResult
from .team import Team
from .round import Round
from ..assets import banner


def load(filename):
    """
    Load a tournament from a file in YAML format.
    """
    with open(filename, 'r', encoding='utf-8') as fp:
        y = yaml.load(fp, Loader=yaml.Loader)
    tournament = Tournament()

    try:
        # Save date
        tournament.save_date = y['enregistrement']

        # Tournament info
        tournament.start_date = y['tournoi']['debut']
        tournament.teams_by_match = y['tournoi']['equipes_par_manche']
        tournament.players_by_team = y['tournoi']['joueurs_par_equipe']
        tournament.points_by_match = y['tournoi']['points_par_manche']

        # Registration info
        for num in y['inscription']:
            team = tournament.add_team(num, y.get('jokers', {}).get(num, 0))
            for player in y['inscription'][num]:
                team.add_player(player[0], player[1])

        # Rounds info
        for num in y['parties']:
            for data in y['parties'][num]:
                m = MatchResult()
                m.load(data)
                tournament.team(num)._results.append(m)

        # Number of rounds
        nb_rounds = 0
        for team in tournament.teams():
            if len(team._results) > nb_rounds:
                nb_rounds = len(team._results)

        # Round creation
        for num in range(1, nb_rounds + 1):
            tournament._rounds.append(Round(tournament))

        tournament.load_date = datetime.now()
        tournament.changed = False
    except Exception as ex:
        raise InconsistencyError(f"File '{filename}' is corrupted ({ex}).")

    return tournament


def dump(tournament, filename):
    """
    Record a tournament in a file in YAML format.
    """
    if Path(filename).exists() and not Path(filename).is_file():
        raise FileError(f"'{filename}' is a directory")

    previous_date = tournament.save_date
    try:
        with open(filename, 'w', encoding='utf-8') as fp:
            fp.write(banner() + '\n')

            # Save date
            d = datetime.now()
            yaml.dump({'enregistrement': d}, fp, default_flow_style=False)

            # Tournament info
            y = {}
            y['tournoi'] = {}
            y['tournoi']['debut'] = tournament.start_date
            y['tournoi']['equipes_par_manche'] = tournament.teams_by_match
            y['tournoi']['joueurs_par_equipe'] = tournament.players_by_team
            y['tournoi']['points_par_manche'] = tournament.points_by_match
            yaml.dump(y, fp, default_flow_style=False)

            # Registration info
            y = {}
            y['inscription'] = {}
            y['jokers'] = {}
            for team in tournament.teams():
                y['inscription'][team.id] = []
                y['jokers'][team.id] = team.joker
                for player in team.players():
                    y['inscription'][team.id].append([player.firstname, player.lastname])
            yaml.dump(y, fp, default_flow_style=False)

            # Rounds info
            y = {}
            y['parties'] = {}
            for team in tournament.teams():
                y['parties'][team.id] = [m.dump() for m in team._results]
            yaml.dump(y, fp, default_flow_style=False)

        tournament.save_date = d
        tournament.changed = False
    except Exception as ex:
        tournament.save_date = previous_date
        raise IOError(f"Tournament dump failed ({ex})")


class Tournament:

    """
    Class which represent a tournament. This class manipulates team data.
    """

    def __init__(self, teams_by_match=2, points_by_match=12, players_by_team=2):
        self.teams_by_match = teams_by_match
        self.players_by_team = players_by_team
        self.points_by_match = points_by_match

        self.start_date = datetime.now()
        self.load_date = None
        self.save_date = None

        self.changed = False
        self._teams = {}
        self._rounds = []

    def __str__(self):
        text = """
        Billon Tournament:
            Date                : %s
            Number of rounds    : %s
            Number of teams     : %s
            Team per match      : %s
            Points per match    : %s
            Players per team    : %s

            Status              : %s
        """
        return text % (self.start_date,
                       len(self.rounds()),
                       len(self._teams),
                       self.teams_by_match,
                       self.points_by_match,
                       self.players_by_team,
                       self.status)

    @property
    def status(self):
        """
        Return tournament status.

        TOURNAMENT_REGISTRATION      => No round started
        TOURNAMENT_WAITING_DRAW      => Last round is finished
        TOURNAMENT_ROUND_IN_PROGRESS => A round is in progress
        """
        # Impossible to create a match
        if self.nb_teams() < self.teams_by_match:
            return cst.TOURNAMENT_REGISTRATION

        # Not all the information has been entered
        for team in self.teams():
            if team.status == cst.TEAM_INCOMPLETE:
                return cst.TOURNAMENT_REGISTRATION

        # State of the current round
        if self.current_round() is None:
            return cst.TOURNAMENT_WAITING_DRAW
        else:
            if self.current_round().status in [cst.ROUND_COMPLETE, cst.ROUND_FINISHED]:
                return cst.TOURNAMENT_WAITING_DRAW
            else:
                return cst.TOURNAMENT_ROUND_IN_PROGRESS

    def statistics(self, excluded_teams=None, round_limit=None):
        """
        Statistics on the previous rounds of the specified teams.
        """
        stat = {}
        for team in self.teams():
            if not excluded_teams or team not in excluded_teams:
                stat[team.id] = {cst.STAT_POINTS: team.points(round_limit),
                                 cst.STAT_WINS: team.wins(round_limit),
                                 cst.STAT_BYES: team.byes(round_limit),
                                 cst.STAT_OPPONENTS: team.opponent_ids(round_limit),
                                 cst.STAT_MATCHES: team.matches(round_limit),
                                 cst.STAT_BUCHHOLZ: team.buchholz_truncated(round_limit),
                                 cst.STAT_GOAL_AVERAGE: team.goal_average(round_limit)}
        return stat

    def locations(self):
        """
        Return a list of available location numbers for this tournament. It is
        based on the previous round in order to determine if some location
        numbers must be ignored (degraded location).

        No location planned for the byes.
        """
        number = self.nb_teams() // self.teams_by_match
        locations = []
        i = 1
        if self.current_round():
            for p in self.current_round().locations():
                if len(locations) == number:
                    break
                locations.append(p)
            if locations:
                i = locations[-1] + 1

        while i <= number:
            locations.append(i)
            i += 1

        return locations

    def nb_teams(self):
        """
        Return the number of registered teams.
        """
        return len(self._teams)

    def team(self, id):
        """
        Return the team with the specified identifier.

        :param id: team identifier (int)
        """
        if type(id) == Team:
            return id
        elif id not in self._teams:
            raise ValueError("Team n°%s does not exist." % id)
        else:
            return self._teams[id]

    def teams(self):
        """
        Return the teams as a list.
        """
        return list(self._teams.values())

    def generate_team_id(self):
        """
        Return an unused team identifier.
        """
        i = 1
        while i in self._teams:
            i += 1
        return i

    def add_team(self, id=None, joker=0):
        """
        Add and return a new team with the specified identifier. If no
        identifier is given, the smallest available one is chosen.

        :param id: team identifier (int)
        """
        if id is None:
            id = self.generate_team_id()
        if id in self._teams:
            raise ValueError("Team n°%s already exists." % id)

        team = Team(self, id, joker)
        self._teams[team.id] = team
        self.changed = True
        return team

    def remove_team(self, id):
        """
        Remove and return the team with the specified identifier.

        :param id: team identifier (int)
        """
        if id not in self._teams:
            raise ValueError("Team n°%s does not exist." % id)

        team = self._teams[id]
        if team.rounds() != 0:
            raise StatusError("Team n°%s cannot be removed once linked to rounds." % id)

        team = self._teams.pop(id)
        self.changed = True
        return team

    def change_team_id(self, id, new_id):
        """
        Change the identifier of a team. Can only be done if no round has
        been started.

        :param id: current team identifier (int)
        :param new_id: new team identifier (int)
        """
        if self.nb_rounds() != 0:
            raise StatusError("The identifier of team n°%s cannot be changed." % id)
        if new_id in self._teams:
            raise ValueError("Team n°%s already exists." % new_id)

        team = self._teams.pop(id)
        team._id = new_id
        self._teams[new_id] = team
        self.changed = True

    def nb_rounds(self):
        """
        Return the number of rounds.
        """
        return len(self.rounds())

    def round(self, number):
        """
        Return the round with the specified number.

        :param number: round number (int)
        """
        if type(number) == Round:
            return number
        elif number not in range(1, len(self.rounds()) + 1):
            raise ValueError("Round n°%s does not exist." % number)
        else:
            return self.rounds()[number - 1]

    def current_round(self):
        """
        Return the last round of the tournament.
        """
        if len(self.rounds()) != 0:
            return self.rounds()[-1]
        else:
            return None

    def rounds(self):
        """
        Return the rounds as a list.
        """
        return self._rounds

    def add_round(self):
        """
        Add and return a new round.
        """
        if self.status == cst.TOURNAMENT_REGISTRATION:
            raise StatusError("Cannot create a round (registration in progress).")
        elif self.status == cst.TOURNAMENT_ROUND_IN_PROGRESS:
            raise StatusError("Cannot create a new round (current round: %s)." %
                              (self.current_round().status))

        round = Round(self)
        self.rounds().append(round)
        self.changed = True
        return round

    def remove_round(self, number):
        """
        Remove the round corresponding to the specified number.

        :param number: round number (int)
        """
        if number > len(self.rounds()) or number < 1:
            raise ValueError("Round n°%s does not exist." % number)
        else:
            self.round(number).delete()
            self.rounds().pop(number - 1)
            self.changed = True

    def matches(self):
        """
        Return the list of matches that already took place during the tournament.
        (Byes and forfeits are excluded from matches, see the definition of the
        matches of a round)
        """
        matches = []
        for round in self.rounds():
            for match in round.matches():
                matches.append(match)
        return matches

    def compare(self, team1, team2, round_limit=None):
        """
        Compare the strength of two teams. The comparison is based on the number
        of wins (if enabled), the number of points, the joker number (if
        enabled), Buchholz score (if enabled) and finally goal average (if
        enabled).

        :param team1: Team instance
        :param team2: Team instance
        :param round_limit: limit for the comparison computation
        """
        if type(team1) != Team or type(team2) != Team:
            raise TypeError("A team must be compared to another one.")

        # priority 1: comparison of wins
        vic = team1.wins(round_limit) + team1.byes(round_limit) - \
            team2.wins(round_limit) - team2.byes(round_limit)
        if vic > 0:
            vic = 1
        elif vic < 0:
            vic = -1

        if self.cmp_with_wins and vic != 0:
            return vic

        # priority 2: comparison of points
        pts = team1.points(round_limit) - team2.points(round_limit)
        if pts > 0:
            pts = 1
        elif pts < 0:
            pts = -1

        if pts != 0:
            return pts

        # priority 3: comparison of joker numbers
        joker = team1.joker - team2.joker
        if joker > 0:
            joker = 1
        elif joker < 0:
            joker = -1

        if self.cmp_with_joker and joker != 0:
            return joker

        # priority 4: comparison of Buchholz scores
        buchholz = team1.buchholz_truncated(round_limit) - team2.buchholz_truncated(round_limit)
        if buchholz > 0:
            buchholz = 1
        elif buchholz < 0:
            buchholz = -1

        if self.cmp_with_buchholz and buchholz != 0:
            return buchholz

        # priority 5: comparison of goal average
        goal_average = team1.goal_average(round_limit) - team2.goal_average(round_limit)
        if goal_average > 0:
            goal_average = 1
        elif goal_average < 0:
            goal_average = -1

        if self.cmp_with_goal_avg and goal_average != 0:
            return goal_average

        return 0

    def ranking(self, with_wins=True, with_joker=True, with_buchholz=True, with_goal_avg=True, round_limit=None):
        """
        Return a list of tuples indicating the team and its place in the
        ranking. In case of a tie, the place(s) following the ex aequo are no
        longer used in order to keep a place number matching the number of teams.

        Example:
            [(12, 1), (4, 2), (7, 2), (9, 4)...]

        :param with_wins: the ranking takes into account the number of wins of the team.
        :param with_joker: the ranking takes into account the greatest joker number.
        :param with_buchholz: the ranking takes into account the Buchholz score.
        :param with_goal_avg: the ranking takes into account the goal average.
        :param round_limit: limit for the ranking computation
        """
        self.cmp_with_wins = with_wins
        self.cmp_with_joker = with_joker
        self.cmp_with_buchholz = with_buchholz
        self.cmp_with_goal_avg = with_goal_avg
        l = sorted(self.teams(), key=cmp_to_key(partial(self.compare, round_limit=round_limit)), reverse=True)

        ranking = []

        if self.nb_teams() != 0:
            place = 1
            ranking.append((l[0], place))
            i = 1
            while i < len(l):
                if self.compare(l[i - 1], l[i], round_limit=round_limit) != 0:
                    place = i + 1
                ranking.append((l[i], place))
                i += 1

        return ranking
