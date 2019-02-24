#!/usr/bin/env python
# -*- coding: UTF-8 -*-

u"""Algorithme génétique pseudo aléatoire (choix de la redondance possible)."""

#--- Import -------------------------------------------------------------------

import random
from tourbillon.trb_core.tirages.utile import (BaseThreadTirage, nb_chapeaux_necessaires,
                                               tri_stat, Cnp, creer_manches, tirage_texte)
from tourbillon.trb_core.tirages.niveau_ag import Tirage as NvTirage, Environement, genese
from tourbillon.trb_core.exceptions import SolutionError

#--- Variables globales -------------------------------------------------------

NOM = u"Aléatoire (Algorithme Génétique)"

DEFAUT = {'TAILLE_POPULATION_INI': 40,
          'TAILLE_POPULATION'    : 50,
          'MAX_GENERATIONS'      : 100,
          'TAUX_CROISEMENT'      : 0.9,
          'TAUX_MUTATION'        : 0.01,
          'OPTIMUM'              : 0.0,
          'REDONDANCE'           : False
          }

#--- Fonctions ----------------------------------------------------------------


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


def comanche(parametres, statistiques, manche):
    """
    Fonction de coût attribuant une performance à la manche:

            f(manche) = nb_vu / len( Cnp(Manche) )

    Avec:
         nb_vu       : nombre de couples qui se sont déjà vu
         Cnp(Manche) : ensemble des couples (de 2) pouvant s'être rencontrés
    """
    manches2a2 = Cnp(manche, 2)
    vu = 0
    for manche in manches2a2:
        if statistiques[manche[1]]['adversaires'].count(manche[0]) > 0:
            vu += 1

    if vu == len(manches2a2):
        return 1
    else:
        return vu * 1.0 / len(manches2a2)


class Tirage(NvTirage):

    def evaluer(self, parametres, optimum=None):
        """
        Evalue le score du tirage. L'algorithme "aléatoire génétique" est conçu
        pour attribuer le meilleur score à un tirage si aucune des manches
        n'a déjà eu lieu.

        Le score est la somme des "cout" de chaque manche (pour le calcul
        du cout d'une manche, voir la description de "comanche").

        Un tirage contenant plusieurs fois la même équipe vaut 1e36
        """
        nb_vu = 0
        for manche in creer_manches(self.chromosome, parametres['equipes_par_manche']):
            # Vérifier si l'utilisateur a demandé l'arrêt
            parametres['arret_utilisateur']()

            nb_vu += comanche(parametres, parametres['statistiques'], manche)

        for eq in self.alleles:
            if self.chromosome.count(eq) > 1:
                nb_vu = 1e36
                break

        self.score = nb_vu


class ThreadTirage(BaseThreadTirage):
    def __init__(self, *args, **kargs):
        BaseThreadTirage.__init__(self, *args, **kargs)
        self.categorie = u"aleatoire_ag"
        self._env = None

        # Parametres par défaut de l'algorithme
        self.configurer(**dict([(cle.lower(), valeur) for cle, valeur in DEFAUT.iteritems()]))

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
            chap = select_chapeau(self.statistiques, self.config['redondance'])
            self.chapeaux.append(chap)

        # Tirage des manches:
        #--------------------

        # Créer l'environement
        Tirage.alleles = self.statistiques.keys()
        self._env = Environement(genese(Tirage, self.config['taille_population_ini']), **self.config)

        # Lancer l'algorithme
        self._env.run()

        self.tirage = creer_manches(self._env.elite.chromosome, self.equipes_par_manche)
        self.rapport(message=tirage_texte(self.statistiques, self.tirage))

        # Verification de la pertinence de la solution
        if self._env.elite.score >= 1e36:
            # ERREUR 150: Une même équipe apparaît plusieurs fois dans le tirage.
            args = []
            for equipe in self.statistiques.keys():
                nb = self._env.elite.chromosome.count(equipe)
                if nb != 1:
                    args.append((equipe, nb))
            raise SolutionError(150, args)

        elif self.config['redondance'] == False and self._env.elite.score >= 1:
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
