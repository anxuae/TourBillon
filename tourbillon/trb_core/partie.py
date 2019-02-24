#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Définitions des parties."""

#--- Import --------------------------------------------------------------------

import copy
from datetime import datetime, timedelta
from tourbillon.trb_core.manche import Manche
from tourbillon.trb_core.exceptions import NumeroError, DureeError, StatutError, IncoherenceError, ResultatError
from tourbillon.trb_core.constantes import (E_ATTEND_TIRAGE, E_JOUE,
                                            P_NON_DEMARREE, P_EN_COURS, P_COMPLETE, P_TERMINEE,
                                            CHAPEAU, GAGNE, PERDU, FORFAIT)
from tourbillon.trb_core.tirages.utile import creer_liste

#--- Classes -------------------------------------------------------------------

class Partie(object):
    """
    Représente une partie.
    
    Note: pour toutes les méthodes de cette class qui manipulent les équipes:
    
        - les valeurs retournées sont les numéros d'équipes
    """
    def __init__(self, parent):
        self.tournoi = parent
        self.numero_erreur_debut = True
        self.numero_erreur_resultat = True

    def __repr__(self):
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
                raise IncoherenceError, u"Cette partie n'appartient pas au tournoi en cours."
        return locals()

    numero = property(**numero())

    def statut():
        doc = """
        Retourne le status de la partie:
        
            P_NON_DEMARREE   => le tirage n'a pas été donné
            P_EN_COURS       => les manches ont été créées
            P_COMPLETE       => la partie est complete, c'est la dernière du tournoi
            P_TERMINEE       => la partie est complete, ce n'est pas la dernière du tournoi
        """

        def fget(self):

            if not self.equipes():
                # Aucune équipe n'a de manche avec ce numero de partie
                return P_NON_DEMARREE

            for equipe in self.equipes():
                if equipe.statut == E_JOUE and self == self.tournoi.partie_courante():
                    return P_EN_COURS

            if self == self.tournoi.partie_courante():
                return P_COMPLETE
            else:
                return P_TERMINEE
        return locals()

    statut = property(**statut())

    def debut(self):
        """
        Retourne l'heure de début de la partie. None est renvoyé
        si la partie n'est pas démarrée.
        """
        if self.statut == P_NON_DEMARREE:
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
            if equipe.resultat(self.numero).etat not in [CHAPEAU, FORFAIT]:
                nb += 1

        return nb

    def tirage(self):
        """
        Retourne les manches de cette partie sous forme
        de liste de numéro d'équipes. (Les chapeaux ne sont
        pas inclus).
        """
        l = []
        manches = []
        if self.statut != P_NON_DEMARREE:
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
        if self.statut != P_NON_DEMARREE:
            for equipe in self.equipes():
                if equipe.resultat(self.numero).etat == CHAPEAU:
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
        if self.statut != P_NON_DEMARREE:
            for equipe in self.equipes():
                if equipe.resultat(self.numero).etat == FORFAIT:
                    forfaits.append(equipe)

        return sorted(forfaits)

    def equipes_incompletes(self):
        """
        Retourne la liste des équipes dont les résultats
        de la manche en cours n'ont pas été saisis.
        """
        liste = []
        for equipe in self.equipes():
            if equipe.statut == E_JOUE:
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
        if self.statut != P_NON_DEMARREE:
            for adv in equipe.resultat(self.numero).adversaires:
                adversaires.append(self.tournoi.equipe(adv))

        return sorted(adversaires)

    def demarrer(self, manches, chapeaux=[]):
        """
        Démarrer la partie avec un tirage donné
        
        manches (dict)       : assosciation de piquet - rencontres
        chapeaux (list)      : liste des chapeaux
        """
        if self.statut != P_NON_DEMARREE:
            if self.statut == P_TERMINEE:
                raise StatutError, u"La partie n°%s est terminée." % self.numero
            else:
                raise StatutError, u"La partie n°%s est en cours." % self.numero
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
            self.tournoi.equipe(num)._ajout_partie(debut, etat=CHAPEAU)

        # Ajout des forfaits parmi les équipes restantes du tournoi
        for equipe in self.tournoi.equipes():
            if equipe.numero not in l:
                equipe._ajout_partie(debut, etat=FORFAIT)

        self._demarre = True
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

        if self.statut == P_NON_DEMARREE:
            raise StatutError, u"La partie n°%s n'est pas démarrée (utiliser 'demarrer')." % self.numero
        if equipe.partie_existe(self.numero):
            raise NumeroError, u"L'équipe n°%s participe déjà à cette partie." % equipe.numero
        if etat not in [FORFAIT, CHAPEAU]:
            raise ResultatError, u"Cette fonction ne peut être utilisée que pour ajouter un CHAPEAU ou un FORFAIT."
        if creer_manche_si_possible == True and not piquet:
            raise NumeroError, u"Un numéro de piquet est nécessaire"

        if self.tournoi.nb_parties() != 1:
            # Vérification que toutes les parties précédentes on été complétées
            for num in range(1, self.numero):
                equipe.resultat(num)

        if self.statut == P_EN_COURS:
            if etat == CHAPEAU:
                nouv_nb_chapeaux = len(self.chapeaux()) + 1
                if nouv_nb_chapeaux % self.tournoi.equipes_par_manche == 0 and creer_manche_si_possible == True:
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
                    equipe._ajout_partie(self.debut(), etat=CHAPEAU)
                    self.tournoi.modifie = True
            else:
                equipe._ajout_partie(self.debut(), etat=FORFAIT)
                self.tournoi.modifie = True
        else:
            equipe._ajout_partie(self.debut(), etat=FORFAIT)
            self.tournoi.modifie = True

    def resultat(self, resultat_manche, fin=None):
        # Vérification: partie commencée
        if self.statut == P_NON_DEMARREE:
            raise StatutError, u"La partie n°%s n'est pas commencée." % self.numero

        # Vérification de l'existance de la manche
        manche = resultat_manche.keys()
        manche.sort()

        if manche not in self.tirage():
            raise ResultatError, u"La manche '%s' n'existe pas." % (manche)

        # Verification pas une manche chapeau
        if CHAPEAU in manche:
            raise ResultatError, u"Le score des équipes chapeaux ne peut pas être modifié."

        # Recherche des gagnants
        gagnants = []
        gagnants_pts = max(resultat_manche.values())
        for num, pts in resultat_manche.items():
            if pts == gagnants_pts:
                gagnants.append(num)

        # Vérification: nombre de points
        if gagnants_pts < self.tournoi.points_par_manche:
            raise ResultatError, u"Au moins une équipe doit avoir un score suppérieur ou égale à %s." % self.tournoi.points_par_manche

        for num in resultat_manche:
            if num in gagnants:
                etat = GAGNE
            else:
                etat = PERDU
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
        if self.statut != P_NON_DEMARREE:
            for equipe in self.equipes():
                equipe._suppr_partie(self.numero)
            self.tournoi.modifie = True
