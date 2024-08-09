# -*- coding: UTF-8 -*-

"""Genetic algorithm to build matches according to teams level"""

import random

from tourbillon.core.cst import MINIMISE
from tourbillon.core.draws.utils import (BaseThreadTirage, nb_chapeaux_necessaires, tri_stat,
                                         creer_manches, NV, NV_REDONDANCE, NV_DISPARITE,
                                         tirage_texte, dernieres_equipes, cnp, len_cnp)
from tourbillon.core.exception import DrawResultError


def genese(individu_type, taille=20):
    """
    Créer la population initiale.
    """
    population = []
    i = 0
    while i < taille:
        genes = list(individu_type.alleles)
        random.shuffle(genes)
        individu = individu_type(genes)
        population.append(individu)
        i += 1

    return population


class Individu:
    alleles = []  # Version d'un gène
    optimization = MINIMISE

    def __init__(self, chromosome=None):
        self.chromosome = chromosome
        self.score = None  # set during evaluation

    def __str__(self):
        return '<%s chromosome= %s score= %s>' % \
               (self.__class__.__name__, self.chromosome, self.score)

    def __cmp__(self, other):
        if self.optimization == MINIMISE:
            return cmp(self.score, other.score)
        else:  # MAXIMISE
            return cmp(other.score, self.score)

    # Exemple de mutation
    def _remplacer(self, gene):
        """
        Choisir aléatoirement un allèle pour remplacer ce gène.
        """
        self.chromosome[self.chromosome.index(gene)] = random.choice(self.alleles)

    # Exemples de croisements
    def _deux_points(self, other):
        "Créer des fils via un croisement en 2 points entre individus parents."
        gauche, droite = self._choisir_pivots()

        def mate(p0, p1):
            chromosome = p0.chromosome[:]
            chromosome[gauche:droite] = p1.chromosome[gauche:droite]
            child = p0.__class__(chromosome)
            child.reparer(p0, p1)
            return child
        return mate(self, other), mate(other, self)

    def _choisir_pivots(self):
        """
        Selectionner deux pivots dans le chromosome (deux indices choisis
        aléatoirement parmis les gènes du chromosome)
        """
        gauche = random.randrange(1, len(self.chromosome) - 2)
        droite = random.randrange(gauche, len(self.chromosome) - 1)
        return gauche, droite

    def reparer(self, parent1, parent2):
        """"
        Surchargez cette methode si nécessaire pour réparer les chromosomes
        ayant des genes dupliqués après croisement.
        """
        pass

    def copier(self):
        """
        Copier l'individu.
        """
        twin = self.__class__(self.chromosome[:])
        twin.score = self.score
        return twin

    def evaluer(self, parametres, optimum=None):
        """
        Cette methode DOIT être surchargée pour évaluer la finesse du
        score d'un individu.
        """
        pass

    def croiser(self, other):
        """"
        Surchargez cette methode pour utiliser un algorithme de croisement
        personnalisé.
        """
        return self._deux_points(other)

    def muter(self, gene):
        """"
        Surchargez cette methode pour utiliser un algorithme de mutation
        personnalisé.
        """
        self._remplacer(gene)


