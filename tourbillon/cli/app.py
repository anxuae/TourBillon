# -*- coding: UTF-8 -*-

import sys
import __builtin__
from datetime import datetime

import tourbillon
from tourbillon.cli.interpreteur import Interpreteur
from tourbillon.cli import progression
from tourbillon.cli.terminal import TERM
from tourbillon.core import tournoi, joueur
from tourbillon.core import tirages
from tourbillon import images
from tourbillon.core import constantes as cst


def question(texte='', strip=True):
    reponse = raw_input(TERM.formater('{GREEN}%s') % texte)
    if strip:
        reponse = reponse.strip()
    return reponse


def normalise_chaine(s):
    """
    Retourne une chaine de charactères dans des guillemets appropriés sous
    forme de ligne si possible.
    """
    tail = ''
    tailpadding = ''
    raw = ''
    if "\\" in s:
        raw = 'r'
        if s.endswith('\\'):
            tail = '[:-1]'
            tailpadding = '_'
    if '"' not in s:
        quote = '"'
    elif "'" not in s:
        quote = "'"
    elif '"""' not in s and not s.endswith('"'):
        quote = '"""'
    elif "'''" not in s and not s.endswith("'"):
        quote = "'''"
    else:
        # give up, backslash-escaped string will do
        return '"%s"' % s.replace('"', '\\"').replace("'", "\\'")
    res = raw + quote + s + tailpadding + quote + tail
    return res


