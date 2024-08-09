# -*- coding: UTF-8 -*-

"""Match class definition"""

from datetime import datetime, timedelta

from tourbillon.core import cst


class Match:
    """
    A represent a match result for a team on a given round.
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
        Return the progress status:
            * M_EN_COURS => match is not started or in progress
            * M_TERMINEE => match is finished (end timestamps is set)
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
            raise TypeError("Le nombre de points doit être un entier positif ou nul")
        if self.data['etat'] == cst.FORFAIT:
            raise ValueError("Le nombre de points d'une manche FORFAIT ne peut pas être modifié")
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
        Set the result:
            * VICTORY
            * LOSS
            * BYE
            * FORFEIT
        
        :param value: result to set
        """
        if value not in [cst.GAGNE, cst.PERDU, cst.CHAPEAU, cst.FORFAIT]:
            raise TypeError("L'état doit être une des valeur suivantes : "
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
        if not isinstance(value, datetime):
            raise TypeError("L'heure de début doit être de type 'datetime'")
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
        if not isinstance(value, timedelta):
            raise TypeError("La durée doit être de type 'timedelta'")
        if self.data['etat'] in [cst.CHAPEAU, cst.FORFAIT]:
            raise ValueError("La durée d'une manche CHAPEAU ou FORFAIT ne peut être modifiée")
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
        if not isinstance(value, datetime):
            raise TypeError("L'heure de fin doit être de type 'datetime'")
        if self.data['etat'] in [cst.CHAPEAU, cst.FORFAIT]:
            raise ValueError("La fin d'une manche CHAPEAU ou FORFAIT ne peut être modifiée")
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
        if not isinstance(value, (list, tuple)):
            raise TypeError("Les adversaires sont donnés sous forme de liste d'entiers")
        for num in value:
            if not isinstance(num, int):
                raise TypeError(f"'{num}' n'est pas un entier")
        if self.data['etat'] in [cst.CHAPEAU, cst.FORFAIT]:
            raise ValueError(f"Il n'y a pas d'adversaires pour une manche {cst.CHAPEAU} ou {cst.FORFAIT}")
        self.data['adversaires'] = value

    @property
    def piquet(self) -> int:
        """
        Return the match location.
        """
        return self.data['piquet']

    @piquet.setter
    def piquet(self, value: int) -> None:
        """
        Set the match location.
        """
        self.data['piquet'] = value