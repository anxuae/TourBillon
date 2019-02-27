# -*- coding: UTF-8 -*-

"""Définitions des parties."""

import copy
from datetime import datetime
from tourbillon.core.manche import Manche
from tourbillon.core.exceptions import StatutError, IncoherenceError, ResultatError
from tourbillon.core import constantes as cst


class Partie(object):
    """
    Représente une partie. Cette classe manipule les données des équipes,
    elle ne conserve aucunes données (C'est un proxy!).
    """

    def __init__(self, parent):
        self.tournoi = parent

    def __str__(self):
        texte = """
        Partie n°%s:
            Joueurs   : %s
            Chapeaux  : %s
            Forfaits  : %s

            Statut    : %s
        """
        return texte % (self.numero,
                        self.nb_equipes(),
                        len(self.chapeaux()),
                        len(self.forfaits()),
                        self.statut)

    def __int__(self):
        return self.numero

    def numero():
        """
        Retourne le numéro de la partie.
        """

        def fget(self):
            if self in self.tournoi.parties():
                return self.tournoi.parties().index(self) + 1
            else:
                raise IncoherenceError(u"Cette partie n'appartient pas au tournoi en cours.")
        return locals()

    numero = property(**numero())

    def statut():
        doc = """
        Retourne le status de la partie:

            P_ATTEND_TIRAGE   => le tirage n'a pas été donné
            P_EN_COURS       => les manches ont été créées
            P_COMPLETE       => la partie est complete, c'est la dernière du tournoi
            P_TERMINEE       => la partie est complete, ce n'est pas la dernière du tournoi
        """

        def fget(self):

            if not self.equipes():
                # Aucune équipe n'a de manche avec ce numero de partie
                return cst.P_ATTEND_TIRAGE

            for equipe in self.equipes():
                if equipe.statut == cst.E_EN_COURS and self == self.tournoi.partie_courante():
                    return cst.P_EN_COURS

            if self == self.tournoi.partie_courante():
                return cst.P_COMPLETE
            else:
                return cst.P_TERMINEE
        return locals()

    statut = property(**statut())

    def debut(self):
        """
        Retourne l'heure de début de la partie. None est renvoyé
        si la partie n'est pas démarrée.
        """
        if self.statut == cst.P_ATTEND_TIRAGE:
            return None

        for equipe in self.equipes():
            debut = copy.deepcopy(equipe.resultat(self.numero).debut)

        return debut

    def nb_equipes(self):
        """
        Retourne le nombre d'équipes qui jouent.
        (Suppression des CHAPEAU et FORFAIT)
        """
        nb = 0
        for equipe in self.equipes():
            if equipe.resultat(self.numero).etat not in [cst.CHAPEAU, cst.FORFAIT]:
                nb += 1

        return nb

    def manches(self):
        """
        Retourne les manches de cette partie sous forme
        de liste de numéro d'équipes. (Les chapeaux ne sont
        pas inclus).
        """
        l = []
        manches = []
        if self.statut != cst.P_ATTEND_TIRAGE:
            for equipe in self.equipes():
                if equipe.numero not in l:
                    l.append(equipe.numero)

                    m = equipe.resultat(self.numero)
                    map(l.append, m.adversaires)

                    if m.adversaires != []:
                        manches.append(sorted([equipe.numero] + m.adversaires))

        return manches

    def chapeaux(self):
        """
        Retourne la liste des chapeaux de cette partie.
        """
        chapeaux = []
        if self.statut != cst.P_ATTEND_TIRAGE:
            for equipe in self.equipes():
                if equipe.resultat(self.numero).etat == cst.CHAPEAU:
                    chapeaux.append(equipe)

        return sorted(chapeaux)

    def equipes(self):
        """
        Retourne la liste des équipes qui on une manche définie
        pour cette partie y compris CHAPEAU et FORFAIT. Sauf cas
        exceptionel (ajout d'équipes lorsqu'un tournoi est déjà
        commancé), une manche est toujours définie pour chaque
        partie.
        """
        equipes = []
        for equipe in self.tournoi.equipes():
            if equipe.partie_existe(self.numero):
                equipes.append(equipe)
        return equipes

    def forfaits(self):
        """
        Retourne la liste des forfaits de cette partie.
        """
        forfaits = []
        if self.statut != cst.P_ATTEND_TIRAGE:
            for equipe in self.equipes():
                if equipe.resultat(self.numero).etat == cst.FORFAIT:
                    forfaits.append(equipe)

        return sorted(forfaits)

    def equipes_incompletes(self):
        """
        Retourne la liste des équipes dont les résultats
        de la manche en cours n'ont pas été saisis.
        """
        liste = []
        for equipe in self.equipes():
            if equipe.statut == cst.E_EN_COURS:
                liste.append(equipe)

        return liste

    def adversaires(self, equipe):
        """
        Retourne les adversaires d'une équipe.

        equipe (int or Equipe)
        """
        if type(equipe) == int:
            equipe = self.tournoi.equipe(equipe)

        adversaires = []
        if self.statut != cst.P_ATTEND_TIRAGE:
            for adv in equipe.resultat(self.numero).adversaires:
                adversaires.append(self.tournoi.equipe(adv))

        return sorted(adversaires)

    def demarrer(self, manches, chapeaux=[]):
        """
        Démarrer la partie avec un tirage donné

        manches (dict)       : assosciation de piquet - rencontres
        chapeaux (list)      : liste des chapeaux
        """
        if self.statut != cst.P_ATTEND_TIRAGE:
            if self.statut == cst.P_TERMINEE:
                raise StatutError(u"La partie n°%s est terminée." % self.numero)
            else:
                raise StatutError(u"La partie n°%s est en cours." % self.numero)
        debut = datetime.now()

        l = []
        # Ajout des manches
        for lieu, manche in manches.iteritems():
            for num in manche:
                l.append(num)
                adversaires = [equipe for equipe in manche if equipe != num]
                self.tournoi.equipe(num)._ajout_partie(debut, adversaires, piquet=lieu)

        # Ajout des chapeaux
        for num in chapeaux:
            l.append(num)
            self.tournoi.equipe(num)._ajout_partie(debut, etat=cst.CHAPEAU)

        # Ajout des forfaits parmi les équipes restantes du tournoi
        for equipe in self.tournoi.equipes():
            if equipe.numero not in l:
                equipe._ajout_partie(debut, etat=cst.FORFAIT)

        self.tournoi.modifie = True

    def ajout_equipe(self, equipe, etat, creer_manche_si_possible=True, piquet=None):
        """
        Ajout d'une équipe à la partie après que celle-ci soit démarrée.
        Permet d'inscrire de nouvelle équipes en cours de jeu. Si le nombre
        de chapeaux ainsi créer sont suffisament nombreux, une nouvelle
        rencontre est créée, les chapeaux sont alors supprimés.
        """
        if type(equipe) == int:
            equipe = self.tournoi.equipe(equipe)

        if self.statut == cst.P_ATTEND_TIRAGE:
            raise StatutError(u"La partie n°%s n'est pas démarrée (utiliser 'demarrer')." % self.numero)
        if equipe.partie_existe(self.numero):
            raise ValueError(u"L'équipe n°%s participe déjà à cette partie." % equipe.numero)
        if etat not in [cst.FORFAIT, cst.CHAPEAU]:
            raise ResultatError(u"Cette fonction ne peut être utilisée que pour ajouter un CHAPEAU ou un FORFAIT.")
        if creer_manche_si_possible and not piquet:
            piquet = self.piquets()[-1] + 1

        if self.tournoi.nb_parties() != 1:
            # Vérification que toutes les parties précédentes on été complétées
            for num in range(1, self.numero):
                equipe.resultat(num)

        if self.statut in [cst.P_EN_COURS, cst.P_COMPLETE]:
            if etat == cst.CHAPEAU:
                nouv_nb_chapeaux = len(self.chapeaux()) + 1
                if nouv_nb_chapeaux % self.tournoi.equipes_par_manche == 0 and creer_manche_si_possible:
                    chapeaux = [eq.numero for eq in self.chapeaux()]
                    # Modifier tous les chapeaux existant
                    for adv in self.chapeaux():
                        m = Manche(self.debut(), [equipe.numero] + [num for num in chapeaux if num != adv.numero])
                        m.piquet = piquet
                        adv._resultats[self.numero - 1] = m

                    # Ajouter l'équipe
                    equipe._ajout_partie(self.debut(), chapeaux, piquet=piquet)
                    self.tournoi.modifie = True
                else:
                    # Ajouter un chapeau supplementaire
                    equipe._ajout_partie(self.debut(), etat=cst.CHAPEAU)
                    self.tournoi.modifie = True
            else:
                equipe._ajout_partie(self.debut(), etat=cst.FORFAIT)
                self.tournoi.modifie = True
        else:
            equipe._ajout_partie(self.debut(), etat=cst.FORFAIT)
            self.tournoi.modifie = True

    def resultat(self, resultat_manche, fin=None):
        # Vérification: partie commencée
        if self.statut == cst.P_ATTEND_TIRAGE:
            raise StatutError(u"La partie n°%s n'est pas commencée." % self.numero)

        # Vérification de l'existance de la manche
        manche = resultat_manche.keys()
        manche.sort()

        if manche not in self.manches():
            raise ResultatError(u"La manche '%s' n'existe pas." % (manche))

        # Verification pas une manche chapeau
        if cst.CHAPEAU in manche:
            raise ResultatError(u"Le score des équipes chapeaux ne peut pas être modifié.")

        # Recherche des gagnants
        gagnants = []
        gagnants_pts = max(resultat_manche.values())
        for num, pts in resultat_manche.items():
            if pts == gagnants_pts:
                gagnants.append(num)

        # Vérification: nombre de points
        if gagnants_pts < self.tournoi.points_par_manche:
            raise ResultatError(u"Au moins une équipe doit avoir un score suppérieur ou égale à %s." %
                                self.tournoi.points_par_manche)

        for num in resultat_manche:
            if num in gagnants:
                etat = cst.GAGNE
            else:
                etat = cst.PERDU
            self.tournoi.equipe(int(num))._modif_partie(self.numero, resultat_manche[num], etat, fin)

        self.tournoi.modifie = True

    def piquets(self):
        """
        Retourne la liste des piquets utilisés pour cette
        partie.
        """
        piquets = []
        for equipe in self.equipes():
            numero = equipe.resultat(self.numero).piquet
            if numero not in piquets and numero is not None:
                piquets.append(numero)

        return sorted(piquets)

    def piquet_est_disponible(self, numero):
        """
        Vérifie que le piquet n'est pas attribué
        à une rencontre.

        numero (tout)
        """
        if numero in self.piquets():
            return False
        else:
            return True

    def raz(self):
        """
        Supprime les manches de chaque équipe correspondant à cette partie
        (utilisé pour supprimer une partie).
        """
        if self.statut != cst.P_ATTEND_TIRAGE:
            for equipe in self.equipes():
                equipe._suppr_partie(self.numero)
            self.tournoi.modifie = True