class Environement:

    def __init__(self, population, taille_population=100, max_generations=1000,
                 taux_croiser=0.90, taux_muter=0.01, optimum=None, rapport=None, **kwrds):

        # Taille maximale de la population
        self.taille = taille_population
        # Optimum à atteindre
        self.optimum = optimum
        # Autres paramètres fournis à la fonction d'évaluation
        self.eval_parametres = kwrds
        # Polulation
        self.population = population
        for individu in self.population:
            individu.evaluer(self.eval_parametres, self.optimum)
        # Pourcentage de croisements
        self.taux_croiser = taux_croiser
        # Pourcentage de mutation
        self.taux_muter = taux_muter
        # Nombre maximum de génération avant arrêt
        self.max_generations = max_generations
        # Indice de la génération actuelle
        self.generation = 0
        # Execute le fonction à chaque nouvelle génération
        self.rapport = rapport
        self.message = "Génération %-" + str(len(str(max_generations))) + "s - score : %-8.5g"

    def run(self):
        while not self._but():
            self.pas()
            if callable(self.rapport):
                evolution = self.generation * 100 // self.max_generations
                self.rapport(evolution, self.message % (self.generation, self.elite.score))
        if callable(self.rapport):
            self.rapport(99, "")

    def _but(self):
        return self.generation > self.max_generations or \
            self.elite.score == self.optimum

    def _croiser(self, individu1, individu2):
        if random.random() < self.taux_croiser:
            enfants = individu1.croiser(individu2)
        else:
            enfants = [individu1.copier()]
        return enfants

    def _muter(self, individu):
        for gene in individu.chromosome:
            if random.random() < self.taux_muter:
                individu.muter(gene)

    def _tournoi(self, taille=6, taux_elite=0.80):
        """
        Selection par tournoi. 'taille' individus sont choisis aléatoirement parmi
        la population. Le pourcentage donné par 'taux_elite' indique la probabilité
        de choisir l'élite parmi l'échantillon.
        """
        competitors = [random.choice(self.population) for _i in range(taille)]
        competitors.sort()
        if random.random() < taux_elite:
            return competitors[0]
        else:
            return random.choice(competitors[1:])

    def select(self):
        return self._tournoi()

    def pas(self):
        self.population.sort()
        next_population = [self.elite.copier()]

        while len(next_population) < self.taille:
            parent1 = self.select()
            parent2 = self.select()

            enfants = self._croiser(parent1, parent2)

            for individu in enfants:
                self._muter(individu)
                individu.evaluer(self.eval_parametres, self.optimum)
                next_population.append(individu)

        self.population = next_population[:self.taille]
        self.generation += 1

    def elite():
        """
        Retourne l'individu ayant le meilleur score dans la population.
        """

        def fget(self):
            return self.population[0]
        return locals()

    elite = property(**elite())


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
                raise DrawResultError(101, args)
        else:
            #  ERREUR 101: Toutes les équipes on été chapeaux une fois.
            args = [cle_tri[0], cle_tri[-1]]
            raise DrawResultError(101, args)

    return num


def cle_manche(manche):
    cle = "_".join([str(num) for num in sorted(manche)])
    return cle


def nb_parties(statistiques, equipe, equipes_par_manche):
    adversaires = len(statistiques[equipe]['adversaires'])
    return adversaires // (equipes_par_manche - 1)


def comanche(parametres, statistiques, manche):
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
    rencontres = {}
    nrc = 0
    for vu in cnp(manche, 2):
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
    nrc += 1 - (rencontres.values().count(0) / len_cnp(manche, 2))

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


class Tirage(Individu):

    def __init__(self, *args, **kwrds):
        Individu.__init__(self, *args, **kwrds)
        self.nv = None
        self.aug = 0

    def evaluer(self, parametres, optimum=None):
        """
        Evalue le score du tirage. L'algorithme "niveau génétique" est conçu
        pour attribuer le meilleur score à un tirage si
           * aucune des manches n'a eu lieu
           * les équipes d'une manche sont de même niveau (ou force)

        Le score est la somme des "cout" de chaque manche (pour le calcul
        du cout d'une manche, voir la description de "comanche").

        Un tirage contenant plusieurs fois la même équipe ou dont les manches
        ne respectent pas les paramètres de niveau definit vaut 1e36
        """
        moindes_carre = 0

        for manche in creer_manches(self.chromosome, parametres['equipes_par_manche']):
            # Vérifier si l'utilisateur a demandé l'arrêt
            parametres['arret_utilisateur']()

            valeur, _ = comanche(parametres, parametres['statistiques'], manche)
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

    def muter(self, gene):
        """
        Reimplementation de la mutation pour eviter de dupliquer
        les equipes. La muation opère une permutation de deux équipes.
        """
        geneopp = None
        while geneopp is None or geneopp == gene:
            geneopp = random.choice(self.alleles)

        ind = self.chromosome.index(gene)
        indopp = self.chromosome.index(geneopp)
        self.chromosome[ind] = geneopp
        self.chromosome[indopp] = gene

    def reparer(self, parent1, parent2):
        """
        Reimplementation de la reparation. Supprime les doublons dans
        le chromosome et les remplace par les gènes manquant.
        """
        manque = []
        for a in self.alleles:
            if a not in self.chromosome:
                manque.append(a)
        i = 0
        while i < len(self.alleles):
            if self.chromosome.count(self.chromosome[i]) > 1:
                self.chromosome[i] = manque.pop(0)
            else:
                i += 1


