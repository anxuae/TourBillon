# -*- coding: utf8 -*-
# Ce module correspond au module principal de TourBillon
#
#####################################################
__author__ = "La Billonnière"
__version__ = "Version : 4.0"
__date__ = "Date: 2008/03/09 21:57:19"
__copyright__ = "La Billonnière, 2008"
#####################################################

#####################################################
# Importation de Modules ou fonctions externes :
#####################################################

from conv4to5.GlobTrb import vg

#####################################################
# Definition exceptions :
#####################################################


class EquipeError(Exception):
    pass


class NotIntegerError(EquipeError):
    pass


class InvalidNumber(EquipeError):
    pass

#####################################################
# Corps principal de la Classe 'Equipe' :
#####################################################

# Valeurs admissibles dans les proc�dures :
# None -> cas de l'initialsation de la valeur
# ''   -> pour retourner la valeur
# val  -> pour assigner une valeur


class Equipe():
    """
    Classe definissant une équipe à partir de son numéro, le nom du premier joueur, \
    le nom du second joueur,le total des points, ne nombre de victoires, le nombre de chapeau
    """

    def __init__(self, numEq=1, nomJ1=None, nomJ2=None, totPts=0, totVic=0, totChap=0,
                 palCl=None, moyBill=None, minmaxBill=None, moyDur=None, minmaxDur=None):
        self.Eq = [None] * 11
        self.numeroEquipe(numEq)
        self.nomJoueur1(nomJ1)
        self.nomJoueur2(nomJ2)
        self.totalPoints(totPts)
        self.totalVictoires(totVic)
        self.totalChapeaux(totChap)
        self.palceClassement(palCl)
        self.moyenneBillon(moyBill)
        self.minmaxBillon(minmaxBill)
        self.moyenneDuree(moyDur)
        self.minmaxDuree(minmaxDur)

    def numeroEquipe(self, numEq=''):
        """
        Retourner ou modifier le numéro d'équipe
        """
        if numEq != '' and numEq != None:
            if type(numEq) != int:
                raise NotIntegerError("'%s' => Ce numéro d'équipe n'est pas un entier" % numEq)
            if numEq < 0:
                raise InvalidNumber("'%s' => Ce numéro d'équipe est < 0" % numEq)

        if numEq == '':                       # Retourne le numéro d'équipe
            return self.Eq[0]
        else:                               # Affecte le numéro d'équipe (=numEq)
            self.Eq[0] = numEq

    def nomJoueur1(self, nomJ1=''):
        """
        Retourner ou modifier le nom du joueur 1
        """
        if nomJ1 == '':                       # Retourne le nom du joueur 1
            return self.Eq[1]
        else:                               # Affecte le nom du joueur 1 (=nomJ1)
            self.Eq[1] = nomJ1

    def nomJoueur2(self, nomJ2=''):
        """
        Retourner ou modifier le nom du joueur 2
        """
        if nomJ2 == '':                       # Retourne le nom du joueur 2
            return self.Eq[2]
        else:                               # Affecte le nom du joueur 2 (=nomJ2)
            self.Eq[2] = nomJ2

    def totalPoints(self, totPts='', oper=''):
        """
        Retourner ou modifier le total des points de l'équipe.
        Si oper='' alors le total des points est remplacé par 'totPts'.
        Si oper='+' alors le total des points est incrémenté de 'totPts'.
        Si oper='-' alors 'totPts' est soustrait du total des points.
        """
        if totPts != '' and totPts != None:
            if type(totPts) != int:
                raise NotIntegerError("'%s' => Ce nombre de points n'est pas un entier" % totPts)
            if totPts < 0:
                raise InvalidNumber("'%s' => Le nombre de points de l'équipe ne peut pas étre < 0" % totPts)

        if totPts == '':                      # Retourne le total des points de l'équipe
            return self.Eq[3]
        elif totPts != '' and oper == '':       # Remplace le total des points actuel par 'totPts'
            self.Eq[3] = totPts
        elif totPts != '' and oper == '+':      # Ajoute 'totPts' au total des points actuel
            if self.Eq[3] == None:
                self.Eq[3] = totPts
            else:
                self.Eq[3] = self.Eq[3] + totPts
        elif totPts != '' and oper == '-':      # Soustrait 'totPts' au total des points actuel
            if self.Eq[3] != None:
                if totPts <= self.Eq[3]:
                    self.Eq[3] = self.Eq[3] - totPts
                else:
                    self.Eq[3] = 0

    def totalVictoires(self, totVic='', oper=''):
        """
        Retourner ou modifier le nombre de victoires de l'équipe.
        Si oper='' alors le total des victoires est remplacé par 'totVic'.
        Si oper='+' alors le total des victoires est incrémenté de 'totVic'.
        Si oper='-' alors 'totVic' est soustrait du total des victoires.
        """
        if totVic != '' and totVic != None:
            if type(totVic) != int:
                raise NotIntegerError("'%s' => Ce nombre de victoires n'est pas un entier" % totVic)
            if not (0 <= totVic <= vg.nbrPart):
                raise InvalidNumber("'%s' => Le nombre des victoires de l'équipe doit être compris entre 0 et %s" % (
                    totVic, vg.nbrPart))

        if totVic == '':                      # Retourne le nombre de victoires de l'�quipe
            return self.Eq[4]
        elif totVic != '' and oper == '':       # Remplace le total des victoires actuel par 'totVic'
            self.Eq[4] = totVic
        elif totVic != '' and oper == '+':      # Ajoute 'totVic' au total des victoires actuel
            if self.Eq[4] == None:
                self.Eq[4] = totVic
            else:
                self.Eq[4] = self.Eq[4] + totVic
        elif totVic != '' and oper == '-':      # Soustrait 'totVic' au total des victoires actuel
            if self.Eq[4] != None:
                if totVic <= self.Eq[4]:
                    self.Eq[4] = self.Eq[4] - totVic
                else:
                    self.Eq[4] = 0

    def totalChapeaux(self, totChap='', oper=''):
        """
        Retourner ou modifier le nombre de fois que l'équipe a été au chapeau.
        Si oper='' alors le total des victoires est remplacé par 'totChap'.
        Si oper='+' alors le total des victoires est incrémenté de 'totChap'.
        Si oper='-' alors 'totChap' est soustrait du total des victoires.
        """
        if totChap != '' and totChap != None:
            if type(totChap) != int:
                raise NotIntegerError("'%s' => le total des points doit être un entier" % totChap)
            if not (0 <= totChap <= vg.nbrPart):
                raise InvalidNumber("'%s' => le total des victoires de l'équipe doit être compris entre 0 et %s" % (
                    totChap, vg.nbrPart))

        if totChap == '':                     # Retourne le nombre de chapeaux
            return self.Eq[5]
        elif totChap != '' and oper == '':       # Remplace le total des chapeaux actuel par 'totChap'
            self.Eq[5] = totChap
        elif totChap != '' and oper == '+':      # Ajoute 'totChap' au total des chapeaux actuel
            if self.Eq[5] == None:
                self.Eq[5] = totChap
            else:
                self.Eq[5] = self.Eq[5] + totChap
        elif totChap != '' and oper == '-':      # Soustrait 'totChap' au total des chapeaux actuel
            if self.Eq[5] != None:
                if totChap <= self.Eq[5]:
                    self.Eq[5] = self.Eq[5] - totChap
                else:
                    self.Eq[5] = 0

    def palceClassement(self, palCl=''):
        """
        Retourner ou modifier le classement provisoire de l'équipe
        """
        if palCl != '' and palCl != None:
            if type(palCl) != int:
                raise NotIntegerError("'%s' => le classement de l'équipe doit être un entier" % palCl)
            if not (0 <= palCl <= vg.listeEq.nbr()):
                raise InvalidNumber("'%s' => le classement de l'équipe doit être compris entre 0 et %s" % (
                    palCl, vg.listeEq.nbr()))
        if palCl == '':                       # Retourne le classement provisoire de l'équipe
            return self.Eq[6]
        else:                               # Affecte le classement provisoire de l'équipe (=palCl)
            self.Eq[6] = palCl

    def moyenneBillon(self, moyBill=''):
        """
        Retourner ou modifier le nombre moyen de billons entrés par partie
        """
        if moyBill == '':
            return self.Eq[7]               # Retourne le nombre moyen de billons entrés en une partie
        else:
            self.Eq[7] = moyBill              # Affecte le nombre moyen de billons entrés en une partie

    def minmaxBillon(self, intervallePts=''):
        """
        Retourner ou modifier le nombre maximum et minimum de billons entrés par l'équipe
        dans un tournoi en une partie [min,num part,max,num part]
        """
        if intervallePts == '':               # Retourne le nombre min/max de billons entrés en une partie
            return self.Eq[8]
        else:                               # Affecte le nombre min/max de billons entrés en une partie (=maxBill)
            self.Eq[8] = intervallePts

    def moyenneDuree(self, moyDur=''):
        """
        Retourner ou modifier le nombre moyen de billons entrés par partie
        """
        if moyDur == '':
            return self.Eq[9]               # Retourne la durée moyenne d'une partie
        else:
            self.Eq[9] = moyDur               # Affecte la durée moyenne d'une partie

    def minmaxDuree(self, intervalleDur=''):
        """
        Retourner ou modifier le nombre maximum et minimum de billons entrés par l'équipe
        dans un tournoi en une partie [min,num part,max,num part]
        """
        if intervalleDur == '':               # Retourne la durée min/max en une partie
            return self.Eq[10]
        else:                               # Affecte la durée min/max en une partie
            self.Eq[10] = intervalleDur
