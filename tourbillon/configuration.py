#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Configuration du logiciel."""

#--- Import --------------------------------------------------------------------

import os, sys
from shutil import copyfile
import atexit
import ast
from optparse import OptionParser, Option
import ConfigParser as cfg
import tourbillon
from tourbillon.trb_core.exceptions import ConfigError

#--- Global Variables ----------------------------------------------------------

USERPATH = os.path.join(os.path.expanduser("~") , '.trb')
CONFIG = None
OPTIONS = None
ARGS = []

#--- Fonctions -----------------------------------------------------------------

def verif_chemin(option, opt_str, value, parser):
    """
    Construit un chemin absolut avec le chemin donné. (i.e. avec os.curdir)
    
    option (Option)       : instance
    opt_str (str)         : nom de l'option utilisée
    value (str)           : valeur de l'option
    parser (OptionParser) : instance
    """
    if value is not None:
        arg = os.path.abspath(os.path.expanduser(value))
        if os.path.exists(arg):
            setattr(parser.values, option.dest, arg)
        else:
            parser.error(u"option %s: Pas de fichier %s." % (option, arg))

def parse_options():
    """
    Parse la ligne de commande.
    """
    global OPTIONS, ARGS

    Option.ALWAYS_TYPED_ACTIONS += ('callback',)  # Display metavar also for options with callback
    parser = OptionParser(usage = "TourBillon [options]", version = "TourBillon v %s.%s.%s" % tourbillon.__version__)
    parser.formatter.max_help_position = 45
    parser.add_option("-r", "--equipe_par_rencontre", metavar = '<nbr>', dest = "equipes_par_rencontre", default = None, help = u"Nombre d'équipes qui se rencontrent lors d'une manche")
    parser.add_option("-j", "--joueurs_par_equipe", metavar = '<nbr>', dest = "joueurs_par_equipes", default = None, help = u"Nombre de joueurs par équipe")
    parser.add_option("-c", "--charger", metavar = '<fichier>', dest = "fichier_tbr", type = 'string', action = "callback", callback = verif_chemin, help = "Tournoi à charger")
    parser.add_option("-l", "--ligne_de_commande", dest = "gui_active", default = True, action = "store_false", help = u"Démarrer TourBillon en ligne de commande")
    Option.ALWAYS_TYPED_ACTIONS = ('store', 'append')

    OPTIONS, ARGS = parser.parse_args()

    return OPTIONS

def enregistrer_config():
    """
    Sauver la configuration utilisateur.
    """
    if CONFIG is not None:
        path = os.path.join(USERPATH , '.cfg')
        file = open(path, 'w')
        CONFIG.write(file)
        file.close()

def charger_config():
    """
    Charger la configuration utilisateur. (créée si non existante)
    """
    chem = os.path.join(USERPATH , '.cfg')
    if os.path.exists(chem):
        # Charger le fichier de configuration
        global CONFIG
        CONFIG = TypedConfigParser()
        CONFIG.read(chem)
    else:
        raise ConfigError, u"Pas de fichier de configuration dans le répertoire utilisateur."

    # Traitement des données
    CONFIG.set('INTERFACE', 'historique', os.path.abspath(os.path.expanduser(CONFIG.get('INTERFACE', 'historique'))))
    CONFIG.set('TOURNOI', 'historique', os.path.abspath(os.path.expanduser(CONFIG.get('TOURNOI', 'historique'))))

    # Enregistrer la configuration avant de quitter
    atexit.register(enregistrer_config)

    return CONFIG

def creer_config():
    """
    Créer un dossier de config avec toutes les variables par défaut.
    """
    # Création du répertoire
    if not os.path.exists(USERPATH):
        os.makedirs(USERPATH)

    # Création du fichier de configuration
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)) , 'defaut.cfg')
    dest = os.path.join(USERPATH, '.cfg')
    copyfile(src, dest)

    # Création du fichier d'historique des joueurs
    chem = os.path.join(USERPATH , '.jou_hist')
    f = open(chem, 'w')
    f.close()

    # Création du fichier d'historique des joueurs
    chem = os.path.join(USERPATH , '.cmd_hist')
    f = open(chem, 'w')
    f.close()

class TypedConfigParser(cfg.SafeConfigParser):

    def get_options(self, section, literal_eval = True):
        d = {}
        for key, value in self.items(section):

            if literal_eval:
                try:
                    value = ast.literal_eval(value)
                except:
                    pass

            d[key] = value

        return d

    def get_typed(self, section, option, raw = False, vars = None):
        value = self.get(section, option, raw, vars)

        try:
            value = ast.literal_eval(value)
        except:
            pass

        return value
