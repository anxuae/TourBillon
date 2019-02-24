#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Definition des tournois."""

#--- Import --------------------------------------------------------------------

import sys, os
from datetime import datetime, timedelta
import yaml

from tourbillon.images import entete
from tourbillon.trb_core.exceptions import FichierError, NumeroError, StatutError, IncoherenceError
from tourbillon.trb_core.equipes import Equipe
from tourbillon.trb_core.parties import Partie
from tourbillon.trb_core.constantes import (CHAPEAU, GAGNE, PERDU, FORFAIT,
                                            E_INCOMPLETE, P_NON_DEMARREE, P_EN_COURS, P_COMPLETE,
                                            T_INSCRIPTION, T_ATTEND_TIRAGE, T_PARTIE_EN_COURS)

#--- Global Variables ----------------------------------------------------------

TOURNOI = None
FICHIER_TOURNOI = None

#--- Fonctions -----------------------------------------------------------------

def tournoi():
    return TOURNOI

def nouveau_tournoi(equipes_par_manche = 2, points_par_manche = 12, joueurs_par_equipe = 2):
    global TOURNOI, FICHIER_TOURNOI
    TOURNOI = Tournoi(equipes_par_manche, points_par_manche, joueurs_par_equipe)
    FICHIER_TOURNOI = None
    return TOURNOI

def enregistrer_tournoi(fichier = None):
    global FICHIER_TOURNOI, TOURNOI
    if TOURNOI is None:
        raise IOError, u"Pas de tournoi commencé."
    elif fichier is None and FICHIER_TOURNOI is None:
        raise FichierError, u"Pas de fichier spécifié pour l'enregistrement."
    elif fichier is not None:
        if os.path.exists(fichier) and not os.path.isfile(fichier):
            raise FichierError, u"'%s' est un répertoire." % fichier
        else:
            FICHIER_TOURNOI = fichier

    # Enregistrer
    ancienne_date = TOURNOI.date_enregistrement
    try:
        f = open(FICHIER_TOURNOI, 'w')
        f.write(entete() + '\n')

        # Date enregistrement
        d = datetime.now()
        yaml.dump({'enregistrement': d}, f, default_flow_style = False)

        # Infos tournoi
        y = {}
        y['tournoi'] = {}
        y['tournoi']['debut'] = TOURNOI.debut
        y['tournoi']['equipes_par_manche'] = TOURNOI.equipes_par_manche
        y['tournoi']['joueurs_par_equipe'] = TOURNOI.joueurs_par_equipe
        y['tournoi']['points_par_manche'] = TOURNOI.points_par_manche
        yaml.dump(y, f, default_flow_style = False)

        # Infos inscription
        y = {}
        y['inscription'] = {}
        for equipe in TOURNOI.equipes():
            y['inscription'][equipe.numero] = []
            for joueur in equipe.joueurs():
                y['inscription'][equipe.numero].append([joueur.prenom, joueur.nom, joueur.age])
        yaml.dump(y, f, default_flow_style = False)

        # Infos parties
        y = {}
        y['parties'] = {}
        for equipe in TOURNOI.equipes():
            y['parties'][equipe.numero] = equipe._resultats
        yaml.dump(y, f, default_flow_style = False)

        f.close()
        TOURNOI.date_enregistrement = d
        TOURNOI.modifie = False
    except Exception, e:
        TOURNOI.date_enregistrement = ancienne_date
        raise IOError, u"L'enregistrement a échoué (%s)." % str(e)

def charger_tournoi(fichier):
    global FICHIER_TOURNOI, TOURNOI
    if not os.path.exists(fichier):
        raise FichierError, u"Le fichier '%s' n'existe pas." % fichier

    donnee = {}
    try:
        # Extraction des données
        f = open(fichier, 'r')
        y = yaml.load(f)
        f.close()
        nouveau_tournoi()

        # Date enregistrement
        TOURNOI.date_enregistrement = y['enregistrement']

        # Infos tournoi
        TOURNOI.debut = y['tournoi']['debut']
        TOURNOI.equipes_par_manche = y['tournoi']['equipes_par_manche']
        TOURNOI.joueurs_par_equipe = y['tournoi']['joueurs_par_equipe']
        TOURNOI.points_par_manche = y['tournoi']['points_par_manche']

        # Infos inscription
        for num in y['inscription']:
            equipe = TOURNOI.ajout_equipe(num)
            for joueur in y['inscription'][num]:
                equipe.ajout_joueur(joueur[0], joueur[1], joueur[2])

        # Infos parties
        for num in y['parties']:
            TOURNOI.equipe(num)._resultats = y['parties'][num]

        # Calcul du nombre de parties
        nb_parties = 0
        for equipe in TOURNOI.equipes():
            if len(equipe._resultats) > nb_parties:
                nb_parties = len(equipe._resultats)

        # Création des parties
        for num in range(1, nb_parties + 1):
            TOURNOI._liste_parties.append(Partie(TOURNOI))

        FICHIER_TOURNOI = fichier
        TOURNOI.date_chargement = datetime.now()
        TOURNOI.modifie = False
    except Exception, e:
        raise IncoherenceError, u"Le fichier '%s' est corrompu." % fichier

    return TOURNOI

#--- Classes -------------------------------------------------------------------

