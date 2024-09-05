# -*- coding: UTF-8 -*-

"""Round class definition"""

import copy
from datetime import datetime

from . import cst
from .match import Match
from .exception import StatusError, InconsistencyError, ResultError


class Round:
    """
    Class which represent a round. This class manipulates team data, it does not
    store any data (It's a proxy!).
    """

    def __init__(self, tournoi):
        self.tournoi = tournoi

    def __str__(self):
        return f"""
        Round n°{self.numero}:
            Players   : {self.nb_equipes()}
            Byes      : {len(self.chapeaux())}
            Forfeits  : {len(self.forfaits())}

            Status    : {self.statut}
        """

    def __int__(self):
        return self.numero

    @property
    def numero(self) -> int:
        """
        Return the round number.
        """
        if self in self.tournoi.parties():
            return self.tournoi.parties().index(self) + 1
        raise InconsistencyError("Cette partie n'appartient pas au tournoi en cours.")

    @property
    def statut(self) -> str:
        """
        Return the round status.

        P_ATTEND_TIRAGE => the draw has not been set
        P_EN_COURS      => the matches have been created
        P_COMPLETE      => the game is complete and it is the last one of the tournament
        P_TERMINEE      => the game is complete and it is not the last one of the tournament
        """
        if not self.equipes():
            # No team has a round with this game number
            return cst.P_ATTEND_TIRAGE

        for equipe in self.equipes():
            if equipe.statut == cst.E_EN_COURS and self == self.tournoi.partie_courante():
                return cst.P_EN_COURS

        if self == self.tournoi.partie_courante():
            return cst.P_COMPLETE
        return cst.P_TERMINEE

    def debut(self):
        """
        Return the start time of the round. None is returned if the
        round is not started.
        """
        if self.statut == cst.P_ATTEND_TIRAGE:
            return None

        for equipe in self.equipes():
            debut = copy.deepcopy(equipe.resultat(self.numero).debut)

        return debut

    def nb_equipes(self):
        """
        Return the number of teams playing (removes BYE and FORFEIT).
        """
        nb = 0
        for equipe in self.equipes():
            if equipe.resultat(self.numero).etat not in [cst.CHAPEAU, cst.FORFAIT]:
                nb += 1

        return nb

    def manches(self) -> list:
        """
        Return the matches of this round as a list of team numbers
        (BYE are not included).

        ex: [[1, 5], [2, 4], [3, 6]]
        """
        l = []
        matches = []
        if self.statut != cst.P_ATTEND_TIRAGE:
            for equipe in self.equipes():
                if equipe.numero not in l:
                    l.append(equipe.numero)

                    m = equipe.resultat(self.numero)
                    for a in m.adversaires:
                        l.append(a)

                    if m.adversaires != []:
                        matches.append(sorted([equipe.numero] + m.adversaires))

        return matches

    def chapeaux(self) -> list:
        """
        Return the list of BYE in this round.
        """
        byes = []
        if self.statut != cst.P_ATTEND_TIRAGE:
            for equipe in self.equipes():
                if equipe.resultat(self.numero).etat == cst.CHAPEAU:
                    byes.append(equipe)

        return sorted(byes)

    def equipes(self) -> list:
        """
        Return the list of teams that have a match defined for this round
        including BYE and FORFEIT. Except in exceptional cases (adding teams
        when a tournament has already started), a match is always defined
        for each round.
        """
        teams = []
        for equipe in self.tournoi.equipes():
            if equipe.partie_existe(self.numero):
                teams.append(equipe)
        return teams

    def forfaits(self) -> list:
        """
        Return the list of FORFEIT in this round.
        """
        forfeits = []
        if self.statut != cst.P_ATTEND_TIRAGE:
            for equipe in self.equipes():
                if equipe.resultat(self.numero).etat == cst.FORFAIT:
                    forfeits.append(equipe)

        return sorted(forfeits)

    def equipes_incompletes(self) -> list:
        """
        Return the list of teams whose results of the current
        match have not been entered.
        """
        incomplete = []
        for equipe in self.equipes():
            if equipe.statut == cst.E_EN_COURS:
                incomplete.append(equipe)

        return incomplete

    def adversaires(self, team) -> list:
        """
        Return a team's competitors.

        :param team: team number (int) or team (object)
        """
        if isinstance(team, int):
            team = self.tournoi.equipe(team)

        competitors = []
        if self.statut != cst.P_ATTEND_TIRAGE:
            for adv in team.resultat(self.numero).adversaires:
                competitors.append(self.tournoi.equipe(adv))

        return sorted(competitors)

    def demarrer(self, matches: dict, byes: list = ()) -> None:
        """
        Start the round with a given draw.

        :param matches: association location - match
        :param byes: list of equipe number set to BYE
        """
        if self.statut != cst.P_ATTEND_TIRAGE:
            if self.statut == cst.P_TERMINEE:
                raise StatusError("La partie n°%s est terminée." % self.numero)
            else:
                raise StatusError("La partie n°%s est en cours." % self.numero)
        debut = datetime.now()

        l = []
        # Ajout des manches
        for lieu, manche in matches.items():
            for num in manche:
                l.append(num)
                adversaires = [equipe for equipe in manche if equipe != num]
                self.tournoi.equipe(num)._ajout_partie(debut, adversaires, location=lieu)

        # Ajout des chapeaux
        for num in byes:
            l.append(num)
            self.tournoi.equipe(num)._ajout_partie(debut, etat=cst.CHAPEAU)

        # Ajout des forfaits parmi les équipes restantes du tournoi
        for equipe in self.tournoi.equipes():
            if equipe.numero not in l:
                equipe._ajout_partie(debut, etat=cst.FORFAIT)

        self.tournoi.changed = True

    def add_team(self, team, match_result: str, try_create_match: bool = True, location: int = None) -> None:
        """
        Add a team to the round after it has started and set it match result. This method
        allows to register new teams during the round.

        If the number of BYEs thus created is sufficient and `try_create_match`=True, a new
        match is created, and the corresponding BYEs are then deleted (`match_result` is 
        ignored).
        """
        if isinstance(team, int):
            team = self.tournoi.equipe(team)

        if self.statut == cst.P_ATTEND_TIRAGE:
            raise StatusError(f"La partie n°{self.numero} n'est pas démarrée (utiliser 'demarrer')")
        if team.partie_existe(self.numero):
            raise ValueError(f"L'équipe n°{team.numero} participe déjà à cette partie")
        if match_result not in [cst.FORFAIT, cst.CHAPEAU]:
            raise ResultError("Cette fonction ne peut être utilisée que pour ajouter un CHAPEAU ou un FORFAIT.")
        if try_create_match and not location:
            location = self.locations()[-1] + 1

        if self.tournoi.nb_parties() != 1:
            # Vérification que toutes les parties précédentes on été complétées
            for num in range(1, self.numero):
                team.resultat(num)

        if self.statut in [cst.P_EN_COURS, cst.P_COMPLETE]:
            if match_result == cst.CHAPEAU:
                nouv_nb_chapeaux = len(self.chapeaux()) + 1
                if nouv_nb_chapeaux % self.tournoi.equipes_par_manche == 0 and try_create_match:
                    chapeaux = [eq.numero for eq in self.chapeaux()]
                    # Modifier tous les chapeaux existant
                    for adv in self.chapeaux():
                        m = Match(self.debut(), [team.numero] + [num for num in chapeaux if num != adv.numero])
                        m.location = location
                        adv._resultats[self.numero - 1] = m

                    # Ajouter l'équipe
                    team._ajout_partie(self.debut(), chapeaux, location=location)
                    self.tournoi.changed = True
                else:
                    # Ajouter un chapeau supplementaire
                    team._ajout_partie(self.debut(), etat=cst.CHAPEAU)
                    self.tournoi.changed = True
            else:
                team._ajout_partie(self.debut(), etat=cst.FORFAIT)
                self.tournoi.changed = True
        else:
            team._ajout_partie(self.debut(), etat=cst.FORFAIT)
            self.tournoi.changed = True

    def add_result(self, match_result: dict, fin: datetime = None) -> None:
        """
        Register new score for a match.

        :param match_result: dictionary of team number and points
        :param fin: end match time
        """
        # Vérification: partie commencée
        if self.statut == cst.P_ATTEND_TIRAGE:
            raise StatusError("La partie n°%s n'est pas commencée." % self.numero)

        # Vérification de l'existance de la manche
        manche = sorted(match_result.keys())

        if manche not in self.manches():
            raise ResultError("La manche '%s' n'existe pas." % (manche))

        # Verification pas une manche chapeau
        if cst.CHAPEAU in manche:
            raise ResultError("Le score des équipes chapeaux ne peut pas être modifié.")

        # Recherche des gagnants
        gagnants = []
        gagnants_pts = max(match_result.values())
        for num, pts in match_result.items():
            if pts == gagnants_pts:
                gagnants.append(num)

        # Vérification: nombre de points
        if gagnants_pts < self.tournoi.points_par_manche:
            raise ResultError("Au moins une équipe doit avoir un score suppérieur ou égale à %s." %
                              self.tournoi.points_par_manche)

        for num in match_result:
            if num in gagnants:
                etat = cst.GAGNE
            else:
                etat = cst.PERDU
            self.tournoi.equipe(int(num))._modif_partie(self.numero, match_result[num], etat, fin)

        self.tournoi.changed = True

    def locations(self) -> list:
        """
        Returns the list of location used for this round.
        """
        locations = []
        for equipe in self.equipes():
            numero = equipe.resultat(self.numero).location
            if numero not in locations and numero is not None:
                locations.append(numero)

        return sorted(locations)

    def is_location_available(self, location: int) -> bool:
        """
        Check that the match location is not assigned to a match.

        :param location: location id
        """
        if location in self.locations():
            return False
        else:
            return True

    def delete(self) -> None:
        """
        Delete, for each team, the matches corresponding to this round
        (used to delete a round).
        """
        if self.statut != cst.P_ATTEND_TIRAGE:
            for equipe in self.equipes():
                equipe._suppr_partie(self.numero)
            self.tournoi.changed = True
