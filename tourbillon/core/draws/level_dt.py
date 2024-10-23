# -*- coding: UTF-8 -*-

"""Determinist algorithm to build matches according to teams level"""

import random

from .. import cst
from .utils import (BaseThreadTirage, nb_chapeaux_necessaires, tri_stat,
                    creer_liste, NV, NV_REDONDANCE, NV_DISPARITE,
                    tirage_texte, dernieres_equipes, cnp, len_cnp)
from ..exception import DrawResultError


MC_CACHE = {}
MR_CACHE = {}
MD_CACHE = {}
CNP_CACHE = []


def cle_matrice(manche):
    cle = "_".join([str(num) for num in sorted(manche)])
    return cle


def vider_caches():
    global MC_CACHE, MR_CACHE, MD_CACHE, CNP_CACHE
    MC_CACHE = {}
    MR_CACHE = {}
    MD_CACHE = {}
    CNP_CACHE = []


def creer_matrices(parametres, statistiques):
    """
    - Matrice de Coût: MC(manche) = ptsA+ptsB+... + kv * (nvA+nvB+...)

        Avec manche: [EquipeA, EquipeB, ...]
             pts   : nombre de points
             nv    : nombre de victoires (GAGNE + CHAPEAU)
             kv    : ponderation des victoires

    - Matrice de Rencontres: MR(manche) = nombre de fois ou la manche à déjà été disputée

        La valeur est < 1 si certaines équipes de la manche se sont déjà rencontrées
        mais pas toutes.

        valeur = nbr_fait_rencontres_2_à_2 / nbr_possible_rencontres_2_à_2

    - Matrice de Disparité: MD(manche) = max_victoires - min_victoires

        écart en nombre de victoires entre l'équipe la plus forte et la plus faible
        de la manche
    """
    global MC_CACHE, MR_CACHE, CNP_CACHE

    total = len_cnp(statistiques.keys(), parametres['equipes_par_manche'])
    parametres['rapport'](message="Création des matrices de coût, de rencontre et de disparité.")
    for manche in cnp(statistiques.keys(), parametres['equipes_par_manche']):
        CNP_CACHE.append(sorted(manche))

    compteur = 0
    for manche in CNP_CACHE:
        cle = cle_matrice(manche)

        # Completer la matrice de coût
        points = 0
        victoires = 0
        min_vic, max_vic = None, None
        for num in manche:
            parametres['arret_utilisateur']()
            points += statistiques[num][cst.STAT_POINTS]
            victoires += statistiques[num][cst.STAT_VICTOIRES]
            victoires += statistiques[num][cst.STAT_CHAPEAUX]
            if min_vic is None or statistiques[num][cst.STAT_VICTOIRES] + statistiques[num][cst.STAT_CHAPEAUX] < min_vic:
                min_vic = statistiques[num][cst.STAT_VICTOIRES] + statistiques[num][cst.STAT_CHAPEAUX]
            if max_vic is None or statistiques[num][cst.STAT_VICTOIRES] + statistiques[num][cst.STAT_CHAPEAUX] > max_vic:
                max_vic = statistiques[num][cst.STAT_VICTOIRES] + statistiques[num][cst.STAT_CHAPEAUX]
        MC_CACHE[cle] = points + parametres['ponderation_victoires'] * victoires

        # Completer la matrice de disparité
        MD_CACHE[cle] = max_vic - min_vic

        # Completer la matrice de rencontres
        rencontres = {}
        nb_vu = 0
        for vu in cnp(manche, 2):
            parametres['arret_utilisateur']()
            rencontres[cle_matrice(vu)] = statistiques[vu[1]][cst.STAT_ADVERSAIRES].count(vu[0])

        r = []
        for equipe in statistiques:
            if manche in statistiques[equipe][cst.STAT_MANCHES] and manche not in r:
                # La manche a déjà été disputée
                r.append(manche)
                for k in rencontres:
                    parametres['arret_utilisateur']()
                    rencontres[k] -= 1
                nb_vu += 1

        # Completer avec un un nombre < 1 pour les rencontres 2 à 2 effectuées
        # dans d'autres manches que celles redondantes
        nb_vu += 1 - (list(rencontres.values()).count(0) / len_cnp(manche, 2))
        MR_CACHE[cle] = nb_vu

        # Avancement du calcul (affichage jusque 99% pour éviter d'indiquer la fin de l'algorithme)
        compteur += 1
        s = "%-" + str(len(str(total))) + "s/%s manches évaluées"
        # 70% du temps attribué à la creation des matrices
        parametres['rapport'](((compteur * 70) / total) - 1, s % (compteur, total))

    parametres['rapport'](message="")


