#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Définitions des équipes."""

#--- Import --------------------------------------------------------------------

from datetime import datetime, timedelta
from tourbillon.trb_core.exceptions import NumeroError, DureeError, LimiteError, StatutError
from tourbillon.trb_core.joueurs import Joueur, creer_id, HISTORIQUE
from tourbillon.trb_core.constantes import (CHAPEAU, GAGNE, PERDU, FORFAIT,
                                            E_INCOMPLETE, E_ATTEND_TIRAGE, E_MANCHE_EN_COURS)

#--- Classes -------------------------------------------------------------------

class Equipe(object):
    def __init__(self, parent, numero):
        self.tournoi = parent
        self._num = int(numero)
        self._liste_joueurs = []
        self._resultats = []

    def __repr__(self):
        texte = """
        Equipe n°%s
            Noms      : %s
            Points    : %s
            Victoires : %s
            Chapeaux  : %s
            
            Statut    : %s
        """
        noms = " / ".join([" ".join([joueur.prenom, joueur.nom]) for joueur in self._liste_joueurs])
        return texte % (self.numero, noms,
                        self.total_points(),
                        self.total_victoires(),
                        self.total_chapeaux(),
                        self.statut)

    def __int__(self):
        return self.numero

    def __cmp__(self, other):
        if int(self) > int(other):
            return 1
        elif int(self) == int(other):
            return 0
        else:
            return - 1

    def _ajout_partie(self, debut, adversaires=[], etat=None):
        """
        Ajouter des résultats par défault pour l'équipe à la partie donnée.
        NE PAS UTILISER !!!!! (Manipulé par les objets Tournoi et Partie)
        
        debut (datetime)    : début de la partie
        
        adversaires (list)  : liste des adversaires rencontrés durant cette partie.

        etat (str)          : etat de l'équipe avant la manche: CHAPEAU ou FORFAIT.
        """
        if self.statut == E_MANCHE_EN_COURS or self.statut == E_INCOMPLETE:
            raise StatutError, u"Impossible de créer une partie pour l'équipe %s. (partie en cours: %s)" % (self.numero, len(self._resultats))
        else:
            if etat == CHAPEAU:
                pts = self.tournoi.points_par_manche
                adversaires = []
            elif etat == FORFAIT:
                pts = 0
                adversaires = []
            else:
                pts = 0
            self._resultats.append({'points':pts,
                                    'etat':etat,
                                    'debut':debut,
                                    'duree':None,
                                    'adversaires':adversaires})

    def _suppr_partie(self, num_partie):
        """
        Supprimer les résultats de l'équipe à la partie donnée.
        NE PAS UTILISER !!!!! (Manipulé par les objets Tournoi et Partie)
        
        num_partie (int)    : numéro de la partie concernée.
        """
        num_partie = int(num_partie)
        if num_partie not in range(1, len(self._resultats) + 1):
            raise NumeroError, u"Impossible de supprimer la partie %s pour l'équipe %s.(total parties: %s)" % (num_partie, self.numero, len(self._resultats))
        else:
            self._resultats.pop(num_partie - 1)

    def _modif_partie(self, num_partie, points=None, etat=None, fin=None):
        """
        Modifier les résultats de l'équipe à la partie donnée.
        NE PAS UTILISER !!!!! (Manipulé par les objets Tournoi et Partie)
        
        num_partie (int)    : numéro de la partie concernée.
        
        points (int)        : points récoltés par l'équipe durant cette manche.
        
        etat (str)          : etat de l'équipe après la manche: GAGNE, PERDU.
        
        fin (datetime)      : date de fin de la partie.
        """
        num_partie = int(num_partie)
        if num_partie not in range(1, len(self._resultats) + 1):
            raise NumeroError, u"La partie %s n'existe pas pour l'équipe %s." % (num_partie, self.numero)
        else:
            if etat == CHAPEAU:
                points = self.tournoi.points_par_manche
                fin = None
            elif etat == FORFAIT:
                points = 0
                fin = None

            if points is not None:
                self._resultats[num_partie - 1]['points'] = points

            if etat is not None:
                self._resultats[num_partie - 1]['etat'] = etat

            etat = self._resultats[num_partie - 1]['etat']

            if (etat == PERDU or etat == GAGNE) and fin is not None:
                self._resultats[num_partie - 1]['duree'] = fin - self._resultats[num_partie - 1]['debut']

    def numero():
        """
        Retourne le numero de l'équipe.
        """
        def fget(self):
            return self._num
        return locals()

    numero = property(**numero())

    def statut():
        def fget(self):
            if self.tournoi.joueurs_par_equipe != len(self._liste_joueurs):
                return E_INCOMPLETE
            else:
                if len(self._resultats) == 0:
                    return E_ATTEND_TIRAGE
                else:
                    partie = self._resultats[-1]
                    if partie['etat'] == CHAPEAU or partie['etat'] == FORFAIT:
                        return E_ATTEND_TIRAGE
                    elif partie['duree'] is None:
                        return E_MANCHE_EN_COURS
                    else:
                        return E_ATTEND_TIRAGE
        return locals()

    statut = property(**statut())

    def nb_joueurs(self):
        return len(self._liste_joueurs)

    def joueurs(self):
        return self._liste_joueurs

    def ajout_joueur(self, prenom, nom, age=''):
        if self.tournoi.joueurs_par_equipe < len(self._liste_joueurs) + 1:
            raise LimiteError, u"Il ne peut y avoir plus de %s joueurs par équipe." % self.tournoi.joueurs_par_equipe

        j = Joueur(prenom, nom, str(age))
        self._liste_joueurs.append(j)
        self.tournoi.modifie = True
        return j

    def suppr_joueurs(self):
        for joueur in self._liste_joueurs:
            if HISTORIQUE is not None:
                HISTORIQUE.pop(joueur.id)
        self._liste_joueurs = []
        self.tournoi.modifie = True

    def resultat(self, num_partie):
        num_partie = int(num_partie)
        if num_partie not in range(1, len(self._resultats) + 1):
            raise NumeroError, u"La partie %s n'existe pas pour l'équipe %s." % (num_partie, self.numero)
        else:
            return self._resultats[num_partie - 1]

    def adversaires(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)
        l = []
        for resultat in self._resultats[:partie_limite]:
            for ad in resultat['adversaires']:
                l.append(ad)

        return l

    def manches(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)
        l = []
        for resultat in self._resultats[:partie_limite]:
            if resultat['etat'] == GAGNE or resultat['etat'] == PERDU:
                manche = resultat['adversaires'] + [self.numero]
                manche.sort()
                l.append(manche)

        return l

    def total_points(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)

        l = [resultat['points'] for resultat in self._resultats[:partie_limite]]
        return sum(l)

    def total_victoires(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)

        l = [resultat['etat'] for resultat in self._resultats[:partie_limite] if resultat['etat'] == GAGNE]
        return len(l)

    def total_forfaits(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)

        l = [resultat['etat'] for resultat in self._resultats[:partie_limite] if resultat['etat'] == FORFAIT]
        return len(l)

    def total_chapeaux(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)

        l = [resultat['etat'] for resultat in self._resultats[:partie_limite] if resultat['etat'] == CHAPEAU]
        return len(l)

    def total_parties(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)

        # Les parties FORFAIT ne sont pas prises en compte
        l = [resultat['etat'] for resultat in self._resultats[:partie_limite] if resultat['etat'] != FORFAIT]
        return len(l)

    def moyenne_billon(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)
        pts = self.total_points(partie_limite)

        # Résultat des parties FORFAIT et de la partie incompléte ne sont pas pris en compte
        parties = len([resultat['etat'] for resultat in self._resultats[:partie_limite] if resultat['etat'] != FORFAIT and resultat['etat'] != None])
        if parties == 0:
            return 0
        else:
            return round(pts * 1.0 / parties, 2)

    def min_billon(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)

        # Résultat des parties FORFAIT et de la partie incompléte ne sont pas pris en compte
        l = [resultat['points'] for resultat in self._resultats[:partie_limite] if resultat['etat'] != FORFAIT and resultat['etat'] != None]
        if l == []:
            return 0
        else:
            return min(l)

    def max_billon(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)

        l = [resultat['points'] for resultat in self._resultats[:partie_limite]]
        if l == []:
            return 0
        else:
            return max(l)

    def moyenne_duree(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)

        # Résultat des parties FORFAIT, CHAPEAU et de la partie incompléte ne sont pas pris en compte
        l = [resultat['duree'] for resultat in self._resultats[:partie_limite] if resultat['duree'] is not None]
        if l == []:
            return timedelta(0)
        else:
            r = timedelta(0)
            for t in l:
                r += t
            return r / len(l)

    def min_duree(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)

        # Résultat des parties FORFAIT, CHAPEAU et de la partie incompléte ne sont pas pris en compte
        l = [resultat['duree'] for resultat in self._resultats[:partie_limite] if resultat['duree'] is not None]
        if l == []:
            return timedelta(0)
        else:
            return min(l)

    def max_duree(self, partie_limite=None):
        if partie_limite is None:partie_limite = len(self._resultats)

        # Résultat des parties FORFAIT, CHAPEAU et de la partie incompléte ne sont pas pris en compte
        l = [resultat['duree'] for resultat in self._resultats[:partie_limite] if resultat['duree'] is not None]
        if l == []:
            return timedelta(0)
        else:
            return max(l)
