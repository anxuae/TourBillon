# -*- coding: UTF-8 -*-

"""Tournament class definition"""

import os
import random
from datetime import datetime
from functools import partial, cmp_to_key

import yaml

from . import cst
from .exception import FileError, StatusError, InconsistencyError
from .match import Match
from .team import Team
from .round import Round
from ..assets import banner


def load(filename):
    """
    Load a tournament from a file in YAML format.
    """
    with open(filename, 'r', encoding='utf-8') as fp:
        y = yaml.load(fp, Loader=yaml.Loader)
    tournament = Tournament()

    try:
        # Save date
        tournament.date_enregistrement = y['enregistrement']

        # Tournament info
        tournament.debut = y['tournoi']['debut']
        tournament.equipes_par_manche = y['tournoi']['equipes_par_manche']
        tournament.joueurs_par_equipe = y['tournoi']['joueurs_par_equipe']
        tournament.points_par_manche = y['tournoi']['points_par_manche']

        # Registration info
        for num in y['inscription']:
            equipe = tournament.ajout_equipe(num, y.get('jokers', {}).get(num, 0))
            for joueur in y['inscription'][num]:
                equipe.ajout_joueur(joueur[0], joueur[1], tournament.debut)

        # Rounds info
        for num in y['parties']:
            for data in y['parties'][num]:
                m = Match()
                m.charger(data)
                tournament.equipe(num)._resultats.append(m)

        # Number of rounds
        nb_parties = 0
        for equipe in tournament.equipes():
            if len(equipe._resultats) > nb_parties:
                nb_parties = len(equipe._resultats)

        # Round creation
        for num in range(1, nb_parties + 1):
            tournament._rounds.append(Round(tournament))

        tournament.date_chargement = datetime.now()
        tournament.changed = False
    except Exception as ex:
        raise InconsistencyError(f"File '{filename}' is corrupted ({ex}).")

    return tournament


def dump(tournament, filename):
    """
    Record a tournament in a file in YAML format.
    """
    if os.path.exists(filename) and not os.path.isfile(filename):
        raise FileError(f"'{filename}' is a directory")

    ancienne_date = tournament.date_enregistrement
    try:
        with open(filename, 'w', encoding='utf-8') as fp:
            fp.write(banner() + '\n')

            # Save date
            d = datetime.now()
            yaml.dump({'enregistrement': d}, fp, default_flow_style=False)

            # Tournament info
            y = {}
            y['tournoi'] = {}
            y['tournoi']['debut'] = tournament.debut
            y['tournoi']['equipes_par_manche'] = tournament.equipes_par_manche
            y['tournoi']['joueurs_par_equipe'] = tournament.joueurs_par_equipe
            y['tournoi']['points_par_manche'] = tournament.points_par_manche
            yaml.dump(y, fp, default_flow_style=False)

            # Registration info
            y = {}
            y['inscription'] = {}
            y['jokers'] = {}
            for equipe in tournament.equipes():
                y['inscription'][equipe.numero] = []
                y['jokers'][equipe.numero] = equipe.joker
                for joueur in equipe.joueurs():
                    y['inscription'][equipe.numero].append([joueur.prenom, joueur.nom])
            yaml.dump(y, fp, default_flow_style=False)

            # Rounds info
            y = {}
            y['parties'] = {}
            for equipe in tournament.equipes():
                y['parties'][equipe.numero] = [m.data for m in equipe._resultats]
            yaml.dump(y, fp, default_flow_style=False)

        tournament.date_enregistrement = d
        tournament.changed = False
    except Exception as ex:
        tournament.date_enregistrement = ancienne_date
        raise IOError(f"Tournament dump failed ({ex})")


