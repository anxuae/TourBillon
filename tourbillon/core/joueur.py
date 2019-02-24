# -*- coding: UTF-8 -*-

"""Définitions des joueurs."""

import os.path as osp
import codecs
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
                       ' ': '_'}


def creer_id(prenom, nom):
    prenom = prenom.lower()
    prenom = prenom.strip()
    nom = nom.lower()
    nom = nom.strip()
    for spe, rep in CARACTERES_SPECIAUX.items():
        prenom.replace(spe, rep)
        nom.replace(spe, rep)
    nom = nom.replace(' ', '_')
    return unicode("%s_%s" % (prenom, nom))


def charger_historique(fichier):
    global HISTORIQUE, FICHIER_HISTORIQUE
    if osp.isfile(fichier):
        f = codecs.open(fichier, 'rb', 'utf-8')
        lignes = f.readlines()
        f.close()
    else:
        lignes = []

    HISTORIQUE = {}
    for ligne in lignes:
        ligne = unicode(ligne).strip()
        l = ligne.split(',')

        HISTORIQUE.setdefault(creer_id(l[1], l[2]), []).append((l[1], l[2], l[3], l[4]))

    FICHIER_HISTORIQUE = osp.abspath(fichier)

    # Enregistrer l'historique avant de quitter
    atexit.register(enregistrer_historique)


def enregistrer_historique():
    if HISTORIQUE:
        ids = HISTORIQUE.keys()
        ids.sort()

        f = codecs.open(FICHIER_HISTORIQUE, 'wb', 'utf-8')
        for joueur_id in ids:
            for donnee in HISTORIQUE[joueur_id]:
                ligne = joueur_id + ',' + ','.join(donnee) + "\n"
                f.write(ligne)
        f.close()


class NomCompleteur(object):

    def __init__(self):
        pass

    def completer(self, prenom, nom=''):
        debut_id = creer_id(prenom, nom)
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
            ids = HISTORIQUE.keys()
            ids.sort()

            debut, fin = 0, len(HISTORIQUE) - 1
            while debut <= fin:
                milieu = (debut + fin) / 2
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


class Joueur(object):

    def __init__(self, prenom, nom, age, **kwrd):
        self._pn = prenom
        self._n = nom
        self._a = age
        self.data = [creer_id(prenom, nom), prenom, nom, age]
        self._enregistrer(kwrd.get('date_ajout'))

    def __str__(self):
        return "%s %s" % (self.data[1], self.data[2])

    def __eq__(self, other):
        if type(other) == Joueur:
            comparateur = other.cle()
        else:
            comparateur = unicode(other)
        if self.cle() == comparateur:
            return True
        else:
            return False

    def __ne__(self, other):
        if type(other) == Joueur:
            comparateur = other.cle()
        else:
            comparateur = unicode(other)
        if self.cle() != comparateur:
            return True
        else:
            return False

    def _enregistrer(self, date_modification=None):
        joueur_id = creer_id(self._pn, self._n)
        if date_modification is not None:
            if type(date_modification) in [str, unicode]:
                date_modification = datetime.strptime(date_modification, '%d/%m/%Y')
            elif type(date_modification) != datetime:
                raise TypeError(u"'%s' doit être de type 'datetime' ou une chaine de format '%d/%m/%Y'" % date_modification)

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
