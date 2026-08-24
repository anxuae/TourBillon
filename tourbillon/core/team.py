# -*- coding: UTF-8 -*-

"""Team class definition"""

from datetime import datetime, timedelta

from . import cst
from .exception import BoundError, StatusError
from .match import MatchResult
from .player import Player


class Team:

    """
    Class which represent a team. This class store all team data for the
    tournament.
    """

    def __init__(self, tournament, id, joker=0):
        self.tournament = tournament
        self.joker = int(joker)
        self._id = int(id)
        self._players_list = []
        self._results = []

    def __str__(self):
        return f"""
        Team n°{self.id}
            Names     : {" / ".join([" ".join([player.firstname, player.lastname]) for player in self._players_list])}
            Points    : {self.points()}
            Wins      : {self.wins()}
            Byes      : {self.byes()}

            Status    : {self.status}
        """

    def __int__(self):
        return self.id

    def __hash__(self):
        return id(self)

    def __lt__(self, other):
        return int(self) < int(other)

    def __le__(self, other):
        return int(self) <= int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __ge__(self, other):
        return int(self) >= int(other)

    def __eq__(self, other):
        return int(self) == int(other)

    def __ne__(self, other):
        return int(self) != int(other)

    def _add_round(self, start: datetime, opponents: list = [], result: str = None, location: int = None):
        """
        Add results for the team to the given round.

        WARNING: DO NOT USE OUTSIDE OF TOURNAMENT AND ROUND CLASSES.

        :param start: match start date
        :param opponents: competitors list
        :param result: match status before it starts (BYE, FORFEIT)
        :param location: match location ID
        """
        if self.status == cst.TEAM_IN_PROGRESS or self.status == cst.TEAM_INCOMPLETE:
            raise StatusError(
                f"Cannot create round for team n°{self.id}. (round in progress: {len(self._results)})")
        else:
            m = MatchResult(start, opponents)
            if result == cst.BYE:
                m.points = self.tournament.points_by_match
            if result:
                m.result = result
            m.location = location
            self._results.append(m)

    def _remove_round(self, round_number: int):
        """
        Delete the team's results in the given round.

        WARNING: DO NOT USE OUTSIDE OF TOURNAMENT AND ROUND CLASSES.

        :param round_number: round number
        """
        round_number = int(round_number)
        if round_number not in range(1, len(self._results) + 1):
            raise ValueError(
                f"Cannot delete round n°{round_number} for team {self.id} (total rounds: {len(self._results)})")
        else:
            self._results.pop(round_number - 1)

    def _modify_round(self, round_number: int, points: int = None, result: str = None, end: datetime = None, location: int = None):
        """
        Change the team's results in the given game.

        WARNING: DO NOT USE OUTSIDE OF TOURNAMENT AND ROUND CLASSES.

        :param round_number: round number
        :param points: points obtained by the team for the given round
        :param result: match status (WON, LOST)
        :param end: match end date
        :param location: match location ID
        """
        round_number = int(round_number)
        if round_number not in range(1, len(self._results) + 1):
            raise ValueError(f"Round n°{round_number} does not exists for team n°{self.id}")
        else:
            m = self._results[round_number - 1]

            if result is not None:
                m.result = result

            if result == cst.BYE:
                m.points = self.tournament.points_by_match
            elif points is not None and result != cst.FORFEIT:
                m.points = points

            if end is not None:
                m.end = end

            if location is not None:
                m.location = location

    @property
    def id(self) -> int:
        """
        Return the team identifier.
        """
        return self._id

    @property
    def status(self) -> str:
        """
        Return the team status.

        TEAM_INCOMPLETE   => some players are missing in the team
        TEAM_IN_PROGRESS  => match with this team is in progress
        TEAM_WAITING_DRAW => match of the last round is completed
        """
        if self.tournament.players_by_team != len(self._players_list):
            return cst.TEAM_INCOMPLETE
        else:
            if len(self._results) == 0:
                return cst.TEAM_WAITING_DRAW
            else:
                m = self._results[-1]
                if m.status == cst.MATCH_IN_PROGRESS:
                    return cst.TEAM_IN_PROGRESS
                else:
                    return cst.TEAM_WAITING_DRAW

    def players(self):
        """
        Return players.
        """
        return self._players_list

    def add_player(self, firstname: str, lastname: str):
        """
        Add a new player.

        :param firstname: firstname
        :param lastname: lastname
        """
        if self.tournament.players_by_team < len(self._players_list) + 1:
            raise BoundError(f"A team shall be composed of {self.tournament.players_by_team} players")

        j = Player(firstname, lastname)
        self._players_list.append(j)
        self.tournament.changed = True
        return j

    def remove_players(self):
        """
        Remove all players.
        """
        self._players_list = []
        self.tournament.changed = True

    def round_exists(self, round_number: int):
        """
        Return True if a match is defined for the specified round. Except in
        exceptional cases (adding teams after a tournament has already started),
        a match is always defined for each round.

        :param round_number: round number
        """
        try:
            return self._results[round_number - 1] is not None
        except IndexError:
            return False

    def result(self, round_number: int):
        """
        Return the match result for the given round number.

        :param round_number: round number
        """
        round_number = int(round_number)
        if round_number not in range(1, len(self._results) + 1):
            raise ValueError(f"Round n°{round_number} not created for team {self.id}")
        else:
            return self._results[round_number - 1]

    def opponent_ids(self, round_limit: int | None = None):
        """
        Return the list of competitor team identifiers encountered since the
        first to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)
        l = []
        seen = set()
        for m in self._results[:round_limit]:
            for ad in m.opponent_ids:
                if ad not in seen:
                    seen.add(ad)
                    l.append(ad)

        return l

    def opponents(self, round_limit: int | None = None):
        """
        Return the list of opponent teams encountered since the first
        to the given round number.

        :param round_limit: last round number (included)
        """
        return [self.tournament.team(opponent_id) for opponent_id in self.opponent_ids(round_limit)]

    def matches(self, round_limit: int = None):
        """
        Return the list of team numbers already encountered since the
        first to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)
        l = []
        for m in self._results[:round_limit]:
            if m.result in [cst.WON, cst.LOST]:
                match = sorted(m.opponent_ids + [self.id])
                l.append(match)

        return l

    def points(self, round_limit: int = None):
        """
        Return the sum of the points since the first
        to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)

        l = [m.points for m in self._results[:round_limit]]
        return sum(l)

    def wins(self, round_limit: int = None):
        """
        Return the number of wins since the first
        to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)

        l = [m.result for m in self._results[:round_limit] if m.result == cst.WON]
        return len(l)

    def forfeits(self, round_limit: int = None):
        """
        Return the number of forfeits since the first
        to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)

        l = [m.result for m in self._results[:round_limit] if m.result == cst.FORFEIT]
        return len(l)

    def byes(self, round_limit: int = None):
        """
        Return the number of byes since the first
        to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)

        l = [m.result for m in self._results[:round_limit] if m.result == cst.BYE]
        return len(l)

    def rounds(self, round_limit: int = None):
        """
        Return the number of rounds which are not forfeit since the first
        to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)

        # FORFEIT rounds are not taken into account
        l = [m.result for m in self._results[:round_limit] if m.result != cst.FORFEIT]
        return len(l)

    def average_score(self, round_limit: int = None):
        """
        Return the average points of a match since the first
        to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)
        pts = self.points(round_limit)

        # FORFEIT rounds and the incomplete round result are not taken into account
        rounds = len([m.result for m in self._results[:round_limit]
                      if m.status != cst.MATCH_IN_PROGRESS and m.result != cst.FORFEIT])
        if rounds == 0:
            return 0
        else:
            return round(pts / rounds, 2)

    def min_score(self, round_limit: int = None):
        """
        Returns the min points of a match from the first
        to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)

        # FORFEIT rounds and the incomplete round result are not taken into account
        l = [m.points for m in self._results[:round_limit] if m.status != cst.MATCH_IN_PROGRESS and m.result != cst.FORFEIT]
        if l == []:
            return 0
        else:
            return min(l)

    def max_score(self, round_limit: int = None):
        """
        Return the max points of a match since the first
        to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)

        l = [m.points for m in self._results[:round_limit]]
        if l == []:
            return 0
        else:
            return max(l)

    def average_duration(self, round_limit: int = None):
        """
        Return the average duration of a match since the first
        to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)

        # FORFEIT, BYE rounds and the incomplete round result are not taken into account
        l = [m.duration for m in self._results[:round_limit] if m.duration is not None]
        if l == []:
            return timedelta(0)
        else:
            r = timedelta(0)
            for t in l:
                r += t
            return r // len(l)

    def min_duration(self, round_limit: int = None):
        """
        Return the min duration of a match since the first
        to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)

        # FORFEIT, BYE rounds and the incomplete round result are not taken into account
        l = [m.duration for m in self._results[:round_limit] if m.duration is not None]
        if l == []:
            return timedelta(0)
        else:
            return min(l)

    def max_duration(self, round_limit: int = None):
        """
        Return the max duration of a match since the first
        to the given round number.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)

        # FORFEIT, BYE rounds and the incomplete round result are not taken into account
        l = [m.duration for m in self._results[:round_limit] if m.duration is not None]
        if l == []:
            return timedelta(0)
        else:
            return max(l)

    def buchholz_truncated(self, round_limit: int | None = None):
        """
        Return the truncated Buchholz score.

        The Buchholz score is the sum of the points obtained by all
        opponents encountered by the team.

        From the second round onward, the opponent with the lowest
        cumulative score is removed.

        BYE and FORFEIT rounds are ignored.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)

        opponent_scores = []

        for opponent in self.opponents(round_limit):
            opponent_scores.append(opponent.points(round_limit))

        if not opponent_scores:
            return 0

        # Truncation only when there are at least 2 rounds.
        if round_limit >= 2:
            opponent_scores.remove(min(opponent_scores))

        return sum(opponent_scores)


    def goal_average(self, round_limit: int | None = None):
        """
        Return the goal average.

        In this tournament:
            goals for     = team's points
            goals against = opponent's points

        The goal average is therefore:

            total points scored - total points conceded

        BYE and FORFEIT rounds are ignored.

        :param round_limit: last round number (included)
        """
        if round_limit is None:
            round_limit = len(self._results)

        goal_for = 0
        goal_against = 0

        for round_number, match in enumerate(
            self._results[:round_limit],
            start=1
        ):
            # BYE and FORFEIT do not count.
            if match.result in [cst.BYE, cst.FORFEIT]:
                continue

            # Points scored by this team.
            goal_for += match.points

            # Points scored by the opponent(s).
            for opponent_id in match.opponent_ids:
                opponent = self.tournament.team(opponent_id)
                opponent_match = opponent.result(round_number)

                if opponent_match.result not in [cst.BYE, cst.FORFEIT]:
                    goal_against += opponent_match.points

        return goal_for - goal_against
