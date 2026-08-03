# -*- coding: UTF-8 -*-

"""Player class definition."""


SPECIAL_CHAR = {'é': 'e',
                'è': 'e',
                'ë': 'e',
                'ê': 'e',
                'à': 'a',
                'ç': 'c',
                'ï': 'i',
                'î': 'i',
                ' ': '-'}


def make_key(firstname: str, lastname: str) -> str:
    """Sanitize firstname and lastname to build a comparison key.

    Note: the key may not be unique (two different players can share it).
    """
    firstname = firstname.lower().strip()
    lastname = lastname.lower().strip()
    for spe, rep in SPECIAL_CHAR.items():
        firstname = firstname.replace(spe, rep)
        lastname = lastname.replace(spe, rep)
    return f"{firstname}_{lastname}"


class Player:
    """
    Class which represent a player for a tournament.
    """

    def __init__(self, firstname, lastname):
        self.data = []
        self._update(firstname, lastname)

    def __str__(self):
        return f"{self.data[1]} {self.data[2]}"

    def __eq__(self, other):
        comparator = other.key if isinstance(other, Player) else str(other)
        return self.key == comparator

    def __ne__(self, other):
        return not self.__eq__(other)

    def _update(self, firstname: str = None, lastname: str = None):
        new_firstname = firstname if firstname is not None else self.firstname
        new_lastname = lastname if lastname is not None else self.lastname
        self.data = [make_key(new_firstname, new_lastname), new_firstname, new_lastname]

    @property
    def key(self):
        """
        Text without special characters representing the player.
        Note: the key may not be unique
        """
        return self.data[0]

    @property
    def firstname(self) -> str:
        """
        Return the player firstname.
        """
        return self.data[1]

    @firstname.setter
    def firstname(self, value: str) -> None:
        """
        Set the player firstname.
        """
        self._update(firstname=value)

    @property
    def lastname(self) -> str:
        """
        Return the player lastname.
        """
        return self.data[2]

    @lastname.setter
    def lastname(self, value: str) -> None:
        """
        Set the player lastname.
        """
        self._update(lastname=value)
