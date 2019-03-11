# -*- coding: utf8 -*-
# Cette classe définie l'objet ListeRencontres
#
#####################################################
__author__ = "La Billonnière"
__version__ = "Version : 4.0"
__date__ = "$Date: 2008/03/09 21:57:19 $"
__copyright__ = "Copyright (c) La Billonnière, 2008"
__license__ = "Python"
#####################################################

#####################################################
# Importation de Modules ou fonctions externes :
#####################################################

from conv4to5.GlobTrb import vg
from conv4to5.RencTrb import Rencontre
from datetime import timedelta

#####################################################
# Definition exceptions :
#####################################################


class ListeRencontresError(Exception):
    pass


class OutOfRangeError(ListeRencontresError):
    pass


class NotIntegerError(ListeRencontresError):
    pass


class InvalidNumber(ListeRencontresError):
    pass

#####################################################
# Corps principal de la Classe 'ListeRencuipes.py' :
#####################################################


class ListeRencontres():
    """
    Classe definissant la liste des rencontres et sa manipulation
    """

    def __init__(self):
        self.ListeRenc = []

    def ajout(self, numPart=None, numEqA=None, numEqB=None, ptsEqA=None, ptsEqB=None, hDebut=None, duree=None):
        """
        Ajouter une rencontre
        """
        if numPart == None:
            numPart = vg.nbrPart

        self.ListeRenc.append(Rencontre(numPart, numEqA, numEqB,
                                        ptsEqA, ptsEqB, hDebut, duree))                    # Ajouter un objet Rencontre à la fin de la liste

    def suppr(self, val, numEq='', ref='Ind'):
        """
        Si 'ref'='Ind': Supprimer une rencontre à partir de son indice
        Si 'ref'='Renc':
            Si numEq='': Supprimer toutes les rencontres de la partie 'val'
            Si numEq<>'': Supprimer la rencontre de la partie 'val' et qui implique l'équipe n°'numEq'
        """
        if type(val) != int:
            raise NotIntegerError("'%s' => Cet indice de rencontre ou numero de partie n'est pas un entier" % val)
        if ref == 'Renc' and not (0 < val <= vg.nbrPart):
            raise OutOfRangeError("'%s' => Ce numero de partie n'est pas compris entre 1 et %s" % (val, vg.nbrPart))
        if numEq != '' and type(numEq) != int:
            raise NotIntegerError("'%s' => Ce numero d'equipe n'est pas un entier" % numEq)

        if ref == 'Renc':
            # ... à partir du numéro de partie
            if numEq == '':
                # ... sans numéro d'équipe
                try:
                    # Construit une nouvelle liste des rencontres en omettant celles de la partie 'val'
                    li = [e for e in self.ListeRenc if e.numeroPartie() != val]
                    self.ListeRenc = li
                except:
                    raise InvalidNumber("'%s' => Ce numero de partie n'existe pas" % val)
            else:
                # ... avec numéro d'équipe
                try:
                    li = [e for e in self.ListeRenc if e.numeroPartie() != val or e.impliqueEquipes([numEq]) == False]
                    self.ListeRenc = li                                                  # Supprime la rencontre voulue
                except:
                    raise InvalidNumber("'[%s,%s]' => La rencontre definie par ce couple n'existe pas" % (val, numEq))
        else:
            # ...à partir de l'indice de la liste
            try:
                del(self.ListeRenc[val])                                                # Supprime la rencontre voulue
            except:
                raise OutOfRangeError("'%s' => Cet indice de rencontre n'existe pas" % val)

    def rencontre(self, val, numEq='', ref='Ind'):
        """
        Si 'ref'='Ind': Retourne une rencontre à partir de son indice
        Si 'ref'='Renc':
            Si numEq='': Retourne toutes les rencontres de la partie 'val' sous forme d'une liste
            Si numEq<>'': Retourne la rencontre de la partie 'val' et qui implique l'équipe n°'numEq'
        """
        if type(val) != int:
            raise NotIntegerError("'%s' => Cet indice de rencontre ou numero de partie n'est pas un entier" % val)
        if ref == 'Renc' and not (0 <= val <= vg.nbrPart):
            raise OutOfRangeError("'%s' => Ce numero de partie n'est pas compris entre 1 et %s" % (val, vg.nbrPart))
        if numEq != '' and type(numEq) != int:
            raise NotIntegerError("'%s' => Ce numéro d'equipe n'est pas un entier" % numEq)

        if ref == 'Renc':
            # ... à partir du numéro de Partie
            # Construit une nouvelle liste des rencontres en omettant celles de la partie 'val'
            li1 = [e for e in self.ListeRenc if e.numeroPartie() == val]
            if numEq == '':
                # ... sans numéro d'équipe
                return li1                                          # Retourne une liste de rencontre de la partie 'val', eut être vide
            else:
                # ... avec numéro d'équipe
                li2 = [e for e in li1 if e.impliqueEquipes([numEq]) != False]
                # Une rencontre est définie par un couple unique [numPart,numEq]
                try:
                    if li2 == []:                                     # Aucune rencontres ne contenant ce numéro d'équipe
                        return None
                    else:
                        # Tente de retourner le 1er terme de la liste qui soit dit en passant
                        return li2[0]
                except:                                             # doit comporter 1 et 1 seul terme. Mais une erreur peut se produire en cas de chapeau
                    raise InvalidNumber("'[Partie %s,Equipe %s]' => La rencontre definie par ce couple n'existe pas" % (
                        val, numEq))
        else:
            # ...à partir de l'indice de la liste
            try:
                if self.ListeRenc == []:
                    return None
                else:
                    return self.ListeRenc[val]                          # Retourne la rencontre voulue
            except:
                raise OutOfRangeError("'%s' => Cet indice de rencontre n'existe pas" % val)

    def equipe(self, numEq, numPart):
        """
        Retourne les résultats (liste d'info) d'une équipe à la partie spécifiée
        """
        if numPart > vg.nbrPart:
            raise OutOfRangeError("'%s' => Ce numero de partie n'existe pas (%s partie)" % (numPart, vg.nbrPart))

        ren = self.rencontre(numPart, numEq, ref='Renc')
        if ren == None:           # La rencontre n'existe pas
            return None
        else:
            if ren.numeroEquipes()[0] == numEq:
                return [ren.etatEquipes()[0], ren.pointsEquipes()[0], ren.dureeRenc()]
            else:
                return [ren.etatEquipes()[1], ren.pointsEquipes()[1], ren.dureeRenc()]

    def listeNumeroEquipes(self, numPart):
        """
        Retourne la liste des équipes qui ont jouées à la partie numPart.
        """
        l = []
        for renc in self.rencontre(numPart, ref='Renc'):
            for num in renc.numeroEquipes():
                if num and num not in l:
                    l.append(num)
        l.sort()
        return l

    def nbr_EqA_vs_EqB(self, numEqA, numEqB):
        """
        Retourne le nombre de fois que les équipes A et B se sont rencontrées
        """
        a = 0
        for e in self.ListeRenc:
            if e.impliqueEquipes([numEqA]) != False and e.impliqueEquipes([numEqB]) != False:
                a = a + 1
        return a

    def minmaxStat(self, numEq):
        """
        Retourne une liste [[minBillon,numPart,maxBillon,numPart],[minDurée,numPart,maxDurée,numPart,duréeTotal]] représentant la meilleur
        performance et la pire de l'équipe 'numEq' au cours d'un tournoi.
        """
        if type(numEq) != int:
            raise NotIntegerError("'%s' => Ce numero d'equipe n'est pas un entier" % numEq)

        minBill = None
        numPartMinBill = None
        maxBill = None
        numPartMaxBill = 0

        minDur = None
        numPartMinDur = None
        maxDur = None
        numPartMaxDur = None
        totDur = timedelta(0, 0, 0)

        i = 0
        while i < len(self.ListeRenc):
            if self.rencontre(i).impliqueEquipes([numEq]) != False:

                if self.rencontre(i).numeroEquipes()[0] == numEq:  # Recherche des points de numEq
                    pts = self.rencontre(i).pointsEquipes()[0]
                elif self.rencontre(i).numeroEquipes()[1] == numEq:
                    pts = self.rencontre(i).pointsEquipes()[1]
                else:
                    pts = None
                dur = self.rencontre(i).dureeRenc()               # Recherche de la durée

                if pts != None:
                    if minBill == None:
                        minBill = pts         # Affectation min
                        numPartMinBill = self.rencontre(i).numeroPartie()
                    else:
                        if (pts < minBill and pts != None):
                            minBill = pts     # Affectation min
                            numPartMinBill = self.rencontre(i).numeroPartie()

                    if maxBill == None:
                        maxBill = pts         # Affectation max
                        numPartMaxBill = self.rencontre(i).numeroPartie()
                    else:
                        if (pts > maxBill and pts != None):
                            maxBill = pts     # Affectation max
                            numPartMaxBill = self.rencontre(i).numeroPartie()

                if dur != None:
                    if minDur == None:
                        # la durée de la rencontre est de plus de 2 minutes (sinon c'est qu'il s'agit d'un chapeau)
                        if dur > timedelta(0, 60, 0):
                            minDur = dur      # Affectation durée min
                            numPartMinDur = self.rencontre(i).numeroPartie()
                    else:
                        if timedelta(0, 60, 0) < dur < minDur:
                            minDur = dur      # Affectation durée min
                            numPartMinDur = self.rencontre(i).numeroPartie()

                    if maxDur == None:
                        if dur > timedelta(0, 60, 0):
                            maxDur = dur      # Affectation durée max
                            numPartMaxDur = self.rencontre(i).numeroPartie()
                    else:
                        if dur > maxDur:
                            maxDur = dur      # Affectation durée max
                            numPartMaxDur = self.rencontre(i).numeroPartie()

                    totDur = totDur + dur

            i = i + 1
        return [[minBill, numPartMinBill, maxBill, numPartMaxBill], [minDur, numPartMinDur, maxDur, numPartMaxDur, totDur]]

    def verifierDonnee(self, numPart):
        """
        Retourne '1' si toutes les données de toutes les rencontres ont été rentrées sinon '0'
        """
        if type(numPart) != int:
            raise NotIntegerError("'%s' => Ce numero de partie n'est pas un entier" % numPart)
        if not (0 < numPart <= vg.nbrPart):
            raise OutOfRangeError("'%s' => Ce numero de partie n'est pas compris entre 1 et %s" % (
                numPart, vg.nbrPart))

        verif = True
        t = self.rencontre(val=numPart, ref='Renc')
        i = 0
        while i < len(t):
            if t[i].compteurModif < 2:
                verif = False
            i = i + 1
        return verif

    def nbr(self):
        """
        Retourne le nombre de rencontres enregistrées
        """
        return len(self.ListeRenc)