class Tournament:

    """
    Class which represent a tournament. This class manipulates team data.
    """

    def __init__(self, equipes_par_manche=2, points_par_manche=12, joueurs_par_equipe=2):
        self.equipes_par_manche = equipes_par_manche
        self.joueurs_par_equipe = joueurs_par_equipe
        self.points_par_manche = points_par_manche

        self.debut = datetime.now()
        self.date_chargement = None
        self.date_enregistrement = None

        self.changed = False
        self._teams = {}
        self._rounds = []

    def __str__(self):
        texte = """
        Billon Tournament:
            Date                : %s
            Number of rounds    : %s
            Number of teams     : %s
            Team per match      : %s
            Points per match    : %s
            Players per team    : %s

            Status              : %s
        """
        return texte % (self.debut,
                        len(self.parties()),
                        len(self._teams),
                        self.equipes_par_manche,
                        self.points_par_manche,
                        self.joueurs_par_equipe,
                        self.statut)

    @property
    def statut(self):
        """
        Return tournament status.

        T_INSCRIPTION     => No round started
        T_ATTEND_TIRAGE   => Last round is finished
        T_PARTIE_EN_COURS => A round is in progress
        """
        # Impossibilité de créer une manche
        if self.nb_equipes() < self.equipes_par_manche:
            return cst.T_INSCRIPTION

        # Toutes les informations ne sont pas entrées
        for equipe in self.equipes():
            if equipe.statut == cst.E_INCOMPLETE:
                return cst.T_INSCRIPTION

        # Etat de la partie courante
        if self.partie_courante() is None:
            return cst.T_ATTEND_TIRAGE
        else:
            if self.partie_courante().statut in [cst.P_COMPLETE, cst.P_TERMINEE]:
                return cst.T_ATTEND_TIRAGE
            else:
                return cst.T_PARTIE_EN_COURS

    def statistiques(self, equipes_exclue=None, partie_limite=None):
        """
        Statistiques sur les parties précédentes des équipes spécifiées.
        """
        stat = {}
        classement = dict(self.classement())
        for equipe in self.equipes():
            if not equipes_exclue or equipe not in equipes_exclue:

                stat[equipe.numero] = {cst.STAT_POINTS: equipe.points(partie_limite),
                                       cst.STAT_VICTOIRES: equipe.victoires(partie_limite),
                                       cst.STAT_CHAPEAUX: equipe.chapeaux(partie_limite),
                                       cst.STAT_ADVERSAIRES: equipe.adversaires(partie_limite),
                                       cst.STAT_MANCHES: equipe.manches(partie_limite),
                                       cst.STAT_PLACE: classement[equipe]}
        return stat

    def locations(self):
        """
        Retourne une liste de numéros de piquets disponibles
        pour ce tournoi. Se base sur la partie précédentes
        afin de determiner si des numéros de piquets doivent
        être ignorés (piquet dégradé).

        Pas de piquet prévu pour les chapeaux.
        """
        nombre = self.nb_equipes() // self.equipes_par_manche
        locations = []
        i = 1
        if self.partie_courante():
            for p in self.partie_courante().locations():
                if len(locations) == nombre:
                    break
                locations.append(p)
            if locations:
                i = locations[-1] + 1

        while i <= nombre:
            locations.append(i)
            i += 1

        return locations

    def nb_equipes(self):
        """
        Retourne le nombre d'équipes inscrites.
        """
        return len(self._teams)

    def equipe(self, numero):
        """
        Retourne l'équipe avec le numéro spécifié.

        numero (int)
        """
        if type(numero) == Team:
            return numero
        elif numero not in self._teams:
            raise ValueError("L'équipe n°%s n'existe pas." % numero)
        else:
            return self._teams[numero]

    def equipes(self):
        """
        Retourne les équipes sous forme de liste.
        """
        return list(self._teams.values())

    def generer_numero_equipe(self):
        """
        Retourne un numéro d'équipe non utilisé
        """
        i = 1
        while i in self._teams:
            i += 1
        return i

    def generer_numero_joker(self):
        """
        Retourne un numéro aléetoir entre 1 et 1000 non utilisé
        """
        if self.nb_equipes() > 1000:
            raise ValueError("La limite de joueurs est atteinte")
        choix = list(range(1, 1001))
        for equipe in self.equipes():
            if equipe.joker in choix:
                choix.remove(equipe.joker)
        return random.choice(choix)

    def ajout_equipe(self, numero=None, joker=0):
        """
        Ajoute et retourne une nouvelle équipe avec le
        numéro spécifié. Si pas de numéro donné, le plus petit numéro
        disponible est choisi.

        numero (int)
        """
        if numero is None:
            numero = self.generer_numero_equipe()
        if numero in self._teams:
            raise ValueError("L'équipe n°%s existe déjà." % numero)

        eq = Team(self, numero, joker)
        self._teams[eq.numero] = eq
        self.changed = True
        return eq

    def suppr_equipe(self, numero):
        """
        Supprime et retourne une équipe avec le numéro spécifié.

        numero (int)
        """
        if numero not in self._teams:
            raise ValueError("L'équipe n°%s n'existe pas." % numero)

        eq = self._teams.pop(numero)
        self.changed = True
        return eq

    def modif_numero_equipe(self, numero, nouv_numero):
        """
        Modifie le numéro d'une équipe. Ne peut se faire que si
        aucune partie n'a été commencée.

        numero (int)
        nouv_numero (int)
        """
        if self.nb_parties() != 0:
            raise StatusError("Le numéro de l'équipe n°%s ne peut pas être changé." % numero)
        if nouv_numero in self._teams:
            raise ValueError("L'équipe n°%s existe déjà." % nouv_numero)

        equipe = self._teams.pop(numero)
        equipe._num = nouv_numero
        self._teams[nouv_numero] = equipe
        self.changed = True

    def nb_parties(self):
        """
        Retourne le nombre de parties.
        """
        return len(self.parties())

    def partie(self, numero):
        """
        Retourne la partie avec le numéro spécifié.

        numero (int)
        """
        if type(numero) == Round:
            return numero
        elif numero not in range(1, len(self.parties()) + 1):
            raise ValueError("La partie n°%s n'existe pas." % numero)
        else:
            return self.parties()[numero - 1]

    def partie_courante(self):
        """
        Retourne la dernière partie du tournoi.
        """
        if len(self.parties()) != 0:
            return self.parties()[-1]
        else:
            return None

    def parties(self):
        """
        Retourne les parties sous forme de liste.
        """
        return self._rounds

    def ajout_partie(self):
        """
        Ajoute et retourne une nouvelle partie.
        """
        if self.statut == cst.T_INSCRIPTION:
            raise StatusError("Impossible de créer une partie (inscriptions en cours).")
        elif self.statut == cst.T_PARTIE_EN_COURS:
            raise StatusError("Impossible de créer une nouvelle partie (partie courante: %s)." %
                              (self.partie_courante().statut))

        partie = Round(self)
        self.parties().append(partie)
        self.changed = True
        return partie

    def suppr_partie(self, numero):
        """
        Supprimer la partie correspondante au numéro spécifié.

        numero (int)
        """
        if numero > len(self.parties()) or numero < 1:
            raise ValueError("La partie n°%s n'existe pas." % numero)
        else:
            self.partie(numero).delete()
            self.parties().pop(numero - 1)
            self.changed = True

    def manches(self):
        """
        Retourne la liste des manches qui ont déjà eu lieu durant le tournoi.
        (Les chapeaux et les forfaits sont exclus des manches, voir la définition
        des manches d'une partie)
        """
        manches = []
        for partie in self.parties():
            for manche in partie.manches():
                manches.append(manche)
        return manches

    def comparer(self, team1, team2, partie_limite=None):
        """
        Comparer la force de deux équipes. La comparaison se fait en fonction du
        nombre de victoires (si activé), du nombre de points, du numéro joker
        et enfin de la durée moyenne d'une partie (si activé).

        equipe1 (Equipe instance)
        equipe2 (Equipe instance)
        partie_limite (int) limite pour le calcul pour la comparaison
        """
        if type(team1) != Team or type(team2) != Team:
            raise TypeError("Une équipe doit être comparée à une autre.")

        # priorité 1: comparaison des victoires
        vic = team1.victoires(partie_limite) + team1.chapeaux(partie_limite) - \
            team2.victoires(partie_limite) - team2.chapeaux(partie_limite)
        if vic > 0:
            vic = 1
        elif vic < 0:
            vic = -1

        if self.cmp_avec_victoires and vic != 0:
            return vic

        # priorité 2: comparaison des points
        pts = team1.points(partie_limite) - team2.points(partie_limite)
        if pts > 0:
            pts = 1
        elif pts < 0:
            pts = -1

        if pts != 0:
            return pts

        # priorité 3: comparaison des numéro joker
        joker = team1.joker - team2.joker
        if joker > 0:
            joker = 1
        elif joker < 0:
            joker = -1

        if self.cmp_avec_joker and joker != 0:
            return joker

        # priorité 4: comparaison des durées moyennes
        # (equipe superieure si durée mini)
        if team1.moyenne_duree(partie_limite) < team2.moyenne_duree(partie_limite):
            dur = 1
        elif team1.moyenne_duree(partie_limite) == team2.moyenne_duree(partie_limite):
            dur = 0
        elif team1.moyenne_duree(partie_limite) > team2.moyenne_duree(partie_limite):
            dur = -1

        if self.cmp_avec_duree and dur != 0:
            return dur

        return 0

    def classement(self, avec_victoires=True, avec_joker=True, avec_duree=True, partie_limite=None):
        """
        Retourne une liste de tuple indiquant l'équipe et sa place
        dans le classement. En cas d'égalité, la ou les places
        suivant les ex aequo ne seront plus utilisées afin de garder
        un numéro de place correspondant au nombre d'équipe.

        Exemple:
            [(12, 1), (4, 2), (7, 2), (9, 4)...]

        avec_victoires (bool): le classement tient compte du nombre de
                               victoires de l'équipe.
        avec_joker (bool)    : le classement tient compte du plus grand
                               numéro joker.
        avec_duree (bool)    : le classement tient compte de la durée
                               moyenne d'une partie
        partie_limite (int)  : limite pour le calcul du classement
        """
        self.cmp_avec_victoires = avec_victoires
        self.cmp_avec_joker = avec_joker
        self.cmp_avec_duree = avec_duree
        l = sorted(self.equipes(), key=cmp_to_key(partial(self.comparer, partie_limite=partie_limite)), reverse=True)

        classement = []

        if self.nb_equipes() != 0:
            place = 1
            classement.append((l[0], place))
            i = 1
            while i < len(l):
                if self.comparer(l[i - 1], l[i]) != 0:
                    place = i + 1
                classement.append((l[i], place))
                i += 1

        return classement
