# -*- coding: UTF-8 -*-

"""Utility functions fro draws"""

from math import factorial
from itertools import combinations as cnp
from datetime import datetime, timedelta
from threading import Thread, Event

from ..exception import DrawError, DrawStopError, DrawResultError


def len_cnp(n, p):
    """
    Retourne le nombre de combinaisons (cnp) possibles pour tirer 'p' équipes
    parmis 'n' equipes sans répétition.
    """
    if isinstance(n, list) or isinstance(n, tuple):
        n = len(n)
    return factorial(n) // (factorial(p) * factorial(n - p))


def tri_stat(statistiques, caracteristique):
    d = {}
    for eq in statistiques:
        valeur = statistiques[eq][caracteristique]
        d.setdefault(valeur, []).append(eq)
    return d


def nb_chapeaux_necessaires(nb_equipes, nb_par_manche):
    if nb_equipes < nb_par_manche:
        raise DrawError("Pas assez d'équipes (nb équipes: %s, nb par manche: %s)" % (nb_equipes, nb_par_manche))
    else:
        return nb_equipes % nb_par_manche


def dernieres_equipes(statistiques, n=1):
    """
    Retourne la liste des n dernières équipes.
    """
    r = []
    d = tri_stat(statistiques, 'place')
    places = d.keys()
    places.sort()
    for p in places:
        r += d[p]

    return r[-n:]


def creer_manches(liste_equipes, equipes_par_manche):
    """
    Création d'un tirage à partir d'une liste d'équipes.
    """
    i = 1
    tirage = []
    manche = liste_equipes[0: equipes_par_manche]
    while manche != []:
        tirage.append(manche)
        manche = liste_equipes[i * equipes_par_manche:i * equipes_par_manche + equipes_par_manche]
        i += 1
    return tirage


def creer_liste(tirage):
    """
    Creation d'une liste d'équipes à partir d'un tirage.
    """
    liste_equipes = []
    for manche in tirage:
        for equipe in manche:
            liste_equipes.append(equipe)
    return liste_equipes


def tirage_texte(statistiques, manches):
    texte = []

    for manche in manches:
        pts = []
        nv = []
        for equipe in manche:
            pts.append(statistiques[equipe]['points'])
            nv.append(statistiques[equipe]['victoires'] + statistiques[equipe]['chapeaux'])

        # Evaluation de l'écart max de points
        dp = max(pts) - min(pts)
        # Evaluation de l'écart max de victoires (+ chapeaux)
        dv = max(nv) - min(nv)

        # Calcul de la redondance (1 pour toute rencontrée + 1/n par semirencontre)
        # Une semirencontre est un jeu de 2 équipes. Une manche peut comporter
        # plus de deux équipes donc il y a cnp(manche, 2) posibilités.
        semirencontres = {}
        nrc = 0
        for vu in cnp(manche, 2):
            vu = sorted(vu)
            cle = "_".join([str(num) for num in vu])
            semirencontres[cle] = statistiques[vu[1]]['adversaires'].count(vu[0])

        r = []
        for equipe in statistiques:
            if manche in statistiques[equipe]['manches'] and manche not in r:
                # La manche a déjà été disputée
                r.append(manche)
                for k in semirencontres:
                    semirencontres[k] -= 1
                nrc += 1

        # Completer avec un un nombre < 1 pour les rencontres 2 à 2 effectuées
        # dans d'autres manches que celles redondantes
        nrc += 1 - (semirencontres.values().count(0) / len_cnp(manche, 2))

        texte.append("%-15s: diff points = %-5s, redondance = %-5s, disparité = %-5s" % (manche, dp, nrc, dv))

    return '\n'.join(texte)


def temps_texte(tps):
    """
    Convertie un objet 'timedelta' en un texte.
    """
    minutes = int(tps.total_seconds() / 60)
    secondes = int(tps.total_seconds() % 60)
    return "%.2im%.2is" % (minutes, secondes)


class NonValide:

    """
    Cette classe represent une manche non valide et embarque
    sa "raison" de n'être pas valide.
    """

    def __init__(self, valeur=None, redondance=0, disparite=0):
        if type(valeur) == self.__class__:
            self.redondance = valeur.redondance
            self.disparite = valeur.disparite
        else:
            self.redondance = redondance
            self.disparite = disparite

    def raison(self):
        return self.redondance | self.disparite

    def __eq__(self, other):
        if type(other) == type:
            if self.__class__ == other:
                return True
            else:
                return False
        elif type(other) == self.__class__:
            if self.raison() == other.raison():
                return True
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        if type(other) == type:
            if self.__class__ != other:
                return True
            else:
                return False
        elif type(other) == self.__class__:
            if self.raison() != other.raison():
                return True
            else:
                return False
        else:
            return False

    def __or__(self, other):
        if other is None:
            return self
        v = self.raison() | other.raison()

        if v == NV_REDONDANCE.raison():
            return NonValide(redondance=1)
        elif v == NV_DISPARITE.raison():
            return NonValide(disparite=2)
        elif v == NV_REDONDANCE.raison() | NV_DISPARITE.raison():
            return NonValide(redondance=1, disparite=2)
        else:
            raise TypeError("unsupported operand type(s) for |: '%s' and '%s'" % (type(self), type(other)))

    __ror__ = __or__


