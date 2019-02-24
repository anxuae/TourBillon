#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import os
import sys
from datetime import datetime, timedelta

import tourbillon
from tourbillon.trb_cli import interpreteur
from tourbillon.trb_cli import progression
from tourbillon.trb_cli import terminal
from tourbillon.trb_core import tournois, joueurs
from tourbillon.trb_core import tirages
from tourbillon import images
from tourbillon.trb_core import constantes as cst

#--- Commandes -----------------------------------------------------------------

COMMANDES = [{'short': 'n', 'long': 'nouveau', 'aide': "Commencer un nouveau tournoi", 'cmd': 'T = __CLI.nouveau()'},
             {'short': 'e', 'long': 'enregistrer', 'aide': "Enregistrer le tournois en cours", 'cmd': '__CLI.enregistrer()'},
             {'short': 'c', 'long': 'charger', 'aide': "Charger un tournoi", 'cmd': 'T=__CLI.charger()'},
             {'short': 't', 'long': 'tirage', 'aide': "Créer un nouveau tirage", 'cmd': 'tir= __CLI.tirage()'},
             {'short': 'r', 'long': 'resultat', 'aide': "Entrer les résultats d'une équipe (ex: 4 g 12 False)\n\
                                Le 4ème argument indique qu'il ne faut pas enregistrer l'heure\n\
                                actuelle comme heure de fin.", 'cmd': 'tir= __CLI.resultat()'},
             {'short': 'q', 'long': 'quitter', 'aide': "Quitter TourBillon CLI", 'cmd': '__CLI.quitter()'},
             {'short': 'a', 'long': 'aide', 'aide': "Aide TourBillon CLI", 'cmd': '__CLI.afficher_aide()'},
             {'short': 'l', 'long': 'licence', 'aide': "Licence GNU GPL", 'cmd': '__CLI.licence()'}]

#--- Fonctions -----------------------------------------------------------------


def question(texte=''):
    return raw_input("%s%s%s" % (terminal.GREEN, texte, terminal.NORMAL))

#--- Classes -------------------------------------------------------------------


class SortieCouleur(object):

    def __init__(self, sortie, couleur='normal'):
        self.couleur = getattr(terminal, couleur.upper())
        self.sortie = sortie

    def _format_localisation(self, texte):
        l = texte.split(', ')
        p0 = l[0].split('"')
        p1 = l[1].split(' ')
        texte = p0[0] + '"' + terminal.CYAN + p0[1] + self.couleur + '", '
        texte += p1[0] + terminal.CYAN + ' ' + p1[1] + self.couleur + ', '
        for t in l[2:]:
            texte += t
        return texte

    def read(self):
        return self.sortie.read()

    def readlines(self):
        return self.sortie.readlines()

    def write(self, texte):
        if texte.startswith('  File'):
            texte = self._format_localisation(texte)
        texte = "%s%s%s" % (self.couleur, texte, terminal.NORMAL)
        self.sortie.write(texte)

    def writelines(sequence):
        new_sequence = []
        i = 0
        while i < len(sequence):
            if i == 0:
                new_sequence.append(self.couleur + sequence[i])
            elif i == len(sequence) - 1:
                new_sequence.append(sequence[i] + terminal.NORMAL)
            else:
                new_sequence.append(sequence[i])
        self.sortie.writelines(new_sequence)

    def isatty(self):
        return self.sortie.isatty()

sys.stderr = SortieCouleur(sys.__stdout__, 'red')


