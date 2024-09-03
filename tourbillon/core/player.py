# -*- coding: UTF-8 -*-

"""Player class definition"""

import os.path as osp
from datetime import datetime
import atexit

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

    def __init__(self, filename=None):
        self.filename = None
        self.history = {}
        if filename:
            self.load(filename)

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

        # Save history before exit
        atexit.register(self.save)

    def save(self):
        """
        Save history file.
        """
        if self.history:
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

    def add(self, prenom: str, nom: str, age: int, date: str) -> str:
        """
        Add new history entry and retrun the associated history key.
        """
        history_key = self.make_history_key(prenom, nom)
        self.history.setdefault(history_key, []).append([prenom, nom, str(age), date])
        return history_key

    def remove(self, history_key: str):
        """
        Remove entry with given history key.
        """
        return self.history.pop(history_key, None)

    def complete(self, firstname, lastname=''):
        """
        Find best match for given player firstname/lastname.
        """
        debut_id = self.make_history_key(firstname, lastname)
        if debut_id.endswith('_'):
            debut_id = debut_id[:-1]

        joueur_ids = self._dichotomie(debut_id)

        if joueur_ids is None:
            return []
        else:
            l = []
            map(l.extend, [self.history[ji] for ji in joueur_ids])
            return l

    def _dichotomie(self, texte):
        match = []
        if self.history and texte != '':
            ids = sorted(self.history.keys())
            debut, fin = 0, len(self.history) - 1
            while debut <= fin:
                milieu = (debut + fin) // 2
                if ids[milieu].startswith(texte):
                    trouve = milieu
                    # L'élément du milieu de la liste correspond
                    while milieu >= 0 and ids[milieu].startswith(texte):
                        # Recherche du premier element correspondant
                        match.append(ids[milieu])
                        milieu -= 1
                    milieu = trouve + 1
                    while milieu >= 0 and ids[milieu].startswith(texte):
                        # Recherche du dernier element correspondant
                        match.append(ids[milieu])
                        milieu += 1
                    return match
                elif texte < ids[milieu]:
                    # Recherche avant le milieu
                    fin = milieu - 1
                else:
                    # Recherche après le milieu
                    debut = milieu + 1


class Player:

    def __init__(self, prenom, nom, age, date_ajout=None):
        self.data = []
        self._update(prenom, nom, age, date_ajout)

    def __str__(self):
        return f"{self.data[1]} {self.data[2]}"

    def __eq__(self, other):
        if isinstance(other, Player):
            comparateur = other.cle()
        else:
            comparateur = str(other)
        if self.cle() == comparateur:
            return True
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, Player):
            comparateur = other.cle()
        else:
            comparateur = str(other)
        if self.cle() != comparateur:
            return True
        else:
            return False

    def _update(self, prenom=None, nom=None, age=None, date_modification=None):
        new_prenom = prenom if prenom is not None else self.prenom
        new_nom = nom if nom is not None else self.nom
        new_age = age if age is not None else self.age
        if date_modification is not None:
            if isinstance(date_modification, str):
                date_modification = datetime.strptime(date_modification, '%d/%m/%Y')
            elif not isinstance(date_modification, datetime):
                raise TypeError(
                    f"'{date_modification}' doit être de type 'datetime' ou une chaine de format '%d/%m/%Y'")

        date = None
        hist = PlayerHistory()
        if self.data and hist.get(self.cle(), None):
            # Remove previous ID if exists
            i = 0
            index = None
            for donnee in hist.get(self.cle()):
                if donnee[0] == self.data[1] and donnee[1] == self.data[2]:
                    index = i
                    break
                i += 1
            if index is not None:
                old_data = hist.get(self.cle()).pop(index)
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

        new_history_key = hist.add(new_prenom, new_nom, new_age, date)
        self.data = [new_history_key, new_prenom, new_nom, new_age]

    def cle(self):
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

    @property
    def age(self) -> int:
        """
        Return the player age.
        """
        return self.data[3]

    @age.setter
    def age(self, value: int) -> None:
        """
        Set the player age.
        """
        self._update(age=value)