class ThreadTirage(BaseThreadTirage):
    NOM = __name__.rsplit('.', maxsplit=1)[-1]

    DESCRIPTION = "Niveau (Algorithme Génétique)"

    DEFAUT = {'TAILLE_POPULATION_INI': 50,
              'TAILLE_POPULATION': 60,
              'MAX_GENERATIONS': 700,
              'TAUX_CROISEMENT': 0.9,
              'TAUX_MUTATION': 0.01,
              'OPTIMUM': 0.0,
              'REDONDANCE': False,
              'PONDERATION_VICTOIRES': 12.0,
              'CALCUL_PONDERATION_AUTO': True,
              'TAUX_AUGMENTATION': 1.05,
              'MAX_DISPARITE': 2,
              'DEPASSEMENT_MAX_DISPARITE': False,
              'CHAPEAUX_PARMIS': 6,
              'DEPASSEMENT_CHAPEAUX_PARMIS': True,
              }

    def __init__(self, *args, **kargs):
        BaseThreadTirage.__init__(self, *args, **kargs)
        self._env = None

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

        # Paramètre de pondération des victoires
        if self.config['calcul_ponderation_auto'] == True:  # Calcul du coefficient de pondération des victoires
            ponderation = 0
            for equipe in self.statistiques:
                parties = nb_parties(self.statistiques, equipe, self.config['equipes_par_manche'])
                if parties == 0:
                    ponderation += 12.0
                else:
                    ponderation += self.statistiques[equipe]['points'] / parties

            self.config['ponderation_victoires'] = ponderation / len(self.statistiques)
            self.rapport(message="Coefficient de pondération des victoires: %s" % self.config['ponderation_victoires'])

        self.rapport(message="Objectif: %s" % self.config['optimum'])
        # Créer l'environement
        Tirage.alleles = self.statistiques.keys()
        self._env = Environement(genese(Tirage, self.config['taille_population_ini']), **self.config)

        # Lancer l'algorithme
        self._env.run()

        self.tirage = creer_manches(self._env.elite.chromosome, self.equipes_par_manche)
        self.rapport(message="")
        self.rapport(message=tirage_texte(self.statistiques, self.tirage))

        # Verification de la pertinence de la solution

        # ERREUR 150: Une même équipe apparaît plusieurs fois dans le tirage.
        args = []
        for equipe in self.statistiques.keys():
            nb = self._env.elite.chromosome.count(equipe)
            if nb != 1:
                args.append((equipe, nb))
        if len(args) != 0:
            raise DrawResultError(150, args)

        elif self._env.elite.score >= 1e36:
            if self._env.elite.nv == NV_REDONDANCE:
                # ERREUR 154: La redondance n'est pas autorisée.
                raise DrawResultError(154, "")
            elif self._env.elite.nv == NV_DISPARITE:
                # ERREUR 155: La disparité est trop faible pour trouver une solution.
                raise DrawResultError(155, "")
            else:
                # ERREUR 156: La disparité doit être augmentée ou la redondance autorisée.
                raise DrawResultError(156, "")