class Alias(object):
    ESC_ALIAS = '%'
    """
    Alias pour le shell interactif.

    Fonctions qui pevent être atteinte dans le shell avec %nom_fonction.
    """

    def __init__(self):
        __builtin__.exit = self.alias_quitter
        __builtin__.quit = self.alias_quitter
        self._quitter = False
        self.config = None
        self.locals = {}

    def liste_alias(self):
        """
        Retourne la liste des alias disponibles.

        Donne la liste après suppression du prefix (['ls','cd', ...], et non
        ['alias_ls','alias_cd',...]
        """

        # Alias définits dans la class
        class_alias = lambda fn: fn.startswith('alias_') and \
            callable(Alias.__dict__[fn])
        # Alias définits dans l'instance (ajoutés par l'utilisateur pendant
        # l'execution)
        inst_alias = lambda fn: fn.startswith('alias_') and \
            callable(self.__dict__[fn])

        aliases = [cle for cle in Alias.__dict__.keys() if class_alias(cle)] + \
                  [cle for cle in self.__dict__.keys() if inst_alias(cle)]

        out = []
        for fn in set(aliases):
            out.append(fn.replace('alias_', '', 1))
        out.sort()
        return out

    def commande(self, nom_alias, args_s):
        u"""
        Retourne la commande à executer dans le shell.
        """
        if nom_alias.startswith(self.ESC_ALIAS):
            nom_alias = nom_alias[1:]
        if nom_alias not in self.liste_alias():
            return None

        cmd = 'intf.alias_%s(%s)' % (nom_alias, normalise_chaine(args_s))
        return cmd

    def alias_licence(self, _args_s=''):
        u"""Afficher la licence GPL.

        Retrouver la licence dans sa version complète sur http://www.gnu.org/licenses/gpl.html
        """

        print u"""
        TourBillon est un logiciel libre distribué sous licence GPL, aussi appelée
        en français Licence Publique Générale GNU. Cette licence vous garantit les
        libertés suivantes :

            -  la liberté d’installer et d’utiliser TourBillon pour quelque usage
               que ce soit ;
            -  la liberté d’étudier le fonctionnement de TourBillon et de l’adapter
               à vos propres besoins en modifiant le code source, auquel vous avez
               un accès immédiat;
            -  la liberté de distribuer des copies à qui que ce soit, tant que vous
               n’altérez ni ne supprimez la licence ;
            -  la liberté d’améliorer TourBillon et de diffuser vos améliorations au
               public, de façon à ce que l’ensemble de la communauté puisse en tirer
               avantage, tant que vous n’altérez ni ne supprimez la licence.

        Il ne faut pas confondre logiciel libre et logiciel en domaine public. L’intérêt
        de la licence GPL (licence du logiciel libre) est de garantir la non-confiscation
        du logiciel, au contraire d’un logiciel du domaine public qui peut se voir
        transformé en logiciel propriétaire. Vous bénéficiez des libertés ci-dessus
        dans le respect de la licence GPL ; en particulier, si vous redistribuez ou si
        vous modifiez TourBillon, vous ne pouvez cependant pas y appliquer une licence
        qui contredirait la licence GPL (par exemple, qui ne donnerait plus le droit à
        autrui de modifier le code source ou de redistribuer le code source modifié).
        """

    def alias_alias(self, args_s=''):
        u"""
        Affiche l'aide des alias de Tourbillon.

        options:

            bref        : affiche un court résumé
        """

        mode = ''
        try:
            if args_s.split()[0] == 'bref':
                mode = 'bref'
        except Exception:
            pass

        alias_doc = []
        for nom_alias in self.liste_alias():
            nom_fonction = 'alias_' + nom_alias
            for space in (Alias, self):
                try:
                    fn = space.__dict__[nom_fonction]
                except KeyError, _e:
                    pass
                else:
                    break
            if mode == 'bref':
                # seulement la première ligne
                if fn.__doc__:
                    lignes = fn.__doc__.split('\n', 2)[:2]
                    if len(lignes) == 1:
                        fndoc = lignes[0].rstrip()
                    else:
                        if lignes[0].strip() == '':
                            fndoc = '\n'.join(lignes).rstrip()
                        else:
                            fndoc = lignes[0].rstrip()
                else:
                    fndoc = u"Pas de documentation"
            else:
                if fn.__doc__:
                    fndoc = fn.__doc__.rstrip()
                else:
                    fndoc = u"Pas de documentation"

            alias_doc.append('%s%s:\n\t%s\n\n' %
                             (self.ESC_ALIAS, nom_alias, fndoc))

        alias_doc = ''.join(alias_doc)

        if mode == 'bref':
            print alias_doc
            return

        outmsg = u"""
Alias des fonctions de Tourbillon:
==================================

Le système d'alias de Tourbillon fournis une série de fonctions qui permettent
de faciliter  l'utilisation  du logiciel en ligne de  commande. Tous ces alias
sont  préfixés avec le  caractère '%', mais les  paramètres  sont donnés sans
parenthèse ni guillemets (séparés par des espaces).

Le système d'alias est composé des fonctions suivantes:\n"""

        outmsg = ("%s\n%s\n\n" % (outmsg, alias_doc))

        print outmsg

    def alias_nouveau(self, _args_s=''):
        u"""
        Commencer un nouveau tournoi.

        options:

            <joueurs>        : nombre de joueurs par équipes
            <manches>        : nombre d'équipes par manche
            <points>         : nombre de points par manche
        """
        joueurs_par_equipe = question(u"Nombre de joueurs par équipe: ")
        if joueurs_par_equipe != '':
            self.config.set(
                'TOURNOI', 'joueurs_par_equipe', str(int(float(joueurs_par_equipe))))

        equipes_par_manche = question(u"Nombre d'équipes par manche: ")
        if equipes_par_manche != '':
            self.config.set(
                'TOURNOI', 'equipes_par_manche', str(int(float(equipes_par_manche))))

        points_par_manche = question(u"Points par manche: ")
        if points_par_manche != '':
            self.config.set(
                'TOURNOI', 'points_par_manche', str(int(float(points_par_manche))))

        equipes_par_manche = self.config.getint(
            "TOURNOI", "equipes_par_manche")
        joueurs_par_equipe = self.config.getint(
            "TOURNOI", "joueurs_par_equipe")
        points_par_manche = self.config.getint("TOURNOI", "points_par_manche")

        self.locals['trb'] = tournoi.nouveau_tournoi(
            equipes_par_manche, points_par_manche, joueurs_par_equipe)

        print tournoi.tournoi()
        print "NOTE: vous pouvez acceder au tournoi via la variable 'trb'"

    def alias_ouvrir(self, args_s=''):
        u"""
        Charger un tournoi.

        options:

            <fichier>        : fichier à charger
        """
        if args_s == '':
            args_s = question(u"Fichier: ", False)

        if args_s != '':
            self.locals['trb'] = tournoi.charger_tournoi(args_s)
            print tournoi.tournoi()
            print "NOTE: vous pouvez acceder au tournoi via la variable 'trb'"

    def alias_enregistrer(self, args_s=''):
        u"""
        Enregistrer le tournoi en cours.

        Les données d'un tournoi sont enregistées dans un fichier texte au format
        YAML ce qui permet une lecture et modification aisée. Cependant la modification
        manuelle de ces fichiers est à eviter au risque de corrompre les données.

        Si le nom du fichier n'est pas donné et qu'un tournoi est en cours, le fichier
        d'enregistrement courant sera écrasé (si il existe).

        options:

            <fichier>        : fichier à enregistrer
        """
        if args_s == '':
            if tournoi.FICHIER_TOURNOI is not None:
                args_s = tournoi.FICHIER_TOURNOI
                tournoi.enregistrer_tournoi()
            else:
                args_s = question(u"Fichier: ", False)
                if args_s != '':
                    tournoi.enregistrer_tournoi(args_s)
        else:
            tournoi.enregistrer_tournoi(args_s)

        if args_s != '':
            print u"Enregistré (%s)" % args_s

    def alias_tirage(self, _args_s=''):
        u"""
        Créer un nouveau tirage pas à pas:
            1. entrer le type de tirage

            2. entrer chaque équipes chapeau, les numéros doivent
               être séparés par une virgules
               Par exemple: 1,14, 31

            3. entrer les numéro d'équipes qui ont déclarées forfait,
               les numéros doivent être séparés par une virgules
               Par exemple: 6,12
        """
        if not tournoi.tournoi():
            print u"Pas de tournoi commencé."
            return

        choix = tirages.TIRAGES.keys()
        algo = question(
            u"Catégorie %s ([ENTRE] pour %s): " % (choix, choix[0]))
        if not algo:
            algo = choix[0]
        if algo not in tirages.TIRAGES:
            raise IOError(u"Catégorie invalide.")

        chap = question(u"Liste des chapeaux ([ENTRE] pour choix auto): ")
        if chap == '':
            chap = []
        else:
            chap = [int(num) for num in chap.split(',')]
        exclues = question(
            u"Liste des équipes exclues ([ENTRE] pour choix auto): ")
        if exclues == '':
            exclues = []
        else:
            exclues = [int(num) for num in exclues.split(',')]

        stat = tournoi.tournoi().statistiques(exclues)

        p = progression.BarreProgression('blue', largeur=60, vide='_')

        def printResulat(progression, message, _tps_restant):
            if generateur.erreur is None and message is not None:
                p.afficher(
                    progression, '\n' + message + u"\n\nTapez sur [ENTRER] pour arrêter.")

            if generateur.tirage:
                p.afficher(p.valeur(), '\n' + message)
                print
                print u"Tirage  : ", generateur.tirage
                print u"Chapeaux: ", generateur.chapeaux
                print u"Validé  : ", generateur.erreur or 'ok'

        generateur = tirages.creer_generateur(
            algo, tournoi.tournoi().equipes_par_manche, stat, chap, printResulat)
        generateur.configurer(**self.config.get_options(algo))

        print  # Pour passer une ligne
        generateur.start()
        question()
        generateur.stop()
        generateur.join()

        self.locals['tir'] = generateur
        print generateur
        print "NOTE: vous pouvez acceder au tirage via la variable 'tir'"

    def alias_demarrer(self, _args_s=''):
        u"""
        Démarrer une nouvelle partie avec le tirage précédement fait.
        """
        tirage = self.locals.get('tir')
        if not tirage:
            print u"Pas de tirage réalisé."
            return

        partie = tournoi.tournoi().ajout_partie()
        partie.demarrer(dict((i, tirage.tirage[i]) for i in range(
            len(tirage.tirage))), tirage.chapeaux)
        self.locals.pop('tir')

    def alias_resultat(self, _args_s=''):
        u"""
        Entrer les résultats d'une équipe (ex: 4 g 12 False)
            Le 4ème argument indique qu'il ne faut pas enregistrer
            l'heure actuelle comme heure de fin.
        """
        if not tournoi.tournoi():
            print u"Pas de tournoi commencé."
        elif not tournoi.tournoi().partie_courante():
            print u"Aucune partie démarrée"
        elif tournoi.tournoi().partie_courante().statut == cst.P_ATTEND_TIRAGE:
            print u"Le tirage n'a pas été fait."
        else:
            r = question(u"Resultat (ex: 4 12): ")
            r = r.split(' ')
            d = {}
            num = int(float(r[0]))
            pts = int(float(r[1]))
            d[num] = pts

            manche = tournoi.tournoi().equipe(num).resultat(tournoi.tournoi().partie_courante().numero).adversaires
            for num in manche:
                r = question(u"Points équipe n°%s: " % num)
                r = r.strip()
                pts = int(float(r))
                d[num] = pts

            if tournoi.tournoi().equipe(num).resultat(tournoi.tournoi().partie_courante().numero).duree is not None:
                r = question(u"Enregistrer l'heure de fin? (o / n) ")
                if r.strip() in ['o', 'oui', 'y', 'yes']:
                    fin = datetime.now()
                else:
                    fin = None
            else:
                fin = datetime.now()

            tournoi.tournoi().partie_courante().resultat(d, fin)

    def alias_quitter(self, _args_s=''):
        u"""
        Quitter TourBillon
        """
        cmd = question(u'Quitter TourBillon? (oui / non): ')
        cmd = cmd.lower()
        if cmd in ['oui', 'o', 'yes', 'y']:
            self._quitter = True


