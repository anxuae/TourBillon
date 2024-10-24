# -*- coding: UTF-8 -*-

"""Match class definition"""

from datetime import datetime, timedelta

from . import cst


class Match:
    """
    A match represent the team result on a given round.
    """

    def __init__(self, debut=datetime.now(), adversaires=()):
        self.data = {'points': 0,
                     'etat': None,
                     'debut': debut,
                     'fin': None,
                     'adversaires': adversaires or [],
                     'piquet': None}

    def __str__(self):
        return f"""
        Match
            Start        : {self.debut}
            Result       : {self.etat}
            Points       : {self.points}
            Competitors  : {self.adversaires}

            Status       : {self.statut}
        """

    def charger(self, data: dict) -> None:
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
    def statut(self) -> str:
        """
        Return the match status:

        M_EN_COURS => match is not started or in progress
        M_TERMINEE => match is finished (end timestamps is set)
        """
        if self.data['etat'] == cst.CHAPEAU or self.data['etat'] == cst.FORFAIT:
            return cst.M_TERMINEE
        elif self.data['fin'] is None:
            return cst.M_EN_COURS
        else:
            return cst.M_TERMINEE

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
        if self.data['etat'] == cst.FORFAIT:
            raise ValueError("Points of FORFEIT match cannot be changed")
        self.data['points'] = value

    @property
    def etat(self) -> str:
        """
        Return the result.
        """
        return self.data['etat']

    @etat.setter
    def etat(self, value: str) -> None:
        """
        Set the match result:
            * VICTORY
            * LOSS
            * BYE
            * FORFEIT
        
        :param value: result to set
        """
        if value not in [cst.GAGNE, cst.PERDU, cst.CHAPEAU, cst.FORFAIT]:
            raise TypeError("Match result must be one of the following value:"
                            f"{cst.GAGNE}, {cst.PERDU}, {cst.CHAPEAU}, {cst.FORFAIT}")
        if value in [cst.GAGNE, cst.PERDU] and self.data['fin'] is None:
            self.data['fin'] = datetime.now()
        if value in [cst.CHAPEAU, cst.FORFAIT]:
            self.data['adversaires'] = []
            self.data['fin'] = self.data['debut']
        if value in [cst.FORFAIT]:
            self.data['points'] = 0

        self.data['etat'] = value

    @property
    def debut(self) -> datetime:
        """
        Return start timestamp.
        """
        return self.data['debut']

    @debut.setter
    def debut(self, value: datetime) -> None:
        """
        Set start timestamp.

        :param value: start timestamp as datetime instance
        """
        self.data['debut'] = value

    @property
    def duree(self) -> timedelta:
        """
        Return the match duration (end timestamp - start timestamp).
        """
        if self.data['fin'] is None or self.data['fin'] == self.data['debut']:
            return None
        else:
            return self.data['fin'] - self.data['debut']

    @duree.setter
    def duree(self, value: timedelta) -> None:
        """
        Set the match duration.

        :param value: match duration
        """
        if self.data['etat'] in [cst.CHAPEAU, cst.FORFAIT]:
            raise ValueError("Duration of a BYE or FORFEIT match cannot be modified")
        self.data['fin'] = self.data['debut'] + value

    @property
    def fin(self) -> datetime:
        """
        Return end timestamp.
        """
        return self.data['fin']

    @fin.setter
    def fin(self, value: datetime) -> None:
        """
        Set end timestamp.

        :param value: end timestamp as datetime instance
        """
        if self.data['etat'] in [cst.CHAPEAU, cst.FORFAIT]:
            raise ValueError("End date of a BYE or FORFEIT match cannot be changed")
        self.data['fin'] = value

    @property
    def adversaires(self) -> list:
        """
        Return the list of team's competitors.
        """
        return self.data['adversaires']

    @adversaires.setter
    def adversaires(self, value: list) -> None:
        """
        Set competitors list.
        """
        for num in value:
            if not isinstance(num, int):
                raise TypeError(f"'{num}' is not an integer")
        if self.data['etat'] in [cst.CHAPEAU, cst.FORFAIT]:
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
