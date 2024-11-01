# -*- coding: UTF-8 -*-

"""Team class definition"""

from datetime import datetime, timedelta

from . import cst
from .exception import BoundError, StatusError
from .match import Match
from .player import Player, PlayerHistory


class Team:

    """
    Class which represent a team. This class store all team data for the
    tournament.
    """

    def __init__(self, tournoi, numero, joker=0):
        self.tournoi = tournoi
        self.joker = int(joker)
        self._num = int(numero)
        self._liste_joueurs = []
        self._resultats = []

    def __str__(self):
        return f"""
        Team n°{self.numero}
            Names     : {" / ".join([" ".join([joueur.prenom, joueur.nom]) for joueur in self._liste_joueurs])}
            Points    : {self.points()}
            Victories : {self.victoires()}
            Byes      : {self.chapeaux()}

            Status    : {self.statut}
        """

    def __int__(self):
        return self.numero

    def __hash__(self):
        return id(self)

    def __lt__(self, other):
        return int(self) < int(other)

    def __le__(self, other):
        return int(self) <= int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __ge__(self, other):
        return int(self) >= int(other)

    def __eq__(self, other):
        return int(self) == int(other)

    def __ne__(self, other):
        return int(self) != int(other)

    def _ajout_partie(self, debut: datetime, adversaires: list = [], etat: str = None, location: int = None):
        """
        Add results for the team to the given round.

        /!\/!\/!\ DO NOT USE OUTSIDE OF TOURNAMENT AND ROUND CLASSES /!\/!\/!\

        :param debut: match start date
        :param adversaires: competitors list
        :param etat: match status before it starts (BYE, FORFEIT)
        :param location: match location ID
        """
        if self.statut == cst.E_EN_COURS or self.statut == cst.E_INCOMPLETE:
            raise StatusError(
                f"Cannot create round for team n°{self.numero}. (round in progress: {len(self._resultats)})")
        else:
            m = Match(debut, adversaires)
            if etat == cst.CHAPEAU:
                m.points = self.tournoi.points_par_manche
            if etat:
                m.etat = etat
            m.location = location
            self._resultats.append(m)

    def _suppr_partie(self, num_partie: int):
        """
        Delete the team's results in the given round.

        /!\/!\/!\ DO NOT USE OUTSIDE OF TOURNAMENT AND ROUND CLASSES /!\/!\/!\

        :param num_partie: round number
        """
        num_partie = int(num_partie)
        if num_partie not in range(1, len(self._resultats) + 1):
            raise ValueError(
                f"Cannot delete round n°{num_partie} pour l'équipe {self.numero} (total parties: {len(self._resultats)})")
        else:
            self._resultats.pop(num_partie - 1)

    def _modif_partie(self, num_partie: int, points: int = None, etat: str = None, fin: datetime = None, location: int = None):
        """
        Change the team's results in the given game.
        
        /!\/!\/!\ DO NOT USE OUTSIDE OF TOURNAMENT AND ROUND CLASSES /!\/!\/!\

        :param num_partie: round number
        :param points: points obtained by the team for the given round
        :param etat: match status (VICTORY, LOSS)
        :param fin: match end date
        :param location: match location ID
        """
        num_partie = int(num_partie)
        if num_partie not in range(1, len(self._resultats) + 1):
            raise ValueError(f"Round n°{num_partie} does not exists for team n°{self.numero}")
        else:
            m = self._resultats[num_partie - 1]

            if etat is not None:
                m.etat = etat

            if etat == cst.CHAPEAU:
                m.points = self.tournoi.points_par_manche
            elif points is not None and etat != cst.FORFAIT:
                m.points = points

            if fin is not None:
                m.fin = fin

            if location is not None:
                m.location = location

    @property
    def numero(self) -> int:
        """
        Return the team number.
        """
        return self._num

    @property
    def statut(self) -> str:
        """
        Return the team status.

        E_INCOMPLETE    => some players are missing in the team
        E_EN_COURS      => match with this team is in progress
        E_ATTEND_TIRAGE => match of the last round is completed
        """
        if self.tournoi.joueurs_par_equipe != len(self._liste_joueurs):
            return cst.E_INCOMPLETE
        else:
            if len(self._resultats) == 0:
                return cst.E_ATTEND_TIRAGE
            else:
                m = self._resultats[-1]
                if m.statut == cst.M_EN_COURS:
                    return cst.E_EN_COURS
                else:
                    return cst.E_ATTEND_TIRAGE

    def joueurs(self):
        """
        Return players.
        """
        return self._liste_joueurs

    def ajout_joueur(self, prenom: str, nom: str, date=None):
        """
        Add a new player.

        :param prenom: firstname
        :param nom: lastname
        :param date: date when the player join the team
        """
        if self.tournoi.joueurs_par_equipe < len(self._liste_joueurs) + 1:
            raise BoundError(f"A team shall be composed of {self.tournoi.joueurs_par_equipe} players")

        j = Player(prenom, nom, date_ajout=date)
        self._liste_joueurs.append(j)
        self.tournoi.changed = True
        return j

    def suppr_joueurs(self):
        """
        Remove all players.
        """
        for joueur in self._liste_joueurs:
            PlayerHistory().remove(joueur.key)
        self._liste_joueurs = []
        self.tournoi.changed = True

    def partie_existe(self, num_partie: int):
        """
        Return True if a match is defined for the specified round. Except in
        exceptional cases (adding teams after a tournament has already started),
        a match is always defined for each round.

        :param num_partie: round number
        """
        try:
            self._resultats[num_partie - 1]
            return True
        except IndexError:
            return False

    def resultat(self, num_partie: int):
        """
        Return the match result for the given round number.

        :param num_partie: round number
        """
        num_partie = int(num_partie)
        if num_partie not in range(1, len(self._resultats) + 1):
            raise ValueError(f"Round n°{num_partie} not created for team {self.numero}")
        else:
            return self._resultats[num_partie - 1]

    def adversaires(self, partie_limite: int = None):
        """
        Return the list of competitors encountered since the
        first to the given round number.

        :param partie_limite: last round number (included)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)
        l = []
        for m in self._resultats[:partie_limite]:
            for ad in m.adversaires:
                l.append(ad)

        return l

    def manches(self, partie_limite: int = None):
        """
        Return the list of team numbers already encountered since the
        first to the given round number.

        :param partie_limite: last round number (included)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)
        l = []
        for m in self._resultats[:partie_limite]:
            if m.etat in [cst.GAGNE, cst.PERDU]:
                manche = sorted(m.adversaires + [self.numero])
                l.append(manche)

        return l

    def points(self, partie_limite: int = None):
        """
        Return the sum of the points since the first
        to the given round number.

        :param partie_limite: last round number (included)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)

        l = [m.points for m in self._resultats[:partie_limite]]
        return sum(l)

    def victoires(self, partie_limite: int = None):
        """
        Return the number of victories since the first
        to the given round number.

        :param partie_limite: last round number (included)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)

        l = [m.etat for m in self._resultats[:partie_limite] if m.etat == cst.GAGNE]
        return len(l)

    def forfaits(self, partie_limite: int = None):
        """
        Return the number of forfeits since the first
        to the given round number.

        :param partie_limite: last round number (included)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)

        l = [m.etat for m in self._resultats[:partie_limite] if m.etat == cst.FORFAIT]
        return len(l)

    def chapeaux(self, partie_limite: int = None):
        """
        Return the number of byes since the first
        to the given round number.

        :param partie_limite: last round number (included)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)

        l = [m.etat for m in self._resultats[:partie_limite] if m.etat == cst.CHAPEAU]
        return len(l)

    def parties(self, partie_limite: int = None):
        """
        Return the number of rounds which are not forfeit since the first
        to the given round number.

        :param partie_limite: last round number (included)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)

        # Les parties FORFAIT ne sont pas prises en compte
        l = [m.etat for m in self._resultats[:partie_limite] if m.etat != cst.FORFAIT]
        return len(l)

    def moyenne_billon(self, partie_limite: int = None):
        """
        Return the average points of a match since the first
        to the given round number.

        :param partie_limite: last round number (included)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)
        pts = self.points(partie_limite)

        # Résultat des parties FORFAIT et de la partie incompléte ne sont pas pris en compte
        parties = len([m.etat for m in self._resultats[:partie_limite]
                      if m.statut != cst.M_EN_COURS and m.etat != cst.FORFAIT])
        if parties == 0:
            return 0
        else:
            return round(pts / parties, 2)

    def min_billon(self, partie_limite: int = None):
        """
        Returns the min points of a match from the first
        to the given round number.

        :param partie_limite: last round number (included)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)

        # Résultat des parties FORFAIT et de la partie incompléte ne sont pas pris en compte
        l = [m.points for m in self._resultats[:partie_limite] if m.statut != cst.M_EN_COURS and m.etat != cst.FORFAIT]
        if l == []:
            return 0
        else:
            return min(l)

    def max_billon(self, partie_limite: int = None):
        """
        Return the max points of a match since the first
        to the given round number.

        :param partie_limite: last round number (included)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)

        l = [m.points for m in self._resultats[:partie_limite]]
        if l == []:
            return 0
        else:
            return max(l)

    def moyenne_duree(self, partie_limite: int = None):
        """
        Return the average duration of a match since the first
        to the given round number.

        :param partie_limite: last round number (included)
        """
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

    def min_duree(self, partie_limite: int = None):
        """
        Return the min duration of a match since the first
        to the given round number.

        :param partie_limite: last round number (included)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)

        # Résultat des parties FORFAIT, CHAPEAU et de la partie incompléte ne sont pas pris en compte
        l = [m.duree for m in self._resultats[:partie_limite] if m.duree is not None]
        if l == []:
            return timedelta(0)
        else:
            return min(l)

    def max_duree(self, partie_limite: int = None):
        """
        Return the max duration of a match since the first
        to the given round number.

        :param partie_limite: last round number (included)
        """
        if partie_limite is None:
            partie_limite = len(self._resultats)

        # Résultat des parties FORFAIT, CHAPEAU et de la partie incompléte ne sont pas pris en compte
        l = [m.duree for m in self._resultats[:partie_limite] if m.duree is not None]
        if l == []:
            return timedelta(0)
        else:
            return max(l)
