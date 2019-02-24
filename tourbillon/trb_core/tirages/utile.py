#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Fonctions utiles à la création d'algorithmes de tirage."""

#--- Import --------------------------------------------------------------------

import random
from threading import Thread, Event
from tourbillon.trb_core.exceptions import TirageError, StopTirageError, SolutionError
from tourbillon.trb_core.constantes import MAXIMISE, MINIMISE

#--- fonctions math ------------------------------------------------------------

def Cnp(equipes, p, l=None, res=None):
    """
    Retourne les combinaisons (Cnp) possibles pour tirer 'p' équipes
    parmis la liste 'equipes' sans répétition.
    
    (ne pas renseigner 'l' et 'res' lors de l'appel.)
    """
    equipes = list(equipes)
    if l is None: l = []
    if res is None: res = []

    if p == 0:
        res.append(l)
        return
    if len(equipes) == 0:
        return

    l1 = list(l)
    l1.append(equipes.pop(len(equipes) - 1))
    equipes_bis = list(equipes)
    Cnp(equipes, p - 1, l1, res)
    Cnp(equipes_bis, p, l, res)

    return res

#--- fonctions générales -------------------------------------------------------

def tri_stat(statistiques, caracteristique):
    d = {}
    for eq in statistiques:
        chap = statistiques[eq][caracteristique]
        if chap not in d:
            d[chap] = []
        d[chap].append(eq)
    return d

def nb_chapeaux_necessaires(nb_equipes, nb_par_manche):
    if nb_equipes < nb_par_manche:
        raise TirageError, u"Pas assez d'équipes (nb équipes: %s, nb par manche: %s)" % (nb_equipes, nb_par_manche)
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

    return r[-6:]

def creer_manches(liste_equipes, equipes_par_manche):
    i = 1
    tirage = []
    manche = liste_equipes[0: equipes_par_manche]
    while manche != []:
        tirage.append(manche)
        manche = liste_equipes[i * equipes_par_manche:i * equipes_par_manche + equipes_par_manche]
        i += 1
    return tirage

def creer_liste(tirage):
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
        # plus de deux équipes donc il y a Cnp(manche, 2) posibilités.
        l = Cnp(manche, 2)
        semirencontres = {}
        nrc = 0
        for vu in l:
            vu.sort()
            cle = "_".join([unicode(num) for num in vu])
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
        nrc += 1 - (1.0 * semirencontres.values().count(0) / len(l))

        texte.append(u"%-15s: diff points = %-5s, redondance = %-5s, disparité = %-5s" % (manche, dp, nrc, dv))

    return '\n'.join(texte)

#--- classes -------------------------------------------------------------------

class NonValide(object):
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
            raise TypeError, "unsupported operand type(s) for |: '%s' and '%s'" % (type(self), type(other))

    __ror__ = __or__

NV = NonValide
NV_REDONDANCE = NonValide(redondance=1)
NV_DISPARITE = NonValide(disparite=2)

class BaseThreadTirage(Thread):
    """
    Base de la classe ThreadTirage.
    """
    def __init__(self, equipes_par_manche, statistiques, chapeaux=[], rapport=None):
        Thread.__init__(self)
        if self.__class__ == BaseThreadTirage:
            raise NotImplemented, u"Classe abstraite"

        self._stop = Event()
        self.config = {}
        self.equipes_par_manche = equipes_par_manche
        self.statistiques = statistiques
        self.erreur = None
        self.tirage = []
        self.chapeaux = chapeaux

        # Surcharge du rapport
        if rapport is not None:
            self.rapport = rapport

        self.configurer()

    def _arret_utilisateur(self):
        if self._stop.isSet() == True:
            raise StopTirageError, u"Arrêt demmandé par l'utilisateur."

    def configurer(self, **kwargs):
        self.config.update(kwargs)
        self.config['statistiques'] = self.statistiques
        self.config['equipes_par_manche'] = self.equipes_par_manche
        self.config['arret_utilisateur'] = self._arret_utilisateur
        self.config['rapport'] = self.rapport

    def start(self):
        self._stop.clear()
        Thread.start(self)

    def run(self):
        try:
            self.demarrer()
            msg = u"\nAlgorithme terminé."
            self.rapport(100, msg, {'tirage':self.tirage, 'chapeaux':self.chapeaux})
        except SolutionError, e:
            msg = u"\nAlgorithme terminé (%s)." % e
            self.erreur = e
            self.rapport(100, msg, {'tirage':self.tirage, 'chapeaux':self.chapeaux}, e)
        except StopTirageError, e:
            msg = u"\nAlgorithme terminé (arrêt utilisateur)."
            self.erreur = e
            self.rapport(100, msg, {'tirage':self.tirage, 'chapeaux':self.chapeaux}, e)

    def demarrer(self):
        """
        Cette methode DOIT être surchargée. Elle démarre l'algorithme
        de tirage.
        """
        pass

    def rapport(self, valeur=0, message=None, resultat={'tirage':[], 'chapeaux':[]}, erreur=None):
        """
        Cette methode peut être surchargée pour l'affichage d'un rapport
        de progression.
        """
        pass

    def stop(self):
        self._stop.set()

#--- Algorithme génétique ------------------------------------------------------

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

class Individu(object):
    alleles = [] # Version d'un gène
    optimization = MINIMISE

    def __init__(self, chromosome=None):
        self.chromosome = chromosome
        self.score = None  # set during evaluation

    def __repr__(self):
        return '<%s chromosome= %s score= %s>' % \
               (self.__class__.__name__, self.chromosome, self.score)

    def __cmp__(self, other):
        if self.optimization == MINIMISE:
            return cmp(self.score, other.score)
        else: # MAXIMISE
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

class Environement(object):
    def __init__(self, population , taille_population=100, max_generations=1000,
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
        self.message = u"Génération %-" + str(len(str(max_generations))) + u"s - score : %-8.5g (objectif: %s)"

    def run(self):
        while not self._but():
            self.pas()
            self._rapport()
        self.rapport(99, "")

    def _but(self):
        return self.generation > self.max_generations or \
               self.elite.score == self.optimum

    def _rapport(self):
        """
        Executer la fonction 'rapport'. Les arguments passés à la fonction
        sont:
            - le % de générations produites (par rapport au nombre maxi)
            - le score du meilleur individu de la dernière génération
        """
        if callable(self.rapport):
            evolution = self.generation * 100 / self.max_generations
            self.rapport(evolution, self.message % (self.generation, self.elite.score, self.optimum))

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
        competitors = [random.choice(self.population) for i in range(taille)]
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
        Retourne l'individu 
        """
        doc = "Individu ayant le meilleur score dans la population."
        def fget(self):
            return self.population[0]
        return locals()

    elite = property(**elite())
