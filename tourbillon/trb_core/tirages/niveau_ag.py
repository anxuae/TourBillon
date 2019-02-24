#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Définitions des équipes."""

#--- Import --------------------------------------------------------------------

import random
import copy
from tourbillon.trb_core.tirages.utile import (BaseThreadTirage, nb_chapeaux_necessaires, tri_stat, Cnp,
                                               Individu, Environement, genese, creer_manches, creer_liste,
                                               NV, NV_REDONDANCE, NV_DISPARITE)
from tourbillon.trb_core.exceptions import StopTirageError, SolutionError

#--- Variables globales --------------------------------------------------------



#--- Fonctions -----------------------------------------------------------------

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

def cle_manche(manche):
    manche.sort()
    cle = "_".join([unicode(num) for num in manche])
    return cle

def nb_parties(statistiques, equipe, equipes_par_manche):
    adversaires = len(statistiques[equipe]['adversaires'])
    return adversaires / (equipes_par_manche - 1)

def fonction_cout(parametres, statistiques, manche):
    """
    Fonction de coût attribuant une performance à la manche:
    
            f(manche) = dp + kv * dv + kv * nrc

            Avec:
                 dp  : max_pts - min_pts  nombre de points
                 dv  : max_nv - min_nv    nombre de victoires (GAGNE + CHAPEAU)
                 kv  : ponderation des victoires
                 nrc : nombre de redondance de la manche
                       (La valeur est < 1 si certaines équipes de la manche se sont déjà rencontrées
                        mais pas toutes.)
        
    (la disparité est incluse dans le terme "kv * (max_nv - min_nv)")
    """
    manche.sort()
    pts = []
    nv = []
    for equipe in manche:
        parametres['arret_utilisateur']()
        pts.append(statistiques[equipe]['points'])
        nv.append(statistiques[equipe]['victoires'] + statistiques[equipe]['chapeaux'])

    dp = max(pts) - min(pts)
    dv = max(nv) - min(nv)
    valeur = dp + parametres['ponderation_victoires'] * dv

    # Terme des rencontres
    l = Cnp(manche, 2)
    rencontres = {}
    nrc = 0
    for vu in l:
        parametres['arret_utilisateur']()
        rencontres[cle_manche(vu)] = statistiques[vu[1]]['adversaires'].count(vu[0])

    r = []
    for equipe in statistiques:
        if manche in statistiques[equipe]['manches'] and manche not in r:
            # La manche a déjà été disputée
            r.append(manche)
            for k in rencontres:
                parametres['arret_utilisateur']()
                rencontres[k] -= 1
            nrc += 1

    # Completer avec un un nombre < 1 pour les rencontres 2 à 2 effectuées
    # dans d'autres manches que celles redondantes
    nrc += 1 - (1.0 * rencontres.values().count(0) / len(l))

    valeur += parametres['ponderation_victoires'] * nrc

    if parametres['redondance'] == False:
        # Interdiction catégorique de rejouer ensemble
        if nrc >= 1:
            valeur = NV_REDONDANCE

    if parametres['max_disparite'] < dv:
        if parametres['depassement_max_disparite'] == False:
            # Interdiction catégorique de dépasser la disparité maxi
            if valeur == NV:
                valeur = valeur | NV_DISPARITE
            else:
                valeur = NV_DISPARITE

    return valeur, [dp, nrc, dv]

#--- Classes -------------------------------------------------------------------

