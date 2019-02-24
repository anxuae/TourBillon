#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Définitions des parties."""

#--- Import --------------------------------------------------------------------

import copy
from datetime import datetime, timedelta
from tourbillon.trb_core.exceptions import NumeroError, DureeError, StatutError, IncoherenceError, ResultatError
from tourbillon.trb_core.constantes import (E_ATTEND_TIRAGE, E_MANCHE_EN_COURS,
                                            P_NON_DEMARREE, P_EN_COURS, P_COMPLETE, P_TERMINEE,
                                            CHAPEAU, GAGNE, PERDU, FORFAIT)

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
        def fget(self):
            if self.debut() is None:
                return P_NON_DEMARREE
            else:
                for equipe in self.tournoi.equipes():
                    if equipe.statut == E_MANCHE_EN_COURS and self == self.tournoi.partie_courante():
                        return P_EN_COURS

                if self == self.tournoi.partie_courante():
                    return P_COMPLETE
                else:
                    return P_TERMINEE
        return locals()

    statut = property(**statut())

    def debut(self):
        nb_equipes = 0
        for equipe in self.tournoi.equipes():
            try:
                debut = copy.deepcopy(equipe.resultat(self.numero)['debut'])
                nb_equipes += 1
            except NumeroError, e:
                pass

        if nb_equipes == self.tournoi.nb_equipes():
            # Toutes les équipes ont cette partie ajoutée à leurs données
            return debut
        elif nb_equipes == 0:
            # La partie n'a pas encore été ajoutée aux données des équipes
            # (Partie non démarrée)
            return None
        else:
            # Incohérence des données, le tournoi est peut être corrompu
            if self.numero_erreur_debut:
                print u"Le début de la partie n°%s n'est pas identique pour toutes les équipes. Le tournoi est peut être corrompu." % self.numero
                self.numero_erreur_debut = False
            return debut

    def tirage(self):
        l = []
        manches = []
        manche_chapeau = []
        if self.statut != P_NON_DEMARREE:
            for equipe in self.tournoi.equipes():
                if equipe.numero not in l:
                    l.append(equipe.numero)

                    try:
                        res = equipe.resultat(self.numero)
                        map(l.append, list(res['adversaires']))
                    except NumeroError, e:
                        res = None
                        print u"La partie n°%s n'est pas définie pour l'équipe n°%s. Le tournoi est peut être corrompu." % (self.numero, equipe.numero)

                    if res is not None:
                        if res['adversaires'] != []:
                            manches.append(sorted([equipe.numero] + res['adversaires']))
                        elif res['etat'] == CHAPEAU:
                            manche_chapeau.append(equipe.numero)

            if len(manche_chapeau) != 0:
                if len(manche_chapeau) >= self.tournoi.equipes_par_manche:
                    raise IncoherenceError, u"Le nombre de chapeaux pour la partie n°% est incorrect (%s chapeaux)" % (self.numero, len(manche_chapeau))
                manches.append(sorted(manche_chapeau))

        return manches

    def chapeaux(self):
        chapeaux = []
        if self.statut != P_NON_DEMARREE:
            for num in self.equipes():
                res = self.tournoi.equipe(num).resultat(self.numero)
                if res['etat'] == CHAPEAU:
                    chapeaux.append(num)
        chapeaux.sort()
        return chapeaux

    def forfaits(self):
        forfaits = []
        if self.statut != P_NON_DEMARREE:
            for equipe in self.tournoi.equipes():
                res = equipe.resultat(self.numero)
                if res['etat'] == FORFAIT:
                    forfaits.append(equipe.numero)
        forfaits.sort()
        return forfaits

    def nb_equipes(self):
        return len(self.equipes())

    def equipes(self):
        equipes = []
        if self.statut != P_NON_DEMARREE:
            for manche in self.tirage():
                map(equipes.append, manche)
            equipes.sort()
        return equipes

    def equipes_incompletes(self):
        liste = []
        for equipe in self.tournoi.equipes():
            if equipe.statut == E_MANCHE_EN_COURS:
                liste.append(equipe.numero)

        return liste

    def adversaires(self, num_equipe):
        l = []
        if self.statut != P_NON_DEMARREE:
            for manche in self.tirage():
                if num_equipe in manche:
                    l = manche
                    l.remove(num_equipe)
                    return l
        l.sort()
        return l

    def demarrer(self, manches, chapeaux=[]):
        if self.statut != P_NON_DEMARREE:
            if self.statut == P_TERMINEE:
                raise StatutError, u"La partie n°%s est terminée." % self.numero
            else:
                raise StatutError, u"La partie n°%s est en cours." % self.numero

        debut = datetime.now()

        l = []
        # Ajout des manches
        for manche in manches:
            for num in manche:
                l.append(num)
                adversaires = [equipe for equipe in manche if equipe != num]
                self.tournoi.equipe(num)._ajout_partie(debut, adversaires)

        # Ajout des chapeaux
        for num in chapeaux:
            l.append(num)
            self.tournoi.equipe(num)._ajout_partie(debut, etat=CHAPEAU)

        # Ajout des forfaits
        for equipe in self.tournoi.equipes():
            if equipe.numero not in l:
                equipe._ajout_partie(debut, etat=FORFAIT)

        self.tournoi.modifie = True

    def ajout_equipe(self, equipe, etat, creer_manche_si_possible=True):
        if type(equipe) == int:
            equipe = self.tournoi.equipe(equipe)

        if self.statut == P_NON_DEMARREE:
            raise StatutError, u"La partie n°%s n'est pas démarrée (utiliser 'demarrer')." % self.numero
        if equipe.numero in self.equipes():
            raise NumeroError, u"L'équipe n°%s participe déjà à cette partie." % equipe.numero
        if etat not in [FORFAIT, CHAPEAU]:
            raise ResultatError, u"Cette fonction ne peut être utilisée que pour ajouter un CHAPEAU ou un FORFAIT."
        if self.tournoi.nb_parties() != 1:
            # Vérification que toutes les parties précédentes on été complétées
            for num in range(1, self.numero):
                equipe.resultat(num)

        if self.statut == P_EN_COURS:
            if etat == CHAPEAU:
                nouv_nb_chapeaux = len(self.chapeaux()) + 1
                if nouv_nb_chapeaux % self.tournoi.equipes_par_manche == 0 and creer_manche_si_possible == True:
                    # Tous les chapeaux peuvent créer une manche
                    chapeaux = self.chapeaux()
                    # Modifier tous les chapeaux
                    for num in chapeaux:
                        adv = chapeaux + [equipe.numero]
                        adv.remove(num)
                        self.tournoi.equipe(num)._resultats[self.numero - 1] = { 'points':0,
                                                                               'etat':None,
                                                                                'debut':self.debut(),
                                                                                'duree':None,
                                                                                'adversaires':adv}
                    # Ajouter l'équipe
                    equipe._ajout_partie(self.debut(), chapeaux)
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

    def raz(self):
        if self.statut == P_TERMINEE:
            raise StatutError, u"Une partie terminée ne peut être remise à zéro."
        if self.statut != P_NON_DEMARREE:
            for equipe in self.tournoi.equipes():
                equipe._suppr_partie(self.numero)
            self.tournoi.modifie = True