class TourBillonCLI(object):

    def __init__(self, nom, config):
        self.config = config
        self._inter = interpreteur.Interpreteur({'__CLI': self, '__TRN': tournois, 'CONFIG': config}, COMMANDES)
        self._inter.charger_historique(config.get('INTERFACE', 'historique'))
        joueurs.charger_historique(config.get('TOURNOI', 'historique'))

        # interpreter prompt.
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = terminal.NORMAL + ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = terminal.NORMAL + "... "

        print """TourBillon Copyright © 2010 La Billonnière.
This program comes with ABSOLUTELY NO WARRANTY; This is free software, and you
are welcome to redistribute it under certain conditions; type `l' for details.
"""
        print
        print images.entete(terminal=True)

    def run(self):
        """
        Let the interpreter execute the last line(s), and clean up accounting for
        the interpreter results:
        (1) the interpreter succeeds
        (2) the interpreter fails, finds no errors and wants more line(s)
        (3) the interpreter fails, finds errors and writes them to sys.stderr
        """
        try:
            plus = False
            while 1:
                try:
                    if plus:
                        ligne = raw_input(sys.ps2)
                    else:
                        ligne = raw_input(sys.ps1)

                    plus = self._inter.push(ligne)
                except KeyboardInterrupt, e:
                    print "\nKeyboardInterrupt"
                    plus = False
        except EOFError, e:
            print
            sys.exit(0)

    def quitter(self):
        cmd = question('Quitter TourBillon? (o / n): ')
        cmd = cmd.lower()
        if cmd == 'oui' or cmd == 'o':
            sys.exit(0)

    def licence(self):
        print tourbillon.__licence__

    def afficher_aide(self):
        texte = "Aide TourBillon CLI:\n"
        for commande in COMMANDES:
            texte = texte + "\t%-15s / %s :   %s\n" % (commande['long'], commande['short'], commande['aide'])

        print texte

    def nouveau(self):
        joueurs_par_equipe = question("Nombre de joueurs par équipe: ")
        if joueurs_par_equipe != '':
            self.config.set('TOURNOI', 'joueurs_par_equipe', str(int(float(joueurs_par_equipe))))

        equipes_par_manche = question("Nombre d'équipes par manche: ")
        if equipes_par_manche != '':
            self.config.set('TOURNOI', 'equipes_par_manche', str(int(float(equipes_par_manche))))

        points_par_manche = question("Points par manche: ")
        if points_par_manche != '':
            self.config.set('TOURNOI', 'points_par_manche', str(int(float(points_par_manche))))

        equipes_par_manche = self.config.getint("TOURNOI", "equipes_par_manche")
        joueurs_par_equipe = self.config.getint("TOURNOI", "joueurs_par_equipe")
        points_par_manche = self.config.getint("TOURNOI", "points_par_manche")
        return tournois.nouveau_tournoi(equipes_par_manche, points_par_manche, joueurs_par_equipe)

    def charger(self):
        fichier = question("Fichier: ")
        return tournois.charger_tournoi(fichier)

    def enregistrer(self):
        fichier = question("Chemin: ")
        if fichier == '':
            fichier = None

        tournois.enregistrer_tournoi(fichier)

        if fichier == None:
            print tournois.FICHIER_TOURNOI

        # Enregistrer l'historique joueurs
        joueurs.enregistrer_historique()

    def chapeaux(self):
        chap = question("Liste des chapeaux ([ENTRE] pour passer): ")
        if chap == '':
            return []
        else:
            return eval(chap)

    def tirage(self):
        if not tournois.tournoi():
            print u"Pas de tournoi commencé."
        else:
            t = question("Catégorie %s: " % tirages.__modules__.keys())
            if t not in tirages.__modules__:
                raise IOError, u"Catégorie invalide."

            if t != u"manuel":
                chap = self.chapeaux()
                exclues = question("Liste des équipes exclues ([ENTRE] pour passer): ")
                if exclues == '':
                    exclues = []
                else:
                    exclues = eval(exclues)

                stat = tournois.tournoi().statistiques(exclues)

                p = progression.BarreProgression('blue', largeur=60, vide='_')

                def printResulat(progression, message, resultat=None, erreur=None):
                    if erreur is None:
                        erreur = 'ok'
                        p.afficher(progression, '\n' + message + "\n\nTapez sur [ENTRER] pour arrêter.")

                    if resultat is not None:
                        p.afficher(p.valeur(), '\n' + message)
                        print
                        print "Tirage  : ", resultat['tirage']
                        print "Chapeaux: ", resultat['chapeaux']
                        print "Validé  : ", erreur

                tir = tirages.tirage(t, tournois.tournoi().equipes_par_manche, stat, chap, printResulat)

                if t == u"aleatoire_ag":
                    tir.configurer(optimum=0)
                elif t == u"niveau_ag":
                    tir.configurer(optimum=0)

                print
                tir.start()
                question()
                tir.stop()
                tir.join()
                return tir
            else:
                exclues = []
                equipes = []
                manches = question("Tirage: ")
                chap = self.chapeaux()
                manches = eval(manches)
                for manche in manches:
                    map(equipes.append, manche)
                for equipe in tournois.tournoi().equipes():
                    if equipe.numero not in equipes and equipe.numero not in chap:
                        exclues.append(equipe.numero)
                return manches

    def resultat(self):
        if not tournois.tournoi():
            print u"Pas de tournoi commencé."
        elif not tournois.tournoi().partie_courante():
            print u"Aucune partie démarrée"
        elif tournois.tournoi().partie_courante().statut == cst.P_NON_DEMARREE:
            print u"Le tirage n'a pas été fait."
        else:
            r = question('Resultat (ex: 4 12): ')
            r = r.split(' ')
            d = {}
            num = int(float(r[0]))
            pts = int(float(r[1]))
            d[num] = pts

            manche = tournois.tournoi().equipe(num).resultat(tournois.tournoi().partie_courante().numero)['adversaires']
            for num in manche:
                r = question('Points équipe n°%s: ' % num)
                r = r.strip()
                pts = int(float(r))
                d[num] = pts

            if tournois.tournoi().equipe(num).resultat(tournois.tournoi().partie_courante().numero)['duree'] != None:
                r = question(u"Enregistrer l'heure de fin? (o / n) ")
                if r.strip() in ['o', 'oui', 'y', 'yes']:
                    fin = datetime.now()
                else:
                    fin = None
            else:
                fin = datetime.now()

            tournois.tournoi().partie_courante().resultat(d, fin)


def run(config):
    nom = "TourBillon v %s.%s.%s" % tourbillon.__version__
    app = TourBillonCLI(nom, config)
    app.run()