class Tournoi(object):
    def __init__(self, equipes_par_manche , points_par_manche, joueurs_par_equipe):
        self.equipes_par_manche = equipes_par_manche
        self.joueurs_par_equipe = joueurs_par_equipe
        self.points_par_manche = points_par_manche

        self.debut = datetime.now()
        self.date_chargement = None
        self.date_enregistrement = None

        self.modifie = False
        self._liste_equipes = {}
        self._liste_parties = []

    def __repr__(self):
        texte = """
        Tournoi de Billon:
            Date                : %s
            Nombre de parties   : %s
            Nombre d'équipes    : %s
            Equipes par manche  : %s
            Points par manche   : %s
            Joueurs par équipe  : %s
            
            Satut               : %s
        """
        return texte % (self.debut,
                        len(self._liste_parties),
                        len(self._liste_equipes),
                        self.equipes_par_manche,
                        self.points_par_manche,
                        self.joueurs_par_equipe,
                        self.statut)

    def statut():
        def fget(self):
            # Nombre d'équipe <3
            if self.nb_equipes() < 3:
                return T_INSCRIPTION

            # Toutes les informations ne sont pas entrées
            for equipe in self.equipes():
                if equipe.statut == E_INCOMPLETE:
                    return T_INSCRIPTION

            # Etat de la partie courante
            if self.partie_courante() is None:
                return T_ATTEND_TIRAGE
            else:
                if  self.partie_courante().statut == P_COMPLETE:
                    return T_ATTEND_TIRAGE
                else:
                    return T_PARTIE_EN_COURS
        return locals()

    statut = property(**statut())

    def statistiques(self, equipes_exclue = [], partie_limite = None):
        """
        Statistiques sur les parties précédentes des équipes spécifiées.
        """
        stat = {}
        classement = {}
        classement.update(self.classement())
        for equipe in self.equipes():
            if equipe not in equipes_exclue:

                stat[equipe.numero] = { 'points':equipe.total_points(partie_limite),
                                        'victoires':equipe.total_victoires(partie_limite),
                                        'chapeaux':equipe.total_chapeaux(partie_limite),
                                        'adversaires':equipe.adversaires(partie_limite),
                                        'manches':equipe.manches(partie_limite),
                                        'place':classement[equipe]}
        return stat

    def tirages(self):
        tir = []
        for partie in self._liste_parties:
            if partie.statut != P_NON_DEMARREE:
                tir.append(partie.tirage())
        return tir

    def nb_equipes(self):
        return len(self._liste_equipes)

    def equipe(self, numero):
        if numero not in self._liste_equipes:
            raise NumeroError, u"L'équipe n°%s n'existe pas." % numero
        else:
            return self._liste_equipes[numero]

    def equipes(self):
        return self._liste_equipes.values()

    def nouveau_numero_equipe(self):
        i = 1
        while i in self._liste_equipes:
            i += 1
        return i

    def ajout_equipe(self, numero):
        if numero in self._liste_equipes:
            raise NumeroError, u"L'équipe n°%s existe déjà." % numero

        eq = Equipe(self, numero)
        self._liste_equipes[eq.numero] = eq
        self.modifie = True
        return eq

    def suppr_equipe(self, numero):
        if numero not in self._liste_equipes:
            raise NumeroError, u"L'équipe n°%s n'existe pas." % numero

        self._liste_equipes.pop(numero)
        self.modifie = True

    def modifier_numero_equipe(self, numero, nouv_numero):
        if self.nb_parties() != 0:
            raise StatutError, u"Le numéro de l'équipe n°%s ne peut pas être changé." % numero
        if nouv_numero in self._liste_equipes:
            raise NumeroError, u"L'équipe n°%s existe déjà." % nouv_numero

        equipe = self._liste_equipes.pop(numero)
        equipe._num = nouv_numero
        self._liste_equipes[nouv_numero] = equipe
        self.modifie = True

    def nb_parties(self):
        return len(self._liste_parties)

    def partie(self, numero):
        if numero not in range(1, len(self._liste_parties) + 1):
            raise NumeroError, u"La partie n°%s n'existe pas." % numero
        else:
            return self._liste_parties[numero - 1]

    def partie_courante(self):
        if len(self._liste_parties) != 0:
            return self._liste_parties[-1]
        else:
            return None

    def parties(self):
        return self._liste_parties

    def ajout_partie(self):
        if self.statut == T_INSCRIPTION:
            raise StatutError, u"Impossible de créer une partie (inscriptions en cours)."
        elif self.statut == T_PARTIE_EN_COURS:
            raise StatutError, u"Impossible de créer une nouvelle partie (partie courante: %s)." % (self.partie_courante().statut)

        partie = Partie(self)
        self._liste_parties.append(partie)
        self.modifie = True
        return partie

    def suppr_partie(self, numero):
        if numero > len(self._liste_parties) or numero < 1:
            raise NumeroError, u"La partie n°%s n'existe pas." % numero
        else:
            partie = self.partie(numero)

            if partie.statut != P_NON_DEMARREE:
                for equipe in self._liste_equipes.values():
                    equipe._suppr_partie(numero)

            self._liste_parties.pop(numero - 1)
            self.modifie = True

    def classement(self, avec_duree = True):
        Equipe.cmp_avec_duree = avec_duree
        l = sorted(self.equipes(), cmp = Equipe.comparer, reverse = True)

        classement = []

        if self.nb_equipes() != 0:
            place = 1
            classement.append((l[0], place))
            i = 1
            while i < len(l):
                if l[i - 1].comparer(l[i]) != 0:
                    place = i + 1
                classement.append((l[i] , place))
                i += 1

        return classement
