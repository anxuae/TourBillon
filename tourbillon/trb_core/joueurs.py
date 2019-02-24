#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Définitions des joueurs."""

#--- Import --------------------------------------------------------------------

import os
from datetime import datetime

#--- Fonctions -----------------------------------------------------------------

HISTORIQUE = None
FICHIER_HISTORIQUE = None

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
    f = open(fichier, 'r')
    lignes = f.readlines()
    f.close()

    HISTORIQUE = {}
    for ligne in lignes:
        ligne = unicode(ligne).strip()
        l = ligne.split(',')
        HISTORIQUE[l[0]] = (l[1], l[2], l[3], l[4])

    FICHIER_HISTORIQUE = os.path.abspath(fichier)

def enregistrer_historique():
    if HISTORIQUE:
        ids = HISTORIQUE.keys()
        ids.sort()

        f = open(FICHIER_HISTORIQUE, 'w')
        for id in ids:
            ligne = id + ',' + ','.join(HISTORIQUE[id]) + "\n"
            f.write(ligne)
        f.close()

#--- Classes -------------------------------------------------------------------

class NomCompleteur(object):
    def __init__(self):
       pass

    def completer(self, prenom, nom = ''):
        debut_id = creer_id(prenom, nom)
        if debut_id.endswith('_'):
            debut_id = debut_id[:-1]

        id = self._dichotomie(debut_id)

        if id == None:
            return ('', '', '', '')
        else:
            if nom == '':
                return (HISTORIQUE[id][0][len(prenom):], HISTORIQUE[id][1], HISTORIQUE[id][2], HISTORIQUE[id][3])
            else:
                return ('', HISTORIQUE[id][1][len(nom):], HISTORIQUE[id][2], HISTORIQUE[id][3])

    def _dichotomie(self, texte) :
        if HISTORIQUE and texte != '':
            ids = HISTORIQUE.keys()
            ids.sort()

            debut, fin = 0, len(HISTORIQUE) - 1
            while debut <= fin :
                milieu = (debut + fin) / 2
                if ids[milieu].startswith(texte) :
                    # L'élément du milieu de la liste correspond
                    # Recherche du premier element correspondant
                    while ids[milieu].startswith(texte):
                        milieu -= 1
                    return ids[milieu + 1]
                elif texte < ids[milieu] :
                    # Recherche avant le milieu
                    fin = milieu - 1
                else :
                    # Recherche après le milieu
                    debut = milieu + 1
        return None

class Joueur(object):
    def __init__(self, prenom, nom, age, **kwrd):
        self._pn = prenom
        self._n = nom
        self.age = age
        self.id = creer_id(self._pn, self._n)
        self._enregistrer()

    def __repr__(self):
        return "%s %s" % (self._pn, self._n)

    def __eq__(self, other):
        if type(other) == Joueur:
            cmp = other.id
        else:
            cmp = unicode(other)
        if self.id == cmp:
            return True
        else:
            return False

    def __ne__(self, other):
        if type(other) == Joueur:
            cmp = other.id
        else:
            cmp = unicode(other)
        if self.id != cmp:
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

    def _enregistrer(self):
        id = creer_id(self._pn, self._n)
        if HISTORIQUE is not None:
            if self.id in HISTORIQUE:
                j = HISTORIQUE.pop(self.id)
                date = j[3]
            else:
                date = datetime.now().strftime('%d/%m/%Y')
            HISTORIQUE[id] = (self._pn, self._n, str(self.age), date)

        self.id = id
