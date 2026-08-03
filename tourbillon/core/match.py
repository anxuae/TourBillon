# -*- coding: UTF-8 -*-

"""Match class definition"""

from datetime import datetime, timedelta

from . import cst


class Match:
    """
    A match represent the team result on a given round.
    """

    def __init__(self, start=datetime.now(), opponents=()):
        # The dict keys are persisted as-is in the YAML save files: DO NOT
        # rename them to keep retro-compatibility with the historical archives.
        self.data = {'points': 0,
                     'etat': None,
                     'debut': start,
                     'fin': None,
                     'adversaires': opponents or [],
                     'piquet': None}

    def __str__(self):
        return f"""
        Match
            Start        : {self.start}
            Result       : {self.result}
            Points       : {self.points}
            Competitors  : {self.opponents}

            Status       : {self.status}
        """

    def load(self, data: dict) -> None:
        """
        Retro-compatible method to load the data of a match via a dictionary.
        (Used by the loading function of a tournament)

        This function has no protection, the input data must be correct.

        :param data: match data
        """
        for k, v in data.items():
            if k in self.data:
                self.data[k] = v
        if 'duree' in data:
            if data['duree']:
                self.data['fin'] = self.data['debut'] + data['duree']
            elif self.data['adversaires'] == []:
                self.data['fin'] = self.data['debut']

    @property
    def status(self) -> str:
        """
        Return the match status:

        MATCH_IN_PROGRESS => match is not started or in progress
        MATCH_FINISHED    => match is finished (end timestamps is set)
        """
        if self.data['etat'] == cst.BYE or self.data['etat'] == cst.FORFEIT:
            return cst.MATCH_FINISHED
        elif self.data['fin'] is None:
            return cst.MATCH_IN_PROGRESS
        else:
            return cst.MATCH_FINISHED

    @property
    def points(self) -> int:
        """
        Return the number of point.
        """
        return self.data['points']

    @points.setter
    def points(self, value: int) -> None:
        """
        Set the number of point.

        :param value: points to set
        """
        if not isinstance(value, int) or value < 0:
            raise TypeError("Points must be a positive or zero integer")
        if self.data['etat'] == cst.FORFEIT:
            raise ValueError("Points of FORFEIT match cannot be changed")
        self.data['points'] = value

    @property
    def result(self) -> str:
        """
        Return the result.
        """
        return self.data['etat']

    @result.setter
    def result(self, value: str) -> None:
        """
        Set the match result:
            * WON
            * LOST
            * BYE
            * FORFEIT

        :param value: result to set
        """
        if value not in [cst.WON, cst.LOST, cst.BYE, cst.FORFEIT]:
            raise TypeError("Match result must be one of the following value:"
                            f"{cst.WON}, {cst.LOST}, {cst.BYE}, {cst.FORFEIT}")
        if value in [cst.WON, cst.LOST] and self.data['fin'] is None:
            self.data['fin'] = datetime.now()
        if value in [cst.BYE, cst.FORFEIT]:
            self.data['adversaires'] = []
            self.data['fin'] = self.data['debut']
        if value in [cst.FORFEIT]:
            self.data['points'] = 0

        self.data['etat'] = value

    @property
    def start(self) -> datetime:
        """
        Return start timestamp.
        """
        return self.data['debut']

    @start.setter
    def start(self, value: datetime) -> None:
        """
        Set start timestamp.

        :param value: start timestamp as datetime instance
        """
        self.data['debut'] = value

    @property
    def duration(self) -> timedelta:
        """
        Return the match duration (end timestamp - start timestamp).
        """
        if self.data['fin'] is None or self.data['fin'] == self.data['debut']:
            return None
        else:
            return self.data['fin'] - self.data['debut']

    @duration.setter
    def duration(self, value: timedelta) -> None:
        """
        Set the match duration.

        :param value: match duration
        """
        if self.data['etat'] in [cst.BYE, cst.FORFEIT]:
            raise ValueError("Duration of a BYE or FORFEIT match cannot be modified")
        self.data['fin'] = self.data['debut'] + value

    @property
    def end(self) -> datetime:
        """
        Return end timestamp.
        """
        return self.data['fin']

    @end.setter
    def end(self, value: datetime) -> None:
        """
        Set end timestamp.

        :param value: end timestamp as datetime instance
        """
        if self.data['etat'] in [cst.BYE, cst.FORFEIT]:
            raise ValueError("End date of a BYE or FORFEIT match cannot be changed")
        self.data['fin'] = value

    @property
    def opponents(self) -> list:
        """
        Return the list of team's competitors.
        """
        return self.data['adversaires']

    @opponents.setter
    def opponents(self, value: list) -> None:
        """
        Set competitors list.
        """
        for num in value:
            if not isinstance(num, int):
                raise TypeError(f"'{num}' is not an integer")
        if self.data['etat'] in [cst.BYE, cst.FORFEIT]:
            raise ValueError("Can not add competitors for a BYE ou FORFEIT match")
        self.data['adversaires'] = value

    @property
    def location(self) -> int:
        """
        Return the match location.
        """
        return self.data['piquet']

    @location.setter
    def location(self, value: int) -> None:
        """
        Set the match location.
        """
        self.data['piquet'] = value
