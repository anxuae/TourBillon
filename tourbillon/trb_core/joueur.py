#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Définitions des joueurs."""

#--- Import -------------------------------------------------------------------

import os.path as osp
import codecs
from datetime import datetime
import atexit

#--- Global Variables ---------------------------------------------------------

HISTORIQUE = None
FICHIER_HISTORIQUE = None

#--- Fonctions ----------------------------------------------------------------


def creer_id(prenom, nom):
    prenom = prenom.lower()
    prenom = prenom.strip()
    prenom = prenom.replace(' ', '_')
    nom = nom.lower()
    nom = nom.strip()
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
        HISTORIQUE[l[0]] = (l[1], l[2], l[3], l[4])

    FICHIER_HISTORIQUE = osp.abspath(fichier)

    # Enregistrer l'historique avant de quitter
    atexit.register(enregistrer_historique)


def enregistrer_historique():
    if HISTORIQUE:
        ids = HISTORIQUE.keys()
        ids.sort()

        f = codecs.open(FICHIER_HISTORIQUE, 'wb', 'utf-8')
        for joueur_id in ids:
            ligne = joueur_id + ',' + ','.join(HISTORIQUE[joueur_id]) + "\n"
            f.write(ligne)
        f.close()


#--- Classes -------------------------------------------------------------------


class NomCompleteur(object):
    def __init__(self):
        pass

    def completer(self, prenom, nom=''):
        debut_id = creer_id(prenom, nom)
        if debut_id.endswith('_'):
            debut_id = debut_id[:-1]

        joueur_id = self._dichotomie(debut_id)

        if joueur_id == None:
            return ('', '', '', '')
        else:
            if nom == '':
                return (HISTORIQUE[joueur_id][0], HISTORIQUE[joueur_id][1], HISTORIQUE[joueur_id][2], HISTORIQUE[joueur_id][3])
            else:
                return ('', HISTORIQUE[joueur_id][1], HISTORIQUE[joueur_id][2], HISTORIQUE[joueur_id][3])

    def _dichotomie(self, texte):
        if HISTORIQUE and texte != '':
            ids = HISTORIQUE.keys()
            ids.sort()

            debut, fin = 0, len(HISTORIQUE) - 1
            while debut <= fin:
                milieu = (debut + fin) / 2
                if ids[milieu].startswith(texte):
                    # L'élément du milieu de la liste correspond
                    # Recherche du premier element correspondant
                    while ids[milieu].startswith(texte):
                        milieu -= 1
                    return ids[milieu + 1]
                elif texte < ids[milieu]:
                    # Recherche avant le milieu
                    fin = milieu - 1
                else:
                    # Recherche après le milieu
                    debut = milieu + 1
        return None


class Joueur(object):
    def __init__(self, prenom, nom, age, **kwrd):
        self._pn = prenom
        self._n = nom
        self.age = age
        self.id = creer_id(self._pn, self._n)
        self._enregistrer(kwrd.get('date_ajout'))

    def __repr__(self):
        return "%s %s" % (self._pn, self._n)

    def __eq__(self, other):
        if type(other) == Joueur:
            comparateur = other.id
        else:
            comparateur = unicode(other)
        if self.id == comparateur:
            return True
        else:
            return False

    def __ne__(self, other):
        if type(other) == Joueur:
            comparateur = other.id
        else:
            comparateur = unicode(other)
        if self.id != comparateur:
            return True
        else:
            return False

    def nom():
        def fget(self):
            return self._n

        def fset(self, nom):
            self._n = nom
            self._enregistrer()
        return locals()

    nom = property(**nom())

    def prenom():
        def fget(self):
            return self._pn

        def fset(self, prenom):
            self._pn = prenom
            self._enregistrer()
        return locals()

    prenom = property(**prenom())

    def _enregistrer(self, date_modification=None):
        joueur_id = creer_id(self._pn, self._n)
        if date_modification is not None:
            if type(date_modification) in [str, unicode]:
                date_modification = datetime.strptime(date_modification, '%d/%m/%Y')
            elif type(date_modification) != datetime:
                raise TypeError(u"'%s' doit être de type 'datetime' ou une chaine de format '%d/%m/%Y'" % date_modification)

        if HISTORIQUE is not None:
            if self.id in HISTORIQUE:
                # Suppression de l'ancien ID
                j = HISTORIQUE.pop(self.id)

                # Si une date est donnée, garder la plus ancienne
                # en comparant avec celle de l'historique (permet
                # de créer un historique en chargeant des fichiers)
                date = j[3]
                if date_modification is not None and date_modification < datetime.strptime(j[3], '%d/%m/%Y'):
                    date = date_modification.strftime('%d/%m/%Y')
            elif date_modification is not None:
                date = date_modification.strftime('%d/%m/%Y')
            else:
                date = datetime.now().strftime('%d/%m/%Y')

            HISTORIQUE[joueur_id] = (self._pn, self._n, str(self.age), date)

        self.id = joueur_id
