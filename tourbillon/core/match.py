# -*- coding: UTF-8 -*-

"""Match result class definition"""

from datetime import datetime, timedelta

from . import cst


# Persistence is retro-compatible with the historical YAML archives, which use
# French keys and French result values. The conversion happens only at the
# (de)serialization boundary (``Match.load`` / ``Match.dump``); the in-memory
# representation is fully English.
_LEGACY_TO_KEY = {
    'points': 'points',
    'etat': 'state',
    'debut': 'start',
    'fin': 'end',
    'adversaires': 'opponents',
    'piquet': 'location',
}
_KEY_TO_LEGACY = {value: key for key, value in _LEGACY_TO_KEY.items()}

_LEGACY_TO_RESULT = {
    'chapeau': cst.BYE,
    'gagné': cst.WON,
    'perdu': cst.LOST,
    'forfait': cst.FORFEIT,
}
_RESULT_TO_LEGACY = {value: key for key, value in _LEGACY_TO_RESULT.items()}


class MatchResult:
    """
    A match represent the team result on a given round.
    """

    def __init__(self, start=datetime.now(), opponent_ids=()):
        self.data = {'points': 0,
                     'state': None,
                     'start': start,
                     'end': None,
                     'opponents': opponent_ids or [],
                     'location': None}

    def __str__(self):
        return f"""
        MatchResult
            Start        : {self.start}
            Result       : {self.result}
            Points       : {self.points}
            Competitors  : {self.opponent_ids}

            Status       : {self.status}
        """

    def load(self, data: dict) -> None:
        """
        Retro-compatible method to load the data of a match from a legacy
        (French-keyed) dictionary. (Used by the loading function of a tournament)

        This function has no protection, the input data must be correct.

        :param data: legacy match data (French keys and result values)
        """
        for legacy_key, value in data.items():
            key = _LEGACY_TO_KEY.get(legacy_key)
            if key is None:
                continue
            if key == 'state':
                value = _LEGACY_TO_RESULT.get(value, value)
            self.data[key] = value
        # Old archives store 'duree' (duration) instead of 'fin' (end).
        if 'duree' in data:
            if data['duree']:
                self.data['end'] = self.data['start'] + data['duree']
            elif self.data['opponents'] == []:
                self.data['end'] = self.data['start']

    def dump(self) -> dict:
        """
        Return the match data as a legacy (French-keyed) dictionary, ready to be
        persisted. Keeps the historical archive format (French keys and result
        values) for backward compatibility.
        """
        legacy = {}
        for key, legacy_key in _KEY_TO_LEGACY.items():
            value = self.data[key]
            if key == 'state':
                value = _RESULT_TO_LEGACY.get(value, value)
            legacy[legacy_key] = value
        return legacy

    @property
    def status(self) -> str:
        """
        Return the match status:

        MATCH_IN_PROGRESS => match is not started or in progress
        MATCH_FINISHED    => match is finished (end timestamps is set)
        """
        if self.data['state'] == cst.BYE or self.data['state'] == cst.FORFEIT:
            return cst.MATCH_FINISHED
        elif self.data['end'] is None:
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
        if self.data['state'] == cst.FORFEIT:
            raise ValueError("Points of FORFEIT match cannot be changed")
        self.data['points'] = value

    @property
    def result(self) -> str:
        """
        Return the result.
        """
        return self.data['state']

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
        if value in [cst.WON, cst.LOST] and self.data['end'] is None:
            self.data['end'] = datetime.now()
        if value in [cst.BYE, cst.FORFEIT]:
            self.data['opponents'] = []
            self.data['end'] = self.data['start']
        if value in [cst.FORFEIT]:
            self.data['points'] = 0

        self.data['state'] = value

    @property
    def start(self) -> datetime:
        """
        Return start timestamp.
        """
        return self.data['start']

    @start.setter
    def start(self, value: datetime) -> None:
        """
        Set start timestamp.

        :param value: start timestamp as datetime instance
        """
        self.data['start'] = value

    @property
    def duration(self) -> timedelta:
        """
        Return the match duration (end timestamp - start timestamp).
        """
        if self.data['end'] is None or self.data['end'] == self.data['start']:
            return None
        else:
            return self.data['end'] - self.data['start']

    @duration.setter
    def duration(self, value: timedelta) -> None:
        """
        Set the match duration.

        :param value: match duration
        """
        if self.data['state'] in [cst.BYE, cst.FORFEIT]:
            raise ValueError("Duration of a BYE or FORFEIT match cannot be modified")
        self.data['end'] = self.data['start'] + value

    @property
    def end(self) -> datetime:
        """
        Return end timestamp.
        """
        return self.data['end']

    @end.setter
    def end(self, value: datetime) -> None:
        """
        Set end timestamp.

        :param value: end timestamp as datetime instance
        """
        if self.data['state'] in [cst.BYE, cst.FORFEIT]:
            raise ValueError("End date of a BYE or FORFEIT match cannot be changed")
        self.data['end'] = value

    @property
    def opponent_ids(self) -> list:
        """
        Return the list of competitor team identifiers.
        """
        return self.data['opponents']

    @opponent_ids.setter
    def opponent_ids(self, value: list) -> None:
        """
        Set competitor team identifiers.
        """
        for num in value:
            if not isinstance(num, int):
                raise TypeError(f"'{num}' is not an integer")
        if self.data['state'] in [cst.BYE, cst.FORFEIT]:
            raise ValueError("Can not add competitors for a BYE ou FORFEIT match")
        self.data['opponents'] = value

    @property
    def location(self) -> int:
        """
        Return the match location.
        """
        return self.data['location']

    @location.setter
    def location(self, value: int) -> None:
        """
        Set the match location.
        """
        self.data['location'] = value

