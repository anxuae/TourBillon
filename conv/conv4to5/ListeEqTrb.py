# -*- coding: utf8 -*-
# Ce module correspond au module principal de TourBillon
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
from conv4to5.EqTrb import Equipe

#####################################################
# Definition fonctions locales :
#####################################################


def inverElem(liste, ind1, ind2):
    "inverser deux éléments dans une liste"
    a = liste[ind1]
    liste[ind1] = liste[ind2]
    liste[ind2] = a
    return liste

#####################################################
# Definition exceptions :
#####################################################


class ListeEquipesError(Exception):
    pass


class OutOfRangeError(ListeEquipesError):
    pass


class NotIntegerError(ListeEquipesError):
    pass


class InvalidNumber(ListeEquipesError):
    pass

#####################################################
# Corps principal de la Classe 'ListeEquipes' :
#####################################################


class ListeEquipes():
    """
    Classe definissant la liste des équipes et sa manipulation
    """

    def __init__(self):
        self.ListeEq = []
        vg.nbrEq = 0
        vg.nbrPart = 0

    def ajout(self, numEq=1, nomJ1=None, nomJ2=None, totPts=0, totVic=0, totChap=0,
              palCl=None, moyBill=None, minmaxBill=None, moyDur=None, minmaxDur=None):
        """
        Ajouter une équipe
        """
        if numEq == None:
            numEq = self.nbr() + 1

        self.ListeEq.append(Equipe(numEq, nomJ1, nomJ2, totPts, totVic, totChap,
                                   palCl, moyBill, minmaxBill, moyDur, minmaxDur))   # Ajouter un objet Equipe à la fin de la liste
        self.trier()

    def suppr(self, val, ref='Ind'):
        """
        Supprimer une équipe à partir de son indice si 'ref'='Ind' \
               ou à partir de son numéro si 'ref'='Equ'
        """
        if type(val) != int:
            raise NotIntegerError("'%s' => Cet indice ou ce numero d'equipe n'est pas un entier" % val)

        if ref == 'Equ':
            "... à partir du numéro d'équipe"
            try:
                listenum = [e.numeroEquipe() for e in self.ListeEq if 1 == 1]   # Construit la liste des numéros
                ind = listenum.index(val)                                     # Fournis l'indice de l'équipe
                del(self.ListeEq[ind])                                      # Supprime l'équipe voulue
            except:
                raise InvalidNumber("'%s' => Ce numero d'equipe n'existe pas" % val)
        else:
            "...à partir de l'indice de la liste"
            try:
                del(self.ListeEq[val])                                      # Supprime l'équipe voulue
            except:
                raise OutOfRangeError("'%s' => Cet indice d'equipe n'existe pas" % val)
        vg.nbrEq = len(self.ListeEq)                                          # Mettre à jour le nombre d'équipes

    def equipe(self, val, ref='Ind'):
        """
        Retourner une équipe à partir de son indice si 'ref'='Ind' \n
               ou à partir de son numéro si 'ref'='Equ'
        """
        if type(val) != int:
            raise NotIntegerError("'%s' => Cet indice d'equipe n'est pas un entier" % val)

        if ref == 'Equ':
            "... à partir du numéro d'équipe"
            try:
                listenum = [e.numeroEquipe() for e in self.ListeEq if 1 == 1]   # Construit la liste des numéros
                ind = listenum.index(val)                                     # Fournis l'indice de l'équipe
                return self.ListeEq[ind]                                    # Retourne l'équipe voulue
            except:
                raise InvalidNumber("'%s' => Ce numero d'equipe n'existe pas" % val)
        else:
            "...à partir de l'indice de la liste"
            try:
                return self.ListeEq[val]                                    # Retourne l'équipe voulue
            except:
                raise OutOfRangeError("'%s' => Cet indice d'equipe n'existe pas" % val)

    def indice(self, numEq):
        """
        Retourne l'indice d'une équipe à partir de son numéro
        """
        listenum = [e.numeroEquipe() for e in self.ListeEq if 1 == 1]
        i = 0
        a = None
        while i < len(self.ListeEq):
            if listenum[i] == numEq:
                a = i
                break
            i = i + 1
        return a

    def trier(self):
        """
        Trie par ordre croissant les equipes de la liste selon leur numero d'equipe
        """
        if len(self.ListeEq) == 0:
            raise OutOfRangeError("'[]' => Aucune equipe n'est enregistree, le triage de la liste est impossible")

        listenum = [e.numeroEquipe() for e in self.ListeEq if 1 == 1]           # Construit la liste des numéros
        nouvliste = []
        i = 0
        while i < len(self.ListeEq):
            ind = listenum.index(max(listenum))
            nouvliste.append(self.ListeEq[ind])
            listenum[ind] = -1
            i = i + 1
        nouvliste.reverse()
        self.ListeEq = nouvliste

    def equipeExiste(self, numEq):
        """
        Vérifie l'unicité du numéro d'équipe, renvoie 0 si le numéro val n'a pas encore été utilisé
        """
        if type(numEq) != int:
            raise NotIntegerError("'%s' => Ce numero d'equipe n'est pas un entier" % numEq)

        listenum = [e.numeroEquipe() for e in self.ListeEq if 1 == 1]            # Construit la liste des numéros
        if numEq in listenum:
            return True
        else:
            return False

    def numLibre(self):
        """
        Retourne le numéro premier numéro libre
        """
        if len(self.ListeEq) == 0:
            return 1
        else:
            i = 1
            numLib = None
            while i < len(self.ListeEq) + 2:
                if self.equipeExiste(i) == False:
                    numLib = i
                    break
                i = i + 1
            return numLib

    def classer(self, ret=False):
        """
        Classer les équipes en fonction de leur niveaux et de leur nombre de points
        """
        i = 0
        listeInd = []
        while i < len(self.ListeEq):          # Liste des indices
            listeInd.append(i)
            i = i + 1

        if len(listeInd) > 1:                 # Deux équipes minimum
            j = 0
            while j < len(listeInd):          # Autant de cycles d'inversion que d'équipes
                i = 0
                while i < len(listeInd) - 1:    # invertion des indices de la liste "listeInd" suivant la force de l'équipe

                    if self.ListeEq[listeInd[i]].totalVictoires() < self.ListeEq[listeInd[i + 1]].totalVictoires():
                        listeInd = inverElem(listeInd, i, i + 1)

                    elif self.ListeEq[listeInd[i]].totalVictoires() == self.ListeEq[listeInd[i + 1]].totalVictoires():

                        if self.ListeEq[listeInd[i]].totalPoints() < self.ListeEq[listeInd[i + 1]].totalPoints():
                            listeInd = inverElem(listeInd, i, i + 1)

                    i = i + 1
                j = j + 1

            if ret == False:      # Assigner le classement aux équipes
                place = 1
                saut = 0
                i = 1
                self.ListeEq[listeInd[0]].palceClassement(place)
                while i < len(listeInd):        # Enregistrement du classement de chaque équipe
                    if self.ListeEq[listeInd[i]].totalVictoires() == self.ListeEq[listeInd[i - 1]].totalVictoires() and self.ListeEq[listeInd[i]].totalPoints() == self.ListeEq[listeInd[i - 1]].totalPoints():
                        self.ListeEq[listeInd[i]].palceClassement(place)
                        saut = saut + 1
                    else:
                        place = place + 1 + saut
                        saut = 0
                        self.ListeEq[listeInd[i]].palceClassement(place)
                    i = i + 1

            elif ret == True:     # Retourner la liste des indices des équipes classées
                return listeInd

    def nbr(self):
        """
        Retourne le nombre d'équipes inscrites au tournoi
        """
        return len(self.ListeEq)
