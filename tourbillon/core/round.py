# -*- coding: UTF-8 -*-

"""Round class definition"""

import copy
from datetime import datetime

from . import cst
from .match import MatchResult
from .exception import StatusError, InconsistencyError, ResultError


class Round:
    """
    Class which represent a round. This class manipulates team data, it does not
    store any data (It's a proxy!).
    """

    def __init__(self, tournament):
        self.tournament = tournament

    def __str__(self):
        return f"""
        Round n°{self.number}:
            Players   : {self.nb_teams()}
            Byes      : {len(self.byes())}
            Forfeits  : {len(self.forfeits())}

            Status    : {self.status}
        """

    def __int__(self):
        return self.number

    @property
    def number(self) -> int:
        """
        Return the round number.
        """
        if self in self.tournament.rounds():
            return self.tournament.rounds().index(self) + 1
        raise InconsistencyError("This round does not belong to the current tournament")

    @property
    def status(self) -> str:
        """
        Return the round status.

        ROUND_WAITING_DRAW => the draw has not been set
        ROUND_IN_PROGRESS  => the matches have been created
        ROUND_COMPLETE     => the game is complete and it is the last one of the tournament
        ROUND_FINISHED     => the game is complete and it is not the last one of the tournament
        """
        if not self.teams():
            # No team has a round with this game number
            return cst.ROUND_WAITING_DRAW

        for team in self.teams():
            if team.status == cst.TEAM_IN_PROGRESS and self == self.tournament.current_round():
                return cst.ROUND_IN_PROGRESS

        if self == self.tournament.current_round():
            return cst.ROUND_COMPLETE
        return cst.ROUND_FINISHED

    def start_time(self) -> datetime:
        """
        Return the start time of the round. None is returned if the
        round is not started.
        """
        if self.status == cst.ROUND_WAITING_DRAW:
            return None

        for team in self.teams():
            start = copy.deepcopy(team.result(self.number).start)

        return start

    def nb_teams(self):
        """
        Return the number of teams playing (removes BYE and FORFEIT).
        """
        nb = 0
        for team in self.teams():
            if team.result(self.number).result not in [cst.BYE, cst.FORFEIT]:
                nb += 1

        return nb

    def matches(self) -> list:
        """
        Return the matches of this round as a list of team numbers
        (BYE are not included).

        ex: [[1, 5], [2, 4], [3, 6]]
        """
        l = []
        matches = []
        if self.status != cst.ROUND_WAITING_DRAW:
            for team in self.teams():
                if team.id not in l:
                    l.append(team.id)

                    m = team.result(self.number)
                    for a in m.opponent_ids:
                        l.append(a)

                    if m.opponent_ids != []:
                        matches.append(sorted([team.id] + m.opponent_ids))

        return matches

    def byes(self) -> list:
        """
        Return the list of BYE in this round.
        """
        byes = []
        if self.status != cst.ROUND_WAITING_DRAW:
            for team in self.teams():
                if team.result(self.number).result == cst.BYE:
                    byes.append(team)

        return sorted(byes)

    def teams(self) -> list:
        """
        Return the list of teams that have a match defined for this round
        including BYE and FORFEIT. Except in exceptional cases (adding teams
        when a tournament has already started), a match is always defined
        for each round.
        """
        teams = []
        for team in self.tournament.teams():
            if team.round_exists(self.number):
                teams.append(team)

        return teams

    def forfeits(self) -> list:
        """
        Return the list of FORFEIT in this round.
        """
        forfeits = []
        if self.status != cst.ROUND_WAITING_DRAW:
            for team in self.teams():
                if team.result(self.number).result == cst.FORFEIT:
                    forfeits.append(team)

        return sorted(forfeits)

    def incomplete_teams(self) -> list:
        """
        Return the list of teams whose results of the current
        match have not been entered.
        """
        incomplete = []
        for team in self.teams():
            if team.status == cst.TEAM_IN_PROGRESS:
                incomplete.append(team)

        return incomplete

    def start(self, matches: dict, byes: list = ()) -> None:
        """
        Start the round with a given draw.

        :param matches: association location - match
        :param byes: list of team identifiers set to BYE
        """
        if self.status != cst.ROUND_WAITING_DRAW:
            if self.status == cst.ROUND_FINISHED:
                raise StatusError(f"Round n°{self.number} is completed")
            else:
                raise StatusError(f"Round n°{self.number} is in progress")
        start = datetime.now()

        l = []
        # Add the matches
        for location, match in matches.items():
            for num in match:
                l.append(num)
                opponents = [team for team in match if team != num]
                self.tournament.team(num)._add_round(start, opponents, location=location)

        # Add the byes
        for num in byes:
            l.append(num)
            self.tournament.team(num)._add_round(start, result=cst.BYE)

        # Add the forfeits among the remaining teams of the tournament
        for team in self.tournament.teams():
            if team.id not in l:
                team._add_round(start, result=cst.FORFEIT)

        self.tournament.changed = True

    def add_team(self, team, match_result: str, try_create_match: bool = True, location: int = None) -> None:
        """
        Add a team to the round after it has started and set it match result. This method
        allows to register new teams during the round.

        If the number of BYEs thus created is sufficient and `try_create_match`=True, a new
        match is created, and the corresponding BYEs are then deleted (`match_result` is
        ignored).
        """
        if isinstance(team, int):
            team = self.tournament.team(team)

        if self.status == cst.ROUND_WAITING_DRAW:
            raise StatusError(f"Round n°{self.number} is not started (call `start`)")
        if team.round_exists(self.number):
            raise ValueError(f"Team n°{team.id} already participates to round n°{self.number}")
        if match_result not in [cst.FORFEIT, cst.BYE]:
            raise ResultError("Can only add team with BYE of FORFEIT result")
        if try_create_match and not location:
            location = self.locations()[-1] + 1

        if self.tournament.nb_rounds() != 1:
            # Check that all previous rounds have been completed
            for num in range(1, self.number):
                team.result(num)

        if self.status in [cst.ROUND_IN_PROGRESS, cst.ROUND_COMPLETE]:
            if match_result == cst.BYE:
                new_nb_byes = len(self.byes()) + 1
                if new_nb_byes % self.tournament.teams_by_match == 0 and try_create_match:
                    byes = [t.id for t in self.byes()]
                    # Modify all the existing byes
                    for adv in self.byes():
                        m = MatchResult(self.start_time(), [team.id] + [num for num in byes if num != adv.id])
                        m.location = location
                        adv._results[self.number - 1] = m

                    # Add the team
                    team._add_round(self.start_time(), byes, location=location)
                    self.tournament.changed = True
                else:
                    # Add an extra bye
                    team._add_round(self.start_time(), result=cst.BYE)
                    self.tournament.changed = True
            else:
                team._add_round(self.start_time(), result=cst.FORFEIT)
                self.tournament.changed = True
        else:
            team._add_round(self.start_time(), result=cst.FORFEIT)
            self.tournament.changed = True

    def add_result(self, match_result: dict, end: datetime = None) -> None:
        """
        Register new score for a match.

        :param match_result: dictionary of team identifier and points
        :param end: end match time
        """
        # Check: round started
        if self.status == cst.ROUND_WAITING_DRAW:
            raise StatusError(f"Round n°{self.number} is not started")

        # Check that the match exists
        match = sorted(match_result.keys())

        if match not in self.matches():
            raise ResultError(f"Match '{match}' is not created")

        # Check it is not a bye match
        if cst.BYE in match:
            raise ResultError("BYE team points cannot be changed")

        # Search for the winners
        winners = []
        winners_pts = max(match_result.values())
        for num, pts in match_result.items():
            if pts == winners_pts:
                winners.append(num)

        # Check: number of points
        if winners_pts < self.tournament.points_by_match:
            raise ResultError(f"At least one team must have points greater than or equal to{self.tournament.points_by_match}")

        for num in match_result:
            if num in winners:
                result = cst.WON
            else:
                result = cst.LOST
            self.tournament.team(int(num))._modify_round(self.number, match_result[num], result, end)

        self.tournament.changed = True

    def locations(self) -> list:
        """
        Return the list of location used for this round.
        """
        locations = []
        for team in self.teams():
            number = team.result(self.number).location
            if number not in locations and number is not None:
                locations.append(number)

        return sorted(locations)

    def is_location_available(self, location: int) -> bool:
        """
        Check that the match location is not assigned to a match.

        :param location: location id
        """
        if location in self.locations():
            return False
        else:
            return True

    def delete(self) -> None:
        """
        Delete, for each team, the matches corresponding to this round
        (used to delete a round).
        """
        if self.status != cst.ROUND_WAITING_DRAW:
            for team in self.teams():
                team._remove_round(self.number)
            self.tournament.changed = True