class Tirage(Individu):
    def __init__(self, *args, **kwrds):
        Individu.__init__(self, *args, **kwrds)
        self.nv = None
        self.aug = 0

    def evaluer(self, parametres, optimum = None):
        """
        """
        # Nombre de manches
        nb_manches = len(self.alleles) / parametres['equipes_par_manche']

        moindes_carre = 0

        for manche in creer_manches(self.chromosome, parametres['equipes_par_manche']):
            # Vérifier si l'utilisateur a demandé l'arrêt
            parametres['arret_utilisateur']()
            valeur, _ = fonction_cout(parametres, parametres['statistiques'], manche)
            if valeur == NV:
                self.nv = self.nv | valeur
                moindes_carre = 1e36 + self.aug
                self.aug += 1
                break
            else:
                moindes_carre += valeur

        for eq in self.alleles:
            if self.chromosome.count(eq) > 1:
                self.nv = self.nv | NV_REDONDANCE
                moindes_carre = 1e36 + self.aug
                self.aug += 1
                break

        self.score = moindes_carre

    def reparer(self, parent1, parent2):
        manque = []
        for a in self.alleles:
            if a not in self.chromosome:
                manque.append(a)
        i = 0
        while i < len(self.alleles):
            if self.chromosome.count(self.chromosome[i]) > 1:
                self.chromosome[i] = manque[0]
                manque.pop(0)
            else:
                i += 1

class ThreadTirage(BaseThreadTirage):
    def __init__(self, equipes_par_manche, statistiques, chapeaux = [], rapport = None):
        BaseThreadTirage.__init__(self, equipes_par_manche, statistiques, chapeaux, rapport)
        self.categorie = u"niveau_ag"
        self._env = None
        self._algo_conf = {}
        self.configurer()

    def configurer(self, taille_population_ini = 40, taille_population = 50, max_generations = 1000, taux_croiser = 0.9, taux_muter = 0.01,
                   optimum = -1, redondance = False, max_disparite = 2, depassement_max_disparite = False, taux_augmentation = 1.05,
                   ponderation_victoires = 12.0, calcul_ponderation_auto = False, chapeaux_parmis = 6, depassement_chapeaux_parmis = True):
        self._algo_conf['taille_population_ini'] = taille_population_ini
        self._algo_conf['taille_population'] = taille_population
        self._algo_conf['max_generations'] = max_generations
        self._algo_conf['taux_croiser'] = taux_croiser
        self._algo_conf['taux_muter'] = taux_muter
        self._algo_conf['optimum'] = optimum
        self._algo_conf['chapeaux_parmis'] = chapeaux_parmis
        self._algo_conf['depassement_chapeaux_parmis'] = depassement_chapeaux_parmis
        self._algo_conf['ponderation_victoires'] = ponderation_victoires
        self._algo_conf['taux_augmentation'] = taux_augmentation
        self._algo_conf['max_disparite'] = max_disparite
        self._algo_conf['depassement_max_disparite'] = depassement_max_disparite
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

        # Créer l'environement
        Tirage.alleles = self.statistiques.keys()
        self._env = Environement(genese(Tirage, self._algo_conf['taille_population_ini']), **self._algo_conf)

        # Lancer l'algorithme
        self._env.run()

        self.tirage = creer_manches(self._env.elite.chromosome, self.equipes_par_manche)

        for manche in self.tirage:
            _, l = fonction_cout(self._algo_conf, self.statistiques, manche)

            self.rapport(99, "%-15s: diff points = %-5s, redondance = %-5s, disparité = %-5s" % (manche, l[0], l[1], l[2]))

        # Verification de la pertinence de la solution

        # ERREUR 150: Une même équipe apparaît plusieurs fois dans le tirage.
        args = []
        for equipe in self.statistiques.keys():
            nb = self._env.elite.chromosome.count(equipe)
            if nb != 1:
                args.append((equipe, nb))
        if len(args) != 0:
            raise SolutionError(150, args)

        elif self._env.elite.score >= 1e36:
            if self._env.elite.nv == NV_REDONDANCE:
                # ERREUR 154: La redondance n'est pas autorisée.
                raise SolutionError(154, "")
            elif self._env.elite.nv == NV_DISPARITE:
                # ERREUR 155: La disparité est trop faible pour trouver une solution.
                raise SolutionError(155, "")
            else:
                # ERREUR 156: La disparité doit être augmentée ou la redondance autorisée.
                raise SolutionError(156, "")
