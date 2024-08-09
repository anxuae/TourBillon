# -*- coding: UTF-8 -*-

"""Configuration du logiciel."""


import os
import sys
import os.path as osp
import atexit
import ast
from optparse import OptionParser, OptionGroup, Option
import configparser as cfg
import tourbillon
from tourbillon import logger
from tourbillon.core import draws


def configdir(*names):
    return osp.join(CONFIGPATH, *names)

CONFIGPATH = osp.join(os.environ.get('APPDATA', osp.expanduser("~")), '.trb')
CONFIG = None
DEFAUT = {'INTERFACE': {'GEOMETRIE': (0, 0, 1000, 600),
                        'MAXIMISER': True,
                        'PLEIN_ECRAN': False,
                        'HISTORIQUE': configdir('hist_cmd'),
                        'ENREGISTREMENT': osp.expanduser("~"),
                        'ENREGISTREMENT_AUTO': False,
                        'NOUVEAU_AFFICHE_PREFERENCES': True,
                        'AFFICHER_STATISTIQUES': False,
                        'AFFICHER_SHELL': False,
                        'BAVARDE': True,
                        'IMAGE': "",
                        'CUMULE_STATISTIQUES': 0},

          'AFFICHAGE': {'DIMENSION_AUTO': True,
                        'MESSAGE': "Tournoi de Billon - %(date)s",
                        'MESSAGE_VISIBLE': True,
                        'MESSAGE_VITESSE': 20,
                        'MESSAGE_POLICE': "12;70;90;90;0;Times New Roman;-1",
                        'MESSAGE_COULEUR': (0, 0, 0, 255),
                        'TEXTE_INSCRIPTION': "Inscriptions en cours...",
                        'TEXTE_TIRAGE': "Tirage n°%(partie suivante)s en cours...",
                        'TEXTE_POLICE': "12;70;90;90;0;Times New Roman;-1",
                        'TEXTE_COULEUR': (34, 68, 13, 255),
                        'TITRE_POLICE': "12;70;90;90;0;Times New Roman;-1",
                        'TITRE_COULEUR': (34, 68, 13, 255),
                        'GRILLE_LIGNES': 15,
                        'GRILLE_POLICE': "12;70;90;90;0;Times New Roman;-1",
                        'GRILLE_DUREE_AFFICHAGE': 20000,
                        'GRILLE_TEMPS_DEFILEMENT': 100,
                        'GRILLE_DEFILEMENT_VERTICAL': True},

          'TOURNOI': {'HISTORIQUE': configdir('hist_jrs'),
                      'JOUEUR_COMPLETION': True,
                      'JOUEURS_PAR_EQUIPE': 2,
                      'CLASSEMENT_VICTOIRES': True,
                      'CLASSEMENT_DUREE': False,
                      'CLASSEMENT_JOKER': True,
                      'POINTS_PAR_MANCHE': 12,
                      'EQUIPES_PAR_MANCHE': 2,
                      'ALGORITHME_DEFAUT': 'level_dt', }
          }


def systeme_config():
    info = []
    try:
        import platform
        info.append(('Plateforme', platform.platform()))
    except ImportError:
        info.append(('Plateforme', 'Non installé'))

    try:
        info.append(('Python', platform.python_version()))
    except ImportError:
        info.append(('Python', 'Non installé'))

    try:
        import wx
        info.append(('WxPython', wx.__version__))
    except ImportError:
        info.append(('WxPython', 'Non installé'))

    try:
        import yaml
        info.append(('PyYAML', yaml.__version__))
    except ImportError:
        info.append(('PyYAML', 'Non installé'))

    try:
        import flask
        info.append(('Flask', flask.__version__))
    except ImportError:
        info.append(('Flask', 'Non installé'))

    info.append(('Encoding', sys.getdefaultencoding()))

    return info


