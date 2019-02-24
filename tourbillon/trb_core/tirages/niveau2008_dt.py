#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Définitions des équipes."""

#--- Import --------------------------------------------------------------------

import random
from tourbillon.trb_core.tirages.utile import (BaseThreadTirage, nb_chapeaux_necessaires, tri_stat, Cnp,
                                               creer_manches, creer_liste, NV, NV_REDONDANCE, NV_DISPARITE)
from tourbillon.trb_core.exceptions import StopTirageError, SolutionError

#--- Variables globales --------------------------------------------------------

MC_CACHE = {}
MR_CACHE = {}
MD_CACHE = {}
CNP_CACHE = []

#--- Fonctions -----------------------------------------------------------------

def cle_matrice(manche):
    manche.sort()
    cle = "_".join([unicode(num) for num in manche])
    return cle

def vider_caches():
    global MC_CACHE, MR_CACHE, MD_CACHE, CNP_CACHE
    MC_CACHE = {}
    MR_CACHE = {}
    MD_CACHE = {}
    CNP_CACHE = []

def creer_matrices(parametres, statistiques):
    """
    - Matrice de Coût: MC(manche) = ptsA+ptsB+... + kv * (nvA+nvB+...) + aléat(0,1)
    
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

    parametres['rapport'](1, u"Création des matrices de coût, de rencontre et de disparité.")
    CNP_CACHE = Cnp(statistiques.keys(), parametres['equipes_par_manche'])
    map(list.sort, CNP_CACHE)

    compteur = 0
    for manche in CNP_CACHE:
        cle = cle_matrice(manche)

        # Completer la matrice de coût
        points = 0
        victoires = 0
        min_vic, max_vic = None, None
        for num in manche:
            parametres['arret_utilisateur']()
            points += statistiques[num]['points']
            victoires += statistiques[num]['victoires']
            victoires += statistiques[num]['chapeaux']
            if statistiques[num]['victoires'] + statistiques[num]['chapeaux'] < min_vic or min_vic is None:
                min_vic = statistiques[num]['victoires'] + statistiques[num]['chapeaux']
            if statistiques[num]['victoires'] + statistiques[num]['chapeaux'] > max_vic or max_vic is None:
                max_vic = statistiques[num]['victoires'] + statistiques[num]['chapeaux']
        MC_CACHE[cle] = points + parametres['ponderation_victoires'] * victoires + random.random()

        # Completer la matrice de disparité
        MD_CACHE[cle] = max_vic - min_vic

        # Completer la matrice de rencontres
        l = Cnp(manche, 2)
        rencontres = {}
        nb_vu = 0
        for vu in l:
            parametres['arret_utilisateur']()
            rencontres[cle_matrice(vu)] = statistiques[vu[1]]['adversaires'].count(vu[0])

        r = []
        for equipe in statistiques:
            if manche in statistiques[equipe]['manches'] and manche not in r:
                # La manche a déjà été disputée
                r.append(manche)
                for k in rencontres:
                    parametres['arret_utilisateur']()
                    rencontres[k] -= 1
                nb_vu += 1

        # Completer avec un un nombre < 1 pour les rencontres 2 à 2 effectuées
        # dans d'autres manches que celles redondantes
        nb_vu += 1 - (1.0 * rencontres.values().count(0) / len(l))
        MR_CACHE[cle] = nb_vu

        # Avancement du calcul (affichage jusque 99% pour éviter d'indiquer la fin de l'algorithme)
        compteur += 1
        s = u"%-" + str(len(str(len(CNP_CACHE)))) + "s/%s manches évaluées"
        parametres['rapport'](((compteur * 100) / len(CNP_CACHE)) - 1, s % (compteur, len(CNP_CACHE)))

    parametres['rapport'](0, "")

def fonction_cout(parametres, manche, redondance = False, disparite = False):
    """
    Fonction de coût attribuant une performance à la manche. Elle se compose
    de trois termes:

    - Fonction de Coût minimum :

            terme1 = MC(manche)

    - Fonction d'Augmentation  :
     
        Si la redondance n'est pas autorisée:
            terme2 = 1 ou NV (Non valide)
        Sinon:
            terme2 = 1 + taux_augmentation * MR(manche)

    - Fonction de Disparité    :

        Si le dépassement de la disparité max n'est pas autorisée:
            terme3 = 1 ou NV (Non valide)
        Sinon:
            terme3 = 1 + MD(manche) / ( MR(manche) + 1 )
    """
    cle = cle_matrice(manche)

    terme1 = MC_CACHE[cle]

    if redondance == False:
        # Interdiction catégorique de rejouer ensemble
        if MR_CACHE[cle] < 1:
            terme2 = 1
        else:
            terme2 = NV_REDONDANCE
    else:
        # Pénalisaton si déjà joué ensembles
        terme2 = 1 + parametres['taux_augmentation'] * MR_CACHE[cle]

    if parametres['max_disparite'] >= MD_CACHE[cle]:
        # Disparité au plus égale à la disparité max autorisée
        terme3 = 1
    else:
        if disparite == False:
            # Interdiction catégorique de dépasser la disparité maxi
            terme3 = NV_DISPARITE
        else:
            # Pénalisation si écart sur le nombre de victoires dépase la disparité max autorisée
            terme3 = 1 + MD_CACHE[cle] / (1.0 + MR_CACHE[cle])

    if terme2 != NV and terme3 != NV:
        return terme1 * terme2 * terme3
    elif terme2 == NV and terme3 == NV:
        return NV_REDONDANCE | NV_DISPARITE
    elif terme2 == NV and terme3 != NV:
        return terme2
    elif terme2 != NV and terme3 == NV:
        return terme3

def manche_possible(manche, equipes_disponibles, equipe = None):
    if equipe is None:
        equipe = manche[0]

    return len(manche) == len([True for e in manche if (e in equipes_disponibles and equipe in manche)])

def min_cout(parametres, equipes_disponibles, redondance = False, disparite = False, equipe = None):
    """
    Fonction renvoyant la manche qui possède la fonction de coût minimale
    
    'equipes' : retourne la manche qui a le cout minimal parmis les manche
                possibles avec 'equipes'.
    """
    min = None
    valeur = None
    nv = None
    for manche in CNP_CACHE:
        parametres['arret_utilisateur']()
        if manche_possible(manche, equipes_disponibles, equipe):
            c = fonction_cout(parametres, manche, redondance, disparite)
            if (valeur is None or valeur > c):
                if c != NV:
                    valeur = c
                    min = manche
                else:
                    nv = c

    if min is None:
        return nv
    else:
        return [e for e in min]

def max_cout(parametres, equipes_disponibles, redondance = False, disparite = False, equipe = None):
    """
    Fonction renvoyant la manche qui possède la fonction de coût minimale
    
    'equipes' : retourne la manche qui a le cout minimal parmis les manche
                possibles avec 'equipes'.
    """
    max = None
    valeur = None
    nv = None
    for manche in CNP_CACHE:
        parametres['arret_utilisateur']()
        if manche_possible(manche, equipes_disponibles, equipe):
            c = fonction_cout(parametres, manche, redondance, disparite)
            if (valeur is None or valeur < c):
                if c != NV:
                    valeur = c
                    max = manche
                else:
                    nv = c

    if max is None:
        return nv
    else:
        return [e for e in max]

def premier(statistiques, equipes):
    """
    Fonction retournant la meilleur équipe de la liste
    """
    p = equipes[0]
    for equipe in equipes:
        if statistiques[equipe]['place'] < statistiques[p]['place']:
            p = equipe

    return p

def dernieres_equipes(statistiques, n = 1):
    """
    Retourne la liste des n dernières équipes.
    """
    r = []
    d = tri_stat(statistiques, 'place')
    places = d.keys()
    places.sort()
    for p in places:
        r += d[p]

    return r[-6:]

def nb_parties(statistiques, equipe, equipes_par_manche):
    adversaires = len(statistiques[equipe]['adversaires'])
    return adversaires / (equipes_par_manche - 1)

def select_chapeau(parametres, statistiques):
    equipes = dernieres_equipes(statistiques, parametres['chapeaux_parmis'])

    stat = {}
    for equipe in equipes:
        stat[equipe] = statistiques[equipe]
    d = tri_stat(stat, 'chapeaux')
    cle_tri = d.keys()
    cle_tri.sort()

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
                raise SolutionError(101, args)
        else:
            #  ERREUR 101: Toutes les équipes on été chapeaux une fois.
            args = [cle_tri[0], cle_tri[-1]]
            raise SolutionError(101, args)

    return num

def message(statistiques, manche):
    cle = cle_matrice(manche)
    pts = [statistiques[equipe]['points'] for equipe in manche]
    dp = max(pts) - min(pts)
    return "%-15s: diff points = %-5s, redondance = %-5s, disparité = %-5s" % (manche, dp, MR_CACHE[cle], MD_CACHE[cle])

class ThreadTirage(BaseThreadTirage):
    def __init__(self, equipes_par_manche, statistiques, chapeaux = [], rapport = None):
        BaseThreadTirage.__init__(self, equipes_par_manche, statistiques, chapeaux, rapport)
        self.categorie = u"niveau2008_dt"
        self._algo_conf = {}
        self.configurer()

    def configurer(self, chapeaux_parmis = 6, depassement_chapeaux_parmis = True, ponderation_victoires = 12.0, calcul_ponderation_auto = False,
                   taux_augmentation = 1.05, max_disparite = 2, depassement_max_disparite = False, optimum = -1, redondance = False):
        self._algo_conf['chapeaux_parmis'] = chapeaux_parmis
        self._algo_conf['depassement_chapeaux_parmis'] = depassement_chapeaux_parmis
        self._algo_conf['ponderation_victoires'] = ponderation_victoires
        self._algo_conf['taux_augmentation'] = taux_augmentation
        self._algo_conf['max_disparite'] = max_disparite
        self._algo_conf['depassement_max_disparite'] = depassement_max_disparite
        self._algo_conf['optimum'] = optimum
        self._algo_conf['redondance'] = redondance
        self._algo_conf['calcul_ponderation_auto'] = calcul_ponderation_auto
        self._algo_conf['statistiques'] = self.statistiques
        self._algo_conf['equipes_par_manche'] = self.equipes_par_manche
        self._algo_conf['arret_utilisateur'] = self._arret_utilisateur
        self._algo_conf['rapport'] = self.rapport

    def demarrer(self):
        nb_eq = len(self.statistiques)
        nb_chapeaux = nb_chapeaux_necessaires(nb_eq, self.equipes_par_manche)

        # Tirage des chapeaux:
        #---------------------

        if len(self.chapeaux) >= self.equipes_par_manche:
            # ERREUR 100: Le nombre de chapeaux ne peu pas être égale au nombre d'équipes par manche
            args = [len(self.chapeaux), self.equipes_par_manche]
            raise SolutionError(100, args)

        if nb_chapeaux - len(self.chapeaux) < 0:
            # ERREUR 102: Nombre de chapeaux fourni incorrecte
            args = (nb_chapeaux_necessaires(nb_eq, self.equipes_par_manche) - len(self.chapeaux),)
            raise SolutionError(102, args)

        for num in self.chapeaux:
            # Suppression des chapeaux pré-séléctionnées
            self.statistiques.pop(int(num))

        for i in range(nb_chapeaux - len(self.chapeaux)):
            # Si le nombre de chapeaux fourni est insuffisant: en choisir d'autres
            self._arret_utilisateur()
            chap = select_chapeau(self._algo_conf, self.statistiques)
            self.chapeaux.append(chap)

        # Tirage des manches:
        #--------------------

        # Vider les caches
        vider_caches()

        # Paramètre de pondération des victoires
        if self._algo_conf['calcul_ponderation_auto'] == True:       # Calcul du coefficient de pondération des victoires
            ponderation = 0
            for equipe in self.statistiques:
                parties = nb_parties(self.statistiques, equipe, self._algo_conf['equipes_par_manche'])
                if parties == 0:
                    ponderation += 12.0
                else:
                    ponderation += (self.statistiques[equipe]['points'] * 1.0) / parties

            self._algo_conf['ponderation_victoires'] = ponderation / len(self.statistiques)
            self.rapport(0, u"Coefficient de pondération des victoires: %s" % self._algo_conf['ponderation_victoires'])

        # Création de la matrice de cout
        creer_matrices(self._algo_conf, self.statistiques)

        # Lancer l'algorithme
        equipes_disponibles = self.statistiques.keys()
        tirage_temp = []

        while equipes_disponibles != []:
            self._algo_conf['arret_utilisateur']()
            # Fonction de coût stricte
            manche = min_cout(self._algo_conf, equipes_disponibles)

            if manche == NV:
                # Pas de solution pour les équipes restantes, on va rechercher 
                p = premier(self.statistiques, equipes_disponibles)

                # Réinitialisation de la liste des équipes disponibles avant le début de
                # l'algorithme moins les équipes définitivement tirées
                equipes_disponibles = self.statistiques.keys()
                map(equipes_disponibles.remove, creer_liste(self.tirage))

                # Réinitialisation de la liste temporaire
                tirage_temp = []

                # Fonction de coût stricte sur la plus forte équipe
                manche = max_cout(self._algo_conf, equipes_disponibles, equipe = p)

                if manche == NV:
                    # La plus forte équipe n'a aucune possibilité de rencontre, on teste avec les paramètres utilisateur
                    # Fonction de coût peut être augmentée (dépend des paramètres utilisateur)
                    manche = max_cout(self._algo_conf, equipes_disponibles, self._algo_conf['redondance'], self._algo_conf['depassement_max_disparite'], equipe = p)

                    if manche == NV_REDONDANCE:
                        # ERREUR 154: La redondance n'est pas autorisée.
                        raise SolutionError(154, "")
                    elif manche == NV_DISPARITE:
                        # ERREUR 155: La disparité est trop faible pour trouver une solution.
                        raise SolutionError(155, "")
                    else:
                        # ERREUR 156: La disparité doit être augmentée ou la redondance autorisée.
                        raise SolutionError(156, "")

                # Ces rencontres sont tirées une fois pour toute
                map(equipes_disponibles.remove, manche)
                self.tirage.append(manche)
                self.rapport(len(self.tirage) * 100 / (len(self.statistiques) / self.equipes_par_manche), message(self.statistiques, manche))
            else:
                # Ajout à la liste temporaire qui sera à effacer si une erreur est trouvée
                # (équipe sans solution)
                map(equipes_disponibles.remove, manche)
                tirage_temp.append(manche)

        for manche in tirage_temp:
            # Passage des manches de la liste temporaire vers la liste définitive
            self._algo_conf['arret_utilisateur']()
            self.tirage.append(manche)
            self.rapport(len(self.tirage) * 100 / (len(self.statistiques) / self.equipes_par_manche), message(self.statistiques, manche))
