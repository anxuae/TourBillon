# -*- coding: UTF-8 -*-

"""Player class definition"""

import os.path as osp
from datetime import datetime
import atexit


HISTORIQUE = {}
FICHIER_HISTORIQUE = None
CARACTERES_SPECIAUX = {'é': 'e',
                       'è': 'e',
                       'ë': 'e',
                       'ê': 'e',
                       'à': 'a',
                       'ç': 'c',
                       'ï': 'i',
                       'î': 'i',
                       ' ': '-'}


def make_history_key(prenom: str, nom: str) -> str:
    """
    Sanitize firstname and lastname to build an key for the players
    history.
    """
    prenom = prenom.lower().strip()
    nom = nom.lower().strip()
    for spe, rep in CARACTERES_SPECIAUX.items():
        prenom.replace(spe, rep)
        nom.replace(spe, rep)
    return f"{prenom}_{nom}"


def charger_historique(fichier):
    global HISTORIQUE, FICHIER_HISTORIQUE
    if osp.isfile(fichier):
        with open(fichier, 'r', encoding='utf-8') as fp:
            lignes = fp.readlines()
    else:
        lignes = []

    HISTORIQUE = {}
    for ligne in lignes:
        ligne = ligne.strip()
        l = ligne.split(',')

        HISTORIQUE.setdefault(make_history_key(l[1], l[2]), []).append((l[1], l[2], l[3], l[4]))

    FICHIER_HISTORIQUE = osp.abspath(fichier)

    # Enregistrer l'historique avant de quitter
    atexit.register(enregistrer_historique)


def enregistrer_historique():
    if HISTORIQUE:
        ids = sorted(HISTORIQUE.keys())
        with open(FICHIER_HISTORIQUE, 'w', encoding='utf-8') as fp:
            for joueur_id in ids:
                for donnee in HISTORIQUE[joueur_id]:
                    ligne = joueur_id + ',' + ','.join(donnee) + "\n"
                    fp.write(ligne)


class NomCompleteur:

    def __init__(self):
        pass

    def completer(self, prenom, nom=''):
        debut_id = make_history_key(prenom, nom)
        if debut_id.endswith('_'):
            debut_id = debut_id[:-1]

        joueur_ids = self._dichotomie(debut_id)

        if joueur_ids is None:
            return []
        else:
            l = []
            map(l.extend, [HISTORIQUE[ji] for ji in joueur_ids])
            return l

    def _dichotomie(self, texte):
        match = []
        if HISTORIQUE and texte != '':
            ids = sorted(HISTORIQUE.keys())
            debut, fin = 0, len(HISTORIQUE) - 1
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

    def __init__(self, prenom, nom, age, **kwrd):
        self._pn = prenom
        self._n = nom
        self._a = age
        self.data = [make_history_key(prenom, nom), prenom, nom, age]
        self._enregistrer(kwrd.get('date_ajout'))

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

    def _enregistrer(self, date_modification=None):
        joueur_id = make_history_key(self._pn, self._n)
        if date_modification is not None:
            if isinstance(date_modification, str):
                date_modification = datetime.strptime(date_modification, '%d/%m/%Y')
            elif not isinstance(date_modification, datetime):
                raise TypeError(f"'{date_modification}' doit être de type 'datetime' ou une chaine de format '%d/%m/%Y'")

        date = None
        if self.cle() in HISTORIQUE:
            # Suppression de l'ancien ID
            i = 0
            index = None
            for donnee in HISTORIQUE[self.cle()]:
                if donnee[1] == self.data[1] and donnee[2] == self.data[2]:
                    index = i
                    break
                i += 1
            if index:
                j = HISTORIQUE[self.cle()].pop(index)
                # Si une date est donnée, garder la plus ancienne
                # en comparant avec celle de l'historique (permet
                # de créer un historique en chargeant des fichiers)
                date = j[3]
                if date_modification is not None and date_modification < datetime.strptime(j[3], '%d/%m/%Y'):
                    date = date_modification.strftime('%d/%m/%Y')
        elif date_modification is not None and date is None:
            date = date_modification.strftime('%d/%m/%Y')
        elif date is None:
            date = datetime.now().strftime('%d/%m/%Y')

            HISTORIQUE.setdefault(joueur_id, []).append([self._pn, self._n, str(self._a), date])

        self.data = [joueur_id, self._pn, self._n, str(self._a)]

    def cle(self):
        """Text sans caractères spéciaux représentant l'équipe.
        Note: la clé peut ne pas être unique
        """
        return self.data[0]

    def prenom():
        def fget(self):
            return self.data[1]

        def fset(self, prenom):
            self._pn = prenom
            self._enregistrer()
        return locals()

    prenom = property(**prenom())

    def nom():
        def fget(self):
            return self.data[2]

        def fset(self, nom):
            self._n = nom
            self._enregistrer()
        return locals()

    nom = property(**nom())

    def age():
        def fget(self):
            return self.data[3]

        def fset(self, age):
            self._a = age
            self._enregistrer()
        return locals()

    age = property(**age())