def comanche(parametres, manche, redondance=False, disparite=False):
    """
    Fonction de coût attribuant une performance à la manche:

            f(manche) = mc * mr * md

    Avec:
         mc  : Fonction de Coût minimum
                   mc = MC(manche)

         mr  : Fonction d'Augmentation
               Si la redondance n'est pas autorisée:
                   mr = 1 ou NV (Non valide)
               Sinon:
                   mr = 1 + taux_augmentation * MR(manche)

         md  : Fonction de Disparité
               Si le dépassement de la disparité max n'est pas autorisée:
                   md = 1 ou NV (Non valide)
               Sinon:
                   md = 1 + MD(manche) / ( MR(manche) + 1 )
    """
    cle = cle_matrice(manche)

    mc = MC_CACHE[cle]

    if not redondance:
        # Interdiction catégorique de rejouer ensemble
        if MR_CACHE[cle] < 1:
            mr = 1
        else:
            mr = NV_REDONDANCE
    else:
        # Pénalisaton si déjà joué ensembles
        mr = 1 + parametres['taux_augmentation'] * MR_CACHE[cle]

    if parametres['max_disparite'] >= MD_CACHE[cle]:
        # Disparité au plus égale à la disparité max autorisée
        md = 1
    else:
        if not disparite:
            # Interdiction catégorique de dépasser la disparité maxi
            md = NV_DISPARITE
        else:
            # Pénalisation si écart sur le nombre de victoires dépase la disparité max autorisée
            md = 1 + MD_CACHE[cle] / (1 + MR_CACHE[cle])

    if mr == NV and md == NV:
        return NV_REDONDANCE | NV_DISPARITE
    elif mr == NV:
        return mr
    elif md == NV:
        return md
    else:
        return mc * mr * md


def manche_possible(manche, equipes_disponibles, equipe=None):
    if equipe is None:
        equipe = manche[0]

    return len(manche) == len([True for e in manche if (e in equipes_disponibles and equipe in manche)])


def min_cout(parametres, equipes_disponibles, redondance=False, disparite=False, equipe=None):
    """
    Fonction renvoyant la manche qui possède la fonction de coût minimal.
    La manche avec un cout minimal comprend les équipes les plus faibles.

    'equipes' : retourne la manche qui a le cout minimal parmis les manche
                possibles avec 'equipes'.
    """
    minium = None
    valeur = None
    nv = None
    for manche in CNP_CACHE:
        parametres['arret_utilisateur']()
        if manche_possible(manche, equipes_disponibles, equipe):
            c = comanche(parametres, manche, redondance, disparite)
            if (valeur is None or valeur > c):
                if c != NV:
                    valeur = c
                    minium = manche
                else:
                    nv = c

    if minium is None:
        return nv
    else:
        return [e for e in minium]


def max_cout(parametres, equipes_disponibles, redondance=False, disparite=False, equipe=None):
    """
    Fonction renvoyant la manche qui possède la fonction de coût maximal
    La manche avec un cout maximal comprend les équipes les plus fortes.

    'equipes' : retourne la manche qui a le cout maximal parmis les manche
                possibles avec 'equipes'.
    """
    maximum = None
    valeur = None
    nv = None
    for manche in CNP_CACHE:
        parametres['arret_utilisateur']()
        if manche_possible(manche, equipes_disponibles, equipe):
            c = comanche(parametres, manche, redondance, disparite)
            if (valeur is None or valeur < c):
                if c != NV:
                    valeur = c
                    maximum = manche
                else:
                    nv = c

    if maximum is None:
        return nv
    else:
        return [e for e in maximum]


def premier(statistiques, equipes):
    """
    Fonction retournant la meilleur équipe de la liste
    """
    p = equipes[0]
    for equipe in equipes:
        if statistiques[equipe][cst.STAT_PLACE] < statistiques[p][cst.STAT_PLACE]:
            p = equipe

    return p


def nb_parties(statistiques, equipe, equipes_par_manche):
    adversaires = len(statistiques[equipe][cst.STAT_ADVERSAIRES])
    return adversaires // (equipes_par_manche - 1)


def select_chapeau(parametres, statistiques):
    equipes = dernieres_equipes(statistiques, parametres['chapeaux_parmis'])

    stat = {}
    for equipe in equipes:
        stat[equipe] = statistiques[equipe]
    d = tri_stat(stat, cst.STAT_CHAPEAUX)
    cle_tri = sorted(d.keys())

    if parametres['redondance'] == True:
        # Tirage aléatoire parmis les moins chapeau des n dernières équipes
        moins_chapeaux = d[cle_tri[0]]
        num = random.choice(moins_chapeaux)
        statistiques.pop(num)
    else:
        if cle_tri[0] == 0:
            # Certaines équipes n'ont jamais été chapeau
            non_chapeaux = d[cle_tri[0]]
            num = random.choice(non_chapeaux)
            statistiques.pop(num)
        elif parametres['depassement_chapeaux_parmis']:
            # effectuer une recherche sur plus de n équipes
            if parametres['chapeaux_parmis'] <= len(statistiques):
                parametres['arret_utilisateur']()
                parametres['chapeaux_parmis'] += 1
                num = select_chapeau(statistiques, parametres)
            else:
                #  ERREUR 101: Toutes les équipes on été chapeaux une fois.
                args = [cle_tri[0], cle_tri[-1]]
                raise DrawResultError(101, args)
        else:
            #  ERREUR 101: Toutes les équipes on été chapeaux une fois.
            args = [cle_tri[0], cle_tri[-1]]
            raise DrawResultError(101, args)

    return num