def parse_options():
    """
    Parse la ligne de commande.
    """
    Option.ALWAYS_TYPED_ACTIONS += ('callback',)  # Display metavar also for options with callback
    parser = OptionParser(usage="TourBillon [fichier] [options]",
                          version="TourBillon v %s.%s.%s" % tourbillon.__version__)
    parser.formatter.max_help_position = 45
    parser.add_option("-p", "--prolixe", action="store_true", dest="verbose",
                      help="afficher tous les messages d'activité et de debug")
    parser.add_option("-l", "--lapidaire", action="store_false", dest="verbose",
                      help="afficher uniquement les alertes et les erreurs")

    group = OptionGroup(parser, "Type d'interface",
                        "TourBillon embarque plusieurs interfaces utilisateur"
                        " pour répondre aux divers besoins des infrastructures."
                        " Par défaut, il demarrera en mode `standalone` (interface graphique).")
    group.add_option("-b", "--backend", action='store_true', default=False,
                     help="démarrer TourBillon en tant que serveur HTTP REST (backend)")
    parser.add_option_group(group)
    Option.ALWAYS_TYPED_ACTIONS = ('store', 'append')
    return parser.parse_args()


def enregistrer_config():
    """
    Sauver la configuration utilisateur.
    """
    if CONFIG is not None:
        with open(configdir('cfg'), 'w', encoding='utf-8') as fp:
            CONFIG.write(fp)


def charger_config(dossier=None):
    """
    Charger la configuration utilisateur. (créée si non existante)
    """
    global CONFIG, CONFIGPATH
    CONFIG = TypedConfigParser()
    if dossier:
        CONFIGPATH = dossier

    # Création du répertoire
    if not osp.exists(configdir()):
        os.makedirs(configdir())

    # Lecture du fichier existant
    fichier = configdir('cfg')
    if osp.isfile(fichier):
        logger.debug("Chargement de la configuration...")
        with open(fichier, 'r', encoding='utf-8') as fp:
            CONFIG.read_file(fp)
    else:
        logger.debug("Création de la configuration...")

    # Création du fichier de configuration interface
    for section, options in list(DEFAUT.items()):
        if not CONFIG.has_section(section):
            CONFIG.add_section(section)
        for opt, val in list(options.items()):
            if not CONFIG.has_option(section, opt):
                CONFIG.set(section, opt, str(val))

    for section, generateur in list(draws.TIRAGES.items()):
        if not CONFIG.has_section(section):
            CONFIG.add_section(section)
        for opt, val in list(generateur.DEFAUT.items()):
            if not CONFIG.has_option(section, opt):
                CONFIG.set(section, opt, str(val))

    # Création du fichier d'historique des joueurs
    fichier_hist = configdir('hist_jrs')
    if not osp.isfile(fichier_hist):
        with open(fichier_hist, 'w', encoding='utf-8') as fp:
            pass # Create empty file

    # Création du fichier d'historique des commandes
    fichier_cmd = configdir('hist_cmd')
    if not osp.isfile(fichier_cmd):
        with open(fichier_cmd, 'w', encoding='utf-8') as fp:
            fp.write("_HiStOrY_V2_\n")
            fp.write("%alias\n")

    # Traitement des chemins
    CONFIG.set('INTERFACE', 'historique', osp.abspath(osp.expanduser(CONFIG.get('INTERFACE', 'historique'))))
    CONFIG.set('INTERFACE', 'enregistrement', osp.abspath(osp.expanduser(CONFIG.get('INTERFACE', 'enregistrement'))))
    if CONFIG.get('INTERFACE', 'image'):
        CONFIG.set('INTERFACE', 'image', osp.abspath(osp.expanduser(CONFIG.get('INTERFACE', 'image'))))
    CONFIG.set('TOURNOI', 'historique', osp.abspath(osp.expanduser(CONFIG.get('TOURNOI', 'historique'))))

    # Enregistrer la configuration avant de quitter
    atexit.register(enregistrer_config)
    return CONFIG


class TypedConfigParser(cfg.SafeConfigParser):

    def get_options(self, section, try_literal_eval=True, upper_keys=False):
        d = {}
        for key, value in self.items(section, raw=True):

            if try_literal_eval:
                try:
                    value = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    pass

            if upper_keys:
                d[key.upper()] = value
            else:
                d[key] = value

        return d

    def get_typed(self, section, option):
        value = self.get(section, option)
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value
