# -*- coding: UTF-8 -*-

"""Player class definition"""

import difflib
import atexit
import os.path as osp
from datetime import datetime

from ..config import Singleton


SPECIAL_CHAR = {'é': 'e',
                'è': 'e',
                'ë': 'e',
                'ê': 'e',
                'à': 'a',
                'ç': 'c',
                'ï': 'i',
                'î': 'i',
                ' ': '-'}


class PlayerHistory(metaclass=Singleton):

    def __init__(self, filename=None, load=True):
        self.filename = None
        self.history = {}
        if filename and load:
            self.load(filename)

        # Save history before exit
        atexit.register(self.save)

    @classmethod
    def make_history_key(cls, prenom: str, nom: str) -> str:
        """
        Sanitize firstname and lastname to build an key for the players
        history.
        """
        prenom = prenom.lower().strip()
        nom = nom.lower().strip()
        for spe, rep in SPECIAL_CHAR.items():
            prenom = prenom.replace(spe, rep)
            nom = nom.replace(spe, rep)
        return f"{prenom}_{nom}"

    def load(self, filename: str):
        """
        Load history file.
        """
        if osp.isfile(filename):
            with open(filename, 'r', encoding='utf-8') as fp:
                lignes = fp.readlines()
        else:
            lignes = []

        self.history = {}
        for ligne in lignes:
            ligne = ligne.strip()
            l = ligne.split(',')
            self.history.setdefault(self.make_history_key(l[1], l[2]), []).append((l[1], l[2], l[3], l[4]))

        self.filename = osp.abspath(filename)

    def save(self):
        """
        Save history file.
        """
        if self.history and self.filename:
            ids = sorted(self.history.keys())
            with open(self.filename, 'w', encoding='utf-8') as fp:
                for player_id in ids:
                    for data in self.history[player_id]:
                        line = player_id + ',' + ','.join(data) + "\n"
                        fp.write(line)

    def get(self, history_key: str, default="__NOT-A-VALUE__"):
        """
        Get the entry with given history key.
        """
        if default == "__NOT-A-VALUE__":
            return self.history[history_key]
        return self.history.get(history_key, default)

    def add(self, prenom: str, nom: str, date: str) -> str:
        """
        Add new history entry and retrun the associated history key.
        """
        history_key = self.make_history_key(prenom, nom)
        self.history.setdefault(history_key, []).append([prenom, nom, "", date])
        return history_key

    def remove(self, history_key: str):
        """
        Remove entry with given history key.
        """
        return self.history.pop(history_key, None)

    def complete(self, firstname, lastname='', n=3):
        """
        Find best match for given player firstname/lastname.
        """
        search_key = self.make_history_key(firstname, lastname)
        matches = []
        for key in difflib.get_close_matches(search_key, self.history.keys(), n=n, cutoff=0.65):
            if key == search_key:
                return self.history[key]
            matches.extend(self.history[key])
        return matches


class Player:
    """
    Class which represent a player for a tournament.
    """

    def __init__(self, prenom, nom, date_ajout=None):
        self.data = []
        self._update(prenom, nom, date_ajout)

    def __str__(self):
        return f"{self.data[1]} {self.data[2]}"

    def __eq__(self, other):
        if isinstance(other, Player):
            comparateur = other.key
        else:
            comparateur = str(other)
        if self.key == comparateur:
            return True
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, Player):
            comparateur = other.key
        else:
            comparateur = str(other)
        if self.key != comparateur:
            return True
        else:
            return False

    def _update(self, prenom: str = None, nom: str = None, date_modification=None):
        new_prenom = prenom if prenom is not None else self.prenom
        new_nom = nom if nom is not None else self.nom
        if date_modification is not None:
            if isinstance(date_modification, str):
                date_modification = datetime.strptime(date_modification, '%d/%m/%Y')
            elif not isinstance(date_modification, datetime):
                raise TypeError(f"'{date_modification}' shall be 'datetime' or '%d/%m/%Y' string formated")

        date = None
        hist = PlayerHistory()
        if self.data and hist.get(self.key, None):
            # Remove previous ID if exists
            i = 0
            index = None
            for donnee in hist.get(self.key):
                if donnee[0] == self.data[1] and donnee[1] == self.data[2]:
                    index = i
                    break
                i += 1
            if index is not None:
                old_data = hist.get(self.key).pop(index)
                # If a date is given, keep the oldest
                # by comparing with that of the history (allows
                # to create a history by loading history files)
                date = old_data[3]
                if date_modification is not None and date_modification < datetime.strptime(old_data[3], '%d/%m/%Y'):
                    date = date_modification.strftime('%d/%m/%Y')
        elif date_modification is not None and date is None:
            date = date_modification.strftime('%d/%m/%Y')
        elif date is None:
            date = datetime.now().strftime('%d/%m/%Y')

        new_history_key = hist.add(new_prenom, new_nom, date)
        self.data = [new_history_key, new_prenom, new_nom]

    @property
    def key(self):
        """
        Text without special characters representing the player.
        Note: the key may not be unique
        """
        return self.data[0]

    @property
    def prenom(self) -> str:
        """
        Return the player firstname.
        """
        return self.data[1]

    @prenom.setter
    def prenom(self, value: str) -> None:
        """
        Set the player firstname.
        """
        self._update(prenom=value)

    @property
    def nom(self) -> str:
        """
        Return the player lastname.
        """
        return self.data[2]

    @nom.setter
    def nom(self, value: str) -> None:
        """
        Set the player lastname.
        """
        self._update(nom=value)
