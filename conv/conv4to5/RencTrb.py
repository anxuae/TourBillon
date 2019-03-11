# -*- coding: utf8 -*-
# Cette classe définie l'objet Rencontre
#
#####################################################
__author__ = "La Billonnière"
__version__ = "Version : 4.0"
__date__ = "Date: 2008/03/09 21:57:19"
__copyright__ = "© La Billonnière, 2008"
#####################################################

#####################################################
# Importation de Modules ou fonctions externes :
#####################################################

from conv4to5.GlobTrb import vg
from conv4to5 import TransfoDateTrb
from datetime import datetime, timedelta

#####################################################
# Definition exceptions :
#####################################################


class RencontreError(Exception):
    pass


class NotIntegerError(RencontreError):
    pass


class InvalidNumber(RencontreError):
    pass

#####################################################
# Corps principal de la Classe 'Rencontre' :
#####################################################

# Valeurs admissibles dans les procédures :
# None -> cas de l'initialsation de la valeur
# ''   -> pour retourner la valeur
# val  -> pour assigner une valeur


class Rencontre():
    """
    Classe definissant une rencontre entre deux équipes à partir du numéro de partie pendant \
    laquelle a eu lieu la rencontre et du numéro, l'état (G,P ou C) et les points de chaque équipes
    """

    def __init__(self, numPart=None, numEqA=None, numEqB=None, ptsEqA=None, ptsEqB=None, hDebut=None, duree=None):
        self.Renc = [None] * 9
        if hDebut != None and duree != None:       # Si les données de temps sont entrées à la création de la rencontre,elles ne seront pas modifées par la suite
            # (compteurModif=2) sinon 'compteurModif'=0 donc lors de la création il y a prise du temps de l'ordi pour
            self.compteurModif = 2
            if type(hDebut) == bytes:
                self.debutRenc(hDebut, 'chn')
            else:
                self.debutRenc(hDebut, 'obj')
            if type(duree) == bytes:
                self.dureeRenc(duree, 'chn')
            else:
                self.dureeRenc(duree, 'obj')
        else:
            # Initialisaion d'une rencontre
            if numEqB == None:                    # Cas ou l'équipe est chapeau
                self.compteurModif = 1
            else:
                # l'heure de début (tirage validé par l'utilisateur= création de toutes les rencontres)
                self.compteurModif = 0
            # lors d'une première rentrée des points, prise de temps pour la durée =>
            # 'compteurModif'=2 : plus de modif quoi qu'il arrive.
            self.debutRenc(datetime.now())

        self.numeroPartie(numPart)
        self.numeroEquipes(numEqA, numEqB)
        self.pointsEquipes(ptsEqA, ptsEqB)

    def __repr__(self):
        return "%s vs %s" % (self.numeroEquipes()[0], self.numeroEquipes()[1])

    def numeroPartie(self, numPart=''):
        """
        Retourner ou modifier le numéro de la partie
        """
        if numPart != '' and numPart != None:
            if type(numPart) != int:
                raise NotIntegerError("'%s' => Ce numero de partie n'est pas un entier" % numPart)
            if not (0 <= numPart <= vg.nbrPart):
                raise InvalidNumber("'%s' => Ce numero de partie n'est pas compris entre 0 et %s" % (
                    numPart, vg.nbrPart))

        if numPart == '':                     # Retourne le numéro d'équipe
            return self.Renc[0]
        # Affecte le numéro de la partie durant laquelle a eu lieu la rencontre (=numPart)
        else:
            self.Renc[0] = numPart

    def numeroEquipes(self, numEqA='', numEqB=''):
        """
        Retourner ou modifier le numéro des deux équipes. Attention, retourne une liste [numEqA,numEqB]
        """
        if numEqA != '' and numEqA != None:
            if type(numEqA) != int:
                raise NotIntegerError("'%s' => Ce numero d'equipe n'est pas un entier" % numEqA)
            if not numEqA >= 0:
                raise InvalidNumber("'%s' => Ce numero d'equipe est < 0" % numEqA)
        if numEqB != '' and numEqB != None:
            if type(numEqB) != int:
                raise NotIntegerError("'%s' => Ce numero de d'equipe n'est pas un entier" % numEqB)
            if not numEqB >= 0:
                raise InvalidNumber("'%s' => Ce numero d'equipe est < 0" % numEqB)

        if numEqA == '' and numEqB == '':       # Retourne les numéros des équipe A et B
            return [self.Renc[1], self.Renc[2]]
        elif numEqA != '' and numEqB == '':     # Affecte le numéro de l'équipe A (=numEqA)
            self.Renc[1] = numEqA
        elif numEqA == '' and numEqB != '':     # Affecte le numéro de l'équipe B (=numEqB)
            self.Renc[2] = numEqB
        elif numEqA != '' and numEqB != '':     # Affecte les numéros des équipe A et B
            self.Renc[1] = numEqA
            self.Renc[2] = numEqB

    def pointsEquipes(self, ptsEqA='', ptsEqB=''):
        """
        Retourner ou modifier les points des deux équipes (et affecte leur état: 'G' ou 'P').
        Attention, retourne une liste [ptsEqA,ptsEqB]
        """
        if ptsEqA != '' and ptsEqA != None:
            if type(ptsEqA) != int:
                raise NotIntegerError("'%s' => le total des points n'est pas un entier" % ptsEqA)
            if ptsEqA < 0:
                raise InvalidNumber("'%s' => le total des points de l'equipe ne peut pas etre < 0" % ptsEqA)
        if ptsEqB != '' and ptsEqB != None:
            if type(ptsEqB) != int:
                raise NotIntegerError("'%s' => le total des points n'est pas un entier" % ptsEqB)
            if ptsEqB < 0:
                raise InvalidNumber("'%s' => le total des points de l'equipe ne peut pas etre < 0" % ptsEqB)

        def affectEtat():
            """
            Affecte les état: 'G' pour l'equipe qui a le plus de points et 'P' pour l'autre
            """
            if self.Renc[1] != None and self.Renc[2] == None:
                self.Renc[5] = "C"
                self.Renc[6] = None
            elif self.Renc[1] != None and self.Renc[2] != None and ptsEqA != None and ptsEqB != None:
                if ptsEqA < ptsEqB:
                    self.Renc[5] = "P"
                    self.Renc[6] = "G"
                elif ptsEqA > ptsEqB:
                    self.Renc[5] = "G"
                    self.Renc[6] = "P"
                elif ptsEqA == ptsEqB and ptsEqA != 0 and ptsEqB != 0:
                    raise InvalidNumber("'%s<>%s' => Lors d'une rencontre, les equipes doivent se departager d'au moins un point" % (
                        ptsEqA, ptsEqB))

        if ptsEqA == '' and ptsEqB == '':       # Retourne les points des équipe A et B
            return [self.Renc[3], self.Renc[4]]
        elif ptsEqA != '' and ptsEqB == '':     # Affecte les points de l'équipe A (=ptsEqA)
            self.Renc[3] = ptsEqA
        elif ptsEqA == '' and ptsEqB != '':     # Affecte les points de l'équipe B (=ptsEqB)
            self.Renc[4] = ptsEqB
        elif ptsEqA != '' and ptsEqB != '':     # Affecte les points des équipe A et B
            self.Renc[3] = ptsEqA
            self.Renc[4] = ptsEqB

        affectEtat()

        if self.compteurModif == 1:       # Calcule la durée de la rencontre
            self.dureeRenc(datetime.now() - self.debutRenc())

        self.compteurModif = self.compteurModif + 1

    def etatEquipes(self):
        """
        Retourner les états des deux équipes. Attention, retourne une liste [etatEqA,etatEqB]
        """
        return [self.Renc[5], self.Renc[6]]

    def debutRenc(self, hDebut='', form='obj'):
        """
        Retourner ou modifier l'heure de début de la rencontre
        Si hDebut=None
            si form='obj' => retourne un objet de type 'datetime'
            si form='chn' => retourne une chaine de caractères ISO "YYYY-MM-DDTHH:MM:SS.mmmmmm"
        Si "hDebut<>None"
            hDebut entré est soit un objet de type 'datetime'
                             soit une chaine de caractères ISO "YYYY-MM-DD HH:MM:SS.mmmmmm"
        """
        if hDebut == '':
            if self.Renc[7] == None:
                return None
            else:
                if form == 'obj':                 # Retourne la date de début de la rencontre sous forme d'un objet 'datetime'
                    return self.Renc[7]
                else:                           # Retourne la date de début de la rencontre sous forme d'une chaine
                    return TransfoDateTrb.datetimeENchaine(self.Renc[7])
        else:                               # Affecte à Renc[7] un objet 'datetime' de début de la rencontre
            if hDebut == None:
                self.Renc[7] = None
            else:
                if type(hDebut) == datetime:
                    self.Renc[7] = hDebut
                else:
                    self.Renc[7] = TransfoDateTrb.chaineENdatetime(hDebut)

    def dureeRenc(self, duree='', form='obj'):
        """
        Retourner ou modifier la durée de la rencontre
        Si duree=None
            si form='obj' => retourne un objet de type 'timedelta'
            si form='chn' => retourne une chaine de caractères ISO "D days, HH:MM:SS.mmmmmm"
        Si duree!=None
            entré est soit un objet 'timedelta',
                      soit une chaine de caractères ISO "D days, HH:MM:SS.mmmmmm"
        """
        if duree == '':
            if self.Renc[8] == None:
                return None
            else:
                if form == 'obj':                 # Retourne un objet 'timedelta' représentant la durée de la rencontre
                    return self.Renc[8]
                else:                           # Retourne une chaine représentant la durée de la rencontre
                    return TransfoDateTrb.timedeltaENchaine(self.Renc[8])
        else:                               # Affecte à Renc[8] un objet 'timedelta'
            if duree == None:
                self.Renc[8] = None
            else:
                if type(duree) == timedelta:
                    self.Renc[8] = duree
                else:
                    self.Renc[8] = TransfoDateTrb.chaineENtimedelta(duree)

    def impliqueEquipes(self, numEqs, ref='Ind'):
        """
        'numEqs' doit être une liste de numéro d'équipes.
        Si au moins une des équipes de 'numEqs' est impliqué dans la rencontre:
            Si 'ref' ='Ind' retourne l'indice du premier n° de la liste 'numEqs' impliqué
            Si 'ref'='Equ' retourne le premier numéro de la liste 'numEqs' impliqué
        Si aucune liste impliqué retourne False.
        """
        i = 0
        a = False
        while i < len(numEqs):
            if numEqs[i] in self.numeroEquipes():
                a = True
                if ref == 'Ind':
                    ind = i
                else:
                    ind = numEqs[i]
                i = len(numEqs)
            i = i + 1
        return a