NV = NonValide
NV_REDONDANCE = NonValide(redondance=1)
NV_DISPARITE = NonValide(disparite=2)


class BaseThreadTirage(Thread):
    """
    Base de la classe ThreadTirage.
    """
    NOM = ""
    DESCRIPTION = ""
    DEFAUT = {}

    def __init__(self, equipes_par_manche, statistiques, chapeaux=[], callback=None):
        Thread.__init__(self)
        if self.__class__ == BaseThreadTirage:
            raise NotImplementedError("Classe abstraite")

        self._stop = Event()
        self._progression = 0
        self._debut = datetime.now()
        self._chrono = datetime.now()
        self.daemon = True
        self.config = {}
        self.equipes_par_manche = equipes_par_manche
        self.statistiques = statistiques
        self.erreur = None
        self.tirage = []
        self.chapeaux = chapeaux
        self.callback = callback

        # Parametres par défaut de l'algorithme
        self.configurer(**dict([(cle.lower(), valeur) for cle, valeur in self.DEFAUT.items()]))

    def __str__(self):
        return "<generateur %s>" % self.NOM

    def _arret_utilisateur(self):
        if self._stop.isSet() == True:
            raise DrawStopError("Arrêt demmandé par l'utilisateur.")

    def configurer(self, **kwargs):
        self.config.update(kwargs)
        self.config['statistiques'] = self.statistiques
        self.config['equipes_par_manche'] = self.equipes_par_manche
        self.config['arret_utilisateur'] = self._arret_utilisateur
        self.config['rapport'] = self.rapport

    def start(self, join=False):
        self._stop.clear()
        Thread.start(self)
        if join:
            self.join(20 * 60)  # 20 min max

    def run(self):
        nb_eq = len(self.statistiques)
        nb_chapeaux = nb_chapeaux_necessaires(nb_eq, self.equipes_par_manche)
        try:
            if len(self.chapeaux) >= self.equipes_par_manche:
                # ERREUR 100: Le nombre de chapeaux ne peut pas être égale au nombre d'équipes par manche
                args = [len(self.chapeaux), self.equipes_par_manche]
                raise DrawResultError(100, args)

            if nb_chapeaux - len(self.chapeaux) < 0:
                # ERREUR 102: Nombre de chapeaux fourni incorrecte
                args = (nb_chapeaux_necessaires(nb_eq, self.equipes_par_manche) - len(self.chapeaux),)
                raise DrawResultError(102, args)

            self._debut = datetime.now()
            self.demarrer()
            msg = "\nAlgorithme terminé (temps de calcul: %s)." % temps_texte(self._chrono - self._debut)
            self.rapport(100, msg)
        except DrawResultError as ex:
            msg = "\nAlgorithme terminé (%s)." % ex
            self.erreur = e
            self.rapport(100, msg)
        except DrawStopError as ex:
            msg = "\nAlgorithme terminé (arrêt utilisateur)."
            self.erreur = ex
            self.rapport(100, msg)

    def demarrer(self):
        """
        Cette methode DOIT être surchargée. Elle démarre l'algorithme
        de tirage.
        """
        raise NotImplementedError('Cette methode DOIT être surchargée')

    def rapport(self, valeur=-1, message=None):
        """
        Cette methode est utilisée pour afficher la progression d'un tirage.
        Le pourcentage est affiché tous les 5%
        """
        self._chrono = datetime.now()
        diff = abs(valeur - self._progression)

        if self._progression <= 0:
            tps_restant = timedelta(0, 1800)
        else:
            tps_restant = None

        if valeur == -1:
            if self.callback:
                self.callback(self._progression, message, tps_restant)
        elif diff >= 5 or valeur == 100:
            self._progression = int(valeur)
            tps_restant = (((self._chrono - self._debut) * 100) // self._progression) - (self._chrono - self._debut)
            if self.callback:
                self.callback(self._progression, message, tps_restant)

    def stop(self):
        self._stop.set()
