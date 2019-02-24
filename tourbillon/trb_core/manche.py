#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Définition d'une manche."""

from datetime import datetime, timedelta
from tourbillon.trb_core.exceptions import StatutError
from tourbillon.trb_core.constantes import (CHAPEAU, GAGNE, PERDU, FORFAIT,
                                            M_EN_COURS, M_TERMINEE)

#--- Fonctions ----------------------------------------------------------------

def Property(func):
    return property(**func())

#--- Classes -------------------------------------------------------------------

class Manche(object):
    def __init__(self, debut=datetime.now(), adversaires=[]):
        self.data = {'points' : 0,
                     'etat' : None,
                     'debut' : debut,
                     'fin' : None,
                     'adversaires' : adversaires,
                     'piquet' : None}

    def __repr__(self):
        texte = """
        Manche
            debut        : %s
            Etat         : %s
            Points       : %s
            Adversaires  : %s

            
            Statut       : %s
        """
        return texte % (self.debut,
                        self.etat,
                        self.points,
                        self.adversaires,
                        self.statut)

    def charger(self, data):
        """
        Methode rétro-compatible pour charger les données d'une manche
        via un dictionnaire. (utilisé par la fonction de chargerment
        d'un tournoi)
        
        Cette fonction ne comporte aucune protection, les données entrées
        doivent êtres impérativement correctes.
        
        data (dict)
        """
        for k, v  in data.iteritems():
            if k in self.data:
                self.data[k] = v
        if 'duree' in data:
            if data['duree']:
                self.data['fin'] = self.data['debut'] + data['duree']
            elif self.data['adversaires'] == []:
                self.data['fin'] = self.data['debut']

    @Property
    def statut():
        doc = """
        Retourne le status de la manche:
        
            M_EN_COURS => manche non commencée ou non terminée
            M_TERMINEE => manche terminée (heure de fin enregistrée)
        """

        def fget(self):
            if self.data['etat'] == CHAPEAU or self.data['etat'] == FORFAIT:
                return M_TERMINEE
            elif self.data['fin'] is None:
                return M_EN_COURS
            else:
                return M_TERMINEE

        return locals()

    @Property
    def points():
        def fget(self):
            return self.data['points']

        def fset(self, valeur):
            if type(valeur) != int or valeur < 0:
                raise TypeError, u"Le nombre de points doit être un entier positif ou nul."
            if self.data['etat'] == FORFAIT:
                raise ValueError, u"Le nombre de points d'une manche FORFAIT ne peut pas être modifié."
            self.data['points'] = valeur

        return locals()

    @Property
    def etat():
        def fget(self):
            return self.data['etat']

        def fset(self, valeur):
            if valeur not in [CHAPEAU, GAGNE, PERDU, FORFAIT]:
                raise TypeError, u"L'état doit être une des valeur suivantes : %s." % ", ".join([CHAPEAU, GAGNE, PERDU, FORFAIT])

            if valeur in [GAGNE, PERDU] and self.data['fin'] is None:
                self.data['fin'] = datetime.now()
            if valeur in [CHAPEAU, FORFAIT]:
                self.data['adversaires'] = []
                self.data['fin'] = self.data['debut']
            if valeur in [ FORFAIT]:
                self.data['points'] = 0

            self.data['etat'] = valeur

        return locals()

    @Property
    def debut():
        def fget(self):
            return self.data['debut']

        def fset(self, valeur):
            if type(valeur) != datetime:
                raise TypeError, u"L'heure de début doit être de type 'datetime'."
            self.data['debut'] = valeur

        return locals()

    @Property
    def duree():
        def fget(self):
            if self.data['fin'] is None or self.data['fin'] == self.data['debut']:
                return None
            else:
                return self.data['fin'] - self.data['debut']

        def fset(self, valeur):
            if type(valeur) != timedelta:
                raise TypeError, u"La durée doit être de type 'timedelta'."
            if self.data['etat']  in [CHAPEAU, FORFAIT]:
                raise ValueError, u"La durée d'une manche CHAPEAU ou FORFAIT ne peut être modifiée."
            self.data['fin'] = self.data['debut'] + valeur

        return locals()

    @Property
    def fin():
        def fget(self):
            return self.data['fin']

        def fset(self, valeur):
            if type(valeur) != datetime:
                raise TypeError, u"L'heure de fin doit être de type 'datetime'."
            if self.data['etat']  in [CHAPEAU, FORFAIT]:
                raise ValueError, u"La fin d'une manche CHAPEAU ou FORFAIT ne peut être modifiée."
            self.data['fin'] = valeur

        return locals()

    @Property
    def adversaires():
        def fget(self):
            return self.data['adversaires']

        def fset(self, valeur):
            if type(valeur) != list:
                raise TypeError, u"Les adversaires sont donnés sous forme de liste d'entiers."
            for num in valeur:
                if type(num) != int:
                    raise TypeError, u"Les adversaires sont donnés sous forme de liste d'entiers."
            if self.data['etat']  in [CHAPEAU, FORFAIT]:
                raise ValueError, u"Il n'y a pas d'adversaires pour une manche CHAPEAU ou FORFAIT."
            self.data['adversaires'] = valeur

        return locals()

    @Property
    def piquet():
        def fget(self):
            return self.data['piquet']

        def fset(self, valeur):
            self.data['piquet'] = valeur

        return locals()
