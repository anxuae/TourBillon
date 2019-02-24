#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Définitions des équipes."""

#--- Import --------------------------------------------------------------------
import random
from tourbillon.trb_core.tirages.utile import (BaseThreadTirage, nb_chapeaux_necessaires, tri_stat, Cnp,
                                               Individu, Environement, genese, creer_manches)
from tourbillon.trb_core.exceptions import StopTirageError, SolutionError

#--- Fonctions -----------------------------------------------------------------

def select_chapeau(statistiques, redondance):
    d = tri_stat(statistiques, 'chapeaux')
    cle_tri = d.keys()
    cle_tri.sort()
    if redondance == True:
        moins_chapeaux = d[cle_tri[0]]
        num = random.choice(moins_chapeaux)
        statistiques.pop(num)
        return num
    else:
        if cle_tri[0] == 0:
            non_chapeaux = d[cle_tri[0]]
            num = random.choice(non_chapeaux)
            statistiques.pop(num)
            return num
        else:
            #  ERREUR 101: Toutes les équipes on été chapeaux une fois.
            args = [cle_tri[0], cle_tri[-1]]
            raise SolutionError(101, args)

#--- Classes -------------------------------------------------------------------

class Tirage(Individu):

    def evaluer(self, parametres, optimum = None):
        """
        Calcul du nombre de fois ou deux équipes qui se sont déjà rencontrées
        vont rejouer une manche.
        
        Manche avec aucune équipe qui se sont déjà rencontrées = 0
        Manche avec certaines équipes qui se sont déjà rencontrées = nb / ( Cnp(Manche) * nb_manches )
        Manche redondante = 1
        
        Tirage = somme des Manches
        Tirage avec plusieurs fois la même équipe = 1e36
        """
        # Vérifier si l'utilisateur a demandé l'arrêt
        parametres['arret_utilisateur']()

        # Nombre de manches
        nb_manches = len(self.alleles) / parametres['equipes_par_manche']

        nb_vu = 0
        for manche in creer_manches(self.chromosome, parametres['equipes_par_manche']):
            l = Cnp(manche, 2)
            c = 0
            for vu in l:
                if parametres['statistiques'][vu[1]]['adversaires'].count(vu[0]) > 0:
                    c += 1

            if c == len(l):
                # Toutes les équipes se sont déjà rencontrées
                nb_vu += 1
            else:
                nb_vu += c * 1.0 / (len(l) * nb_manches)

        for eq in self.alleles:
            if self.chromosome.count(eq) > 1:
                nb_vu = 1e36
                break

        self.score = nb_vu

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
        self.categorie = u"aleatoire_ag"
        self._env = None
        self._algo_conf = {}
        self.configurer()

    def configurer(self, taille_population_ini = 40, taille_population = 50, max_generations = 1000, taux_croiser = 0.9, taux_muter = 0.01,
                   optimum = -1, redondance = False):
        self._algo_conf['taille_population_ini'] = taille_population_ini
        self._algo_conf['taille_population'] = taille_population
        self._algo_conf['max_generations'] = max_generations
        self._algo_conf['taux_croiser'] = taux_croiser
        self._algo_conf['taux_muter'] = taux_muter
        self._algo_conf['optimum'] = optimum
        self._algo_conf['redondance'] = redondance
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
            chap = select_chapeau(self.statistiques, self._algo_conf['redondance'])
            self.chapeaux.append(chap)

        # Tirage des manches:
        #--------------------

        # Créer l'environement
        Tirage.alleles = self.statistiques.keys()
        self._env = Environement(genese(Tirage, self._algo_conf['taille_population_ini']), **self._algo_conf)

        # Lancer l'algorithme
        self._env.run()

        self.tirage = creer_manches(self._env.elite.chromosome, self.equipes_par_manche)

        # Verification de la pertinence de la solution
        if self._env.elite.score >= 1e36:
            # ERREUR 150: Une même équipe apparaît plusieurs fois dans le tirage.
            args = []
            for equipe in self.statistiques.keys():
                nb = self._env.elite.chromosome.count(equipe)
                if nb != 1:
                    args.append((equipe, nb))
            raise SolutionError(150, args)

        elif self._algo_conf['redondance'] == False and self._env.elite.score >= 1:
            # ERREUR 151: Au moins une manche qui a déjà été disputée se trouve dans le tirage et
            #             la redondance n'est pas autorisée.
            args = []
            for manche in creer_manches(self._env.elite.chromosome, self.equipes_par_manche):
                nb_vu = 0
                l = Cnp(manche, 2)
                for vu in l:
                    nb_vu += self.statistiques[vu[1]]['adversaires'].count(vu[0])
                if nb_vu >= len(l):
                    args.append(manche)
            raise SolutionError(151, args)
