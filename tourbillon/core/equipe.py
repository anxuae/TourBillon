# -*- coding: UTF-8 -*-

"""Définition d'une équipe."""

from datetime import timedelta
from tourbillon.core.exceptions import LimiteError, StatutError
from tourbillon.core.joueur import Joueur, HISTORIQUE
from tourbillon.core.manche import Manche
from tourbillon.core.constantes import (CHAPEAU, GAGNE, PERDU, FORFAIT,
                                        M_EN_COURS, E_INCOMPLETE,
                                        E_ATTEND_TIRAGE, E_EN_COURS)


class Equipe(object):

    def __init__(self, parent, numero, joker=0):
        self.tournoi = parent
        self.joker = int(joker)
        self._num = int(numero)
        self._liste_joueurs = []
        self._resultats = []

    def __str__(self):
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
                        self.points(),
                        self.victoires(),
                        self.chapeaux(),
                        self.statut)

    def __int__(self):
        return self.numero

    def __cmp__(self, other):
        if int(self) > int(other):
            return 1
        elif int(self) == int(other):
            return 0
        else:
            return -1

    def _ajout_partie(self, debut, adversaires=[], etat=None, piquet=None):
        """
        Ajouter des résultats par défault pour l'équipe à la partie donnée.
        NE PAS UTILISER !!!!! (Manipulé par les objets Tournoi et Partie)

        debut (datetime)    : début de la partie

        adversaires (list)  : liste des adversaires rencontrés durant cette partie.

        etat (str)          : etat de l'équipe avant la manche: CHAPEAU ou FORFAIT.

        piquet (int)        : numéro de piquet où l'équipe joue.
        """
        if self.statut == E_EN_COURS or self.statut == E_INCOMPLETE:
            raise StatutError("Impossible de créer une partie pour l'équipe %s. (partie en cours: %s)" % (self.numero, len(self._resultats)))
        else:
            m = Manche(debut, adversaires)
            if etat == CHAPEAU:
                m.points = self.tournoi.points_par_manche
            if etat:
                m.etat = etat
            m.piquet = piquet
            self._resultats.append(m)

    def _suppr_partie(self, num_partie):
        """
        Supprimer les résultats de l'équipe à la partie donnée.
        NE PAS UTILISER !!!!! (Manipulé par les objets Tournoi et Partie)

        num_partie (int)    : numéro de la partie concernée.
        """
        num_partie = int(num_partie)
        if num_partie not in range(1, len(self._resultats) + 1):
            raise ValueError("Impossible de supprimer la partie %s pour l'équipe %s.(total parties: %s)" % (num_partie, self.numero, len(self._resultats)))
        else:
            self._resultats.pop(num_partie - 1)

    def _modif_partie(self, num_partie, points=None, etat=None, fin=None, piquet=None):
        """
        Modifier les résultats de l'équipe à la partie donnée.
        NE PAS UTILISER !!!!! (Manipulé par les objets Tournoi et Partie)

        num_partie (int)    : numéro de la partie concernée.

        points (int)        : points récoltés par l'équipe durant cette manche.

        etat (str)          : etat de l'équipe après la manche: GAGNE, PERDU.

        fin (datetime)      : date de fin de la partie.

        piquet (int)        : numéro de piquet où l'équipe joue.
        """
        num_partie = int(num_partie)
        if num_partie not in range(1, len(self._resultats) + 1):
            raise ValueError("La partie %s n'existe pas pour l'équipe %s." % (num_partie, self.numero))
        else:
            m = self._resultats[num_partie - 1]

            if etat is not None:
                m.etat = etat

            if etat == CHAPEAU:
                m.points = self.tournoi.points_par_manche
            elif points is not None and etat != FORFAIT:
                m.points = points

            if fin is not None:
                m.fin = fin

            if piquet is not None:
                m.piquet = piquet

    def numero():
        """
        Retourne le numero de l'équipe.
        """

        def fget(self):
            return self._num

        return locals()

    numero = property(**numero())

    def statut():
        doc = """
        Retourne le status de l'équipe:

            E_INCOMPLETE    => il manque des joueurs dans l'équipe
            E_EN_COURS          => une manche est en cours
            E_ATTEND_TIRAGE => la manche de la dernière partie est terminée
        """

        def fget(self):
            if self.tournoi.joueurs_par_equipe != len(self._liste_joueurs):
                return E_INCOMPLETE
            else:
                if len(self._resultats) == 0:
                    return E_ATTEND_TIRAGE
                else:
                    m = self._resultats[-1]
                    if m.statut == M_EN_COURS:
                        return E_EN_COURS
                    else:
                        return E_ATTEND_TIRAGE

        return locals()

    statut = property(**statut())

    def nb_joueurs(self):
        """
        Retourne le nombre de joueurs de l'équipe.
        """
        return len(self._liste_joueurs)

    def joueurs(self):
        """
        Retourne la liste des joeurs de l'équipe.
        """
        return self._liste_joueurs

    def ajout_joueur(self, prenom, nom, age='', date=None):
        """
        Ajouer un joueur dans l'équipe.

        prenom (str)
        nom (str)
        age (str)
        date (str)  : la date actuelle est utilisée par defaut
        """
        if self.tournoi.joueurs_par_equipe < len(self._liste_joueurs) + 1:
            raise LimiteError("Il ne peut y avoir plus de %s joueurs par équipe." % self.tournoi.joueurs_par_equipe)

        j = Joueur(prenom, nom, str(age), date_ajout=date)
        self._liste_joueurs.append(j)
        self.tournoi.modifie = True
        return j

    def suppr_joueurs(self):
        """
        Suppression de tous les joueurs de l'équipe.
        """
        for joueur in self._liste_joueurs:
            HISTORIQUE.pop(joueur.cle(), None)
        self._liste_joueurs = []
        self.tournoi.modifie = True

    def partie_existe(self, num_partie):
        """
        Retourne True si une manche est définie pour la partie
        spécifiée. Sauf cas exceptionel (ajout d'équipes lorsqu'un
        tournoi est déjà commencé), une manche est toujours définie
        pour chaque partie.

        num_partie (int)
        """
        try:
            self._resultats[num_partie - 1]
            return True
        except IndexError:
            return False

    def resultat(self, num_partie):
        """
        Retourne la manche de la partie concernée.

        num_partie (int)
        """
        num_partie = int(num_partie)
        if num_partie not in range(1, len(self._resultats) + 1):
            raise ValueError("La partie %s n'existe pas pour l'équipe %s." % (num_partie, self.numero))
        else:
            return self._resultats[num_partie - 1]

    def adversaires(self, partie_limite=None):
        """
        Retourne la liste des adversaires rencontrés depuis la
        première partie jusqu'au numéro de partie donnée.

        partie_limite (int)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)
        l = []
        for m in self._resultats[:partie_limite]:
            for ad in m.adversaires:
                l.append(ad)

        return l

    def manches(self, partie_limite=None):
        """
        Retourne la liste des numéro des équipes qui se sont
        réncontrées depuis la première partie jusqu'au numéro
        de partie donnée.

        partie_limite (int)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)
        l = []
        for m in self._resultats[:partie_limite]:
            if m.etat in [GAGNE, PERDU]:
                manche = m.adversaires + [self.numero]
                manche.sort()
                l.append(manche)

        return l

    def points(self, partie_limite=None):
        if partie_limite is None:
            partie_limite = len(self._resultats)

        l = [m.points for m in self._resultats[:partie_limite]]
        return sum(l)

    def victoires(self, partie_limite=None):
        if partie_limite is None:
            partie_limite = len(self._resultats)

        l = [m.etat for m in self._resultats[:partie_limite] if m.etat == GAGNE]
        return len(l)

    def forfaits(self, partie_limite=None):
        if partie_limite is None:
            partie_limite = len(self._resultats)

        l = [m.etat for m in self._resultats[:partie_limite] if m.etat == FORFAIT]
        return len(l)

    def chapeaux(self, partie_limite=None):
        if partie_limite is None:
            partie_limite = len(self._resultats)

        l = [m.etat for m in self._resultats[:partie_limite] if m.etat == CHAPEAU]
        return len(l)

    def parties(self, partie_limite=None):
        if partie_limite is None:
            partie_limite = len(self._resultats)

        # Les parties FORFAIT ne sont pas prises en compte
        l = [m.etat for m in self._resultats[:partie_limite] if m.etat != FORFAIT]
        return len(l)

    def moyenne_billon(self, partie_limite=None):
        if partie_limite is None:
            partie_limite = len(self._resultats)
        pts = self.points(partie_limite)

        # Résultat des parties FORFAIT et de la partie incompléte ne sont pas pris en compte
        parties = len([m.etat for m in self._resultats[:partie_limite] if m.statut != M_EN_COURS and m.etat != FORFAIT])
        if parties == 0:
            return 0
        else:
            return round(pts / parties, 2)

    def min_billon(self, partie_limite=None):
        if partie_limite is None:
            partie_limite = len(self._resultats)

        # Résultat des parties FORFAIT et de la partie incompléte ne sont pas pris en compte
        l = [m.points for m in self._resultats[:partie_limite] if m.statut != M_EN_COURS and m.etat != FORFAIT]
        if l == []:
            return 0
        else:
            return min(l)

    def max_billon(self, partie_limite=None):
        if partie_limite is None:
            partie_limite = len(self._resultats)

        l = [m.points for m in self._resultats[:partie_limite]]
        if l == []:
            return 0
        else:
            return max(l)

    def moyenne_duree(self, partie_limite=None):
        if partie_limite is None:
            partie_limite = len(self._resultats)

        # Résultat des parties FORFAIT, CHAPEAU et de la partie incompléte ne sont pas pris en compte
        l = [m.duree for m in self._resultats[:partie_limite] if m.duree is not None]
        if l == []:
            return timedelta(0)
        else:
            r = timedelta(0)
            for t in l:
                r += t
            return r // len(l)

    def min_duree(self, partie_limite=None):
        if partie_limite is None:
            partie_limite = len(self._resultats)

        # Résultat des parties FORFAIT, CHAPEAU et de la partie incompléte ne sont pas pris en compte
        l = [m.duree for m in self._resultats[:partie_limite] if m.duree is not None]
        if l == []:
            return timedelta(0)
        else:
            return min(l)

    def max_duree(self, partie_limite=None):
        if partie_limite is None:
            partie_limite = len(self._resultats)

        # Résultat des parties FORFAIT, CHAPEAU et de la partie incompléte ne sont pas pris en compte
        l = [m.duree for m in self._resultats[:partie_limite] if m.duree is not None]
        if l == []:
            return timedelta(0)
        else:
            return max(l)