class ThreadTirage(BaseThreadTirage):
    NOM = __name__.rsplit('.', maxsplit=1)[-1]

    DESCRIPTION = "Niveau (Algorithme Déterministe)"

    DEFAUT = {'OPTIMUM': 0.0,
              'REDONDANCE': False,
              'PONDERATION_VICTOIRES': 12.0,
              'CALCUL_PONDERATION_AUTO': True,
              'TAUX_AUGMENTATION': 1.05,
              'MAX_DISPARITE': 2,
              'DEPASSEMENT_MAX_DISPARITE': False,
              'CHAPEAUX_PARMIS': 6,
              'DEPASSEMENT_CHAPEAUX_PARMIS': True,
              }

    def demarrer(self):
        nb_eq = len(self.statistiques)
        nb_chapeaux = nb_chapeaux_necessaires(nb_eq, self.equipes_par_manche)

        # Tirage des chapeaux:
        # --------------------

        for num in self.chapeaux:
            # Suppression des chapeaux pré-séléctionnées
            self.statistiques.pop(int(num))

        for _i in range(nb_chapeaux - len(self.chapeaux)):
            # Si le nombre de chapeaux fourni est insuffisant: en choisir d'autres
            self._arret_utilisateur()
            chap = select_chapeau(self.config, self.statistiques)
            self.chapeaux.append(chap)

        # Tirage des manches:
        # -------------------

        # Vider les caches
        vider_caches()

        # Paramètre de pondération des victoires
        if self.config['calcul_ponderation_auto'] == True:  # Calcul du coefficient de pondération des victoires
            ponderation = 0
            for equipe in self.statistiques:
                parties = nb_parties(self.statistiques, equipe, self.config['equipes_par_manche'])
                if parties == 0:
                    ponderation += 12.0
                else:
                    ponderation += self.statistiques[equipe][cst.STAT_POINTS] / parties

            self.config['ponderation_victoires'] = ponderation // len(self.statistiques)
            self.rapport(message="Coefficient de pondération des victoires: %s" % self.config['ponderation_victoires'])

        # Création de la matrice de cout
        creer_matrices(self.config, self.statistiques)

        # Lancer l'algorithme
        equipes_disponibles = list(self.statistiques.keys())
        tirage_temp = []

        while equipes_disponibles != []:
            self.config['arret_utilisateur']()
            # Fonction de coût stricte
            manche = min_cout(self.config, equipes_disponibles)

            if manche == NV:
                # Pas de solution pour les équipes restantes, on va rechercher
                p = premier(self.statistiques, equipes_disponibles)

                # Réinitialisation de la liste des équipes disponibles avant le début de
                # l'algorithme moins les équipes définitivement tirées
                equipes_disponibles = self.statistiques.keys()
                for num in creer_liste(self.tirage):
                    equipes_disponibles.remove(num)

                # Réinitialisation de la liste temporaire
                tirage_temp = []

                # Fonction de coût stricte sur la plus forte équipe
                manche = max_cout(self.config, equipes_disponibles, equipe=p)

                if manche == NV:
                    # La plus forte équipe n'a aucune possibilité de rencontre, on teste avec les paramètres utilisateur
                    # Fonction de coût peut être augmentée (dépend des paramètres utilisateur)
                    manche = max_cout(self.config, equipes_disponibles,
                                      self.config['redondance'], self.config['depassement_max_disparite'], equipe=p)

                    if manche == NV_REDONDANCE:
                        # ERREUR 154: La redondance n'est pas autorisée.
                        raise DrawResultError(154, "")
                    elif manche == NV_DISPARITE:
                        # ERREUR 155: La disparité est trop faible pour trouver une solution.
                        raise DrawResultError(155, "")
                    else:
                        # ERREUR 156: La disparité doit être augmentée ou la redondance autorisée.
                        raise DrawResultError(156, "")

                # Ces rencontres sont tirées une fois pour toute
                for num in manche:
                    equipes_disponibles.remove(num)
                self.tirage.append(manche)
            else:
                # Ajout à la liste temporaire qui sera à effacer si une erreur est trouvée
                # (équipe sans solution)
                for num in manche:
                    equipes_disponibles.remove(num)
                tirage_temp.append(manche)
                # 30% attribué au choix des équipes
                self.rapport(70 + (len(self.tirage) * self.equipes_par_manche + len(tirage_temp) * self.equipes_par_manche +
                                   len(self.chapeaux)) * 30 / len(self.statistiques))

        for manche in tirage_temp:
            # Passage des manches de la liste temporaire vers la liste définitive
            self.config['arret_utilisateur']()
            self.tirage.append(manche)

        self.rapport(message=tirage_texte(self.statistiques, self.tirage))