class TourBillonCLI(Alias):

    def __init__(self, config):
        Alias.__init__(self)
        self.config = config
        self.nom = '__cli__'
        self.locals = {'intf': self, 'trb': tournoi.tournoi(),
                       'cfg': config, 'cst': cst}
        self._inter = Interpreteur(self, self.locals)
        self._inter.charger_historique(config.get('INTERFACE', 'historique'))
        joueur.charger_historique(config.get('TOURNOI', 'historique'))

        # interpreter prompt.
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = TERM.formater("{NORMAL}>>> ")
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = TERM.formater("{BLUE}... ")

        print u"%s  Copyright © 2010  La Billonnière." % tourbillon.__nom__
        print u"""
This program comes with ABSOLUTELY NO WARRANTY; This is a free software, and
you are welcome to redistribute it under certain conditions;

type `%licence' for details.
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
            while not self._quitter:
                try:
                    if plus:
                        ligne = raw_input(sys.ps2)
                    else:
                        ligne = raw_input(sys.ps1)

                    try:
                        cmd = self.commande(
                            ligne.split()[0], ' '.join(ligne.split()[1:]))
                    except Exception:
                        cmd = None

                    if cmd is not None:
                        plus = self._inter.push(cmd)
                    else:
                        plus = self._inter.push(ligne)
                except KeyboardInterrupt, e:
                    print "\nKeyboardInterrupt"
                    plus = False
        except EOFError, e:
            print e
            sys.exit(1)

    def ouvrir(self, fichier):
        tournoi.charger_tournoi(fichier)
        self.locals['trb'] = tournoi.tournoi()
        print tournoi.tournoi()
