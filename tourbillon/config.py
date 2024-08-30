# -*- coding: UTF-8 -*-

"""Configuration"""

import os
import os.path as osp
import sys
import atexit
import ast
import argparse
import logging
import configparser
from abc import ABCMeta

import tourbillon
from tourbillon import logger
from tourbillon.core import draws


def configdir(*names: str) -> str:
    """
    Return path based on configuration directory.
    """
    return osp.join(CONFIGPATH, *names)


CONFIGPATH = osp.join(os.environ.get('APPDATA', osp.expanduser("~")), '.trb')
DEFAUT = {'INTERFACE': {'GEOMETRIE': (0, 0, 1000, 600),
                        'MAXIMISER': True,
                        'PLEIN_ECRAN': False,
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


def system_config() -> list:
    """
    Return dependencies versions.
    """
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
        import fastapi
        info.append(('Fastapi', fastapi.__version__))
    except ImportError:
        info.append(('Fastapi', 'Non installé'))

    info.append(('Encoding', sys.getdefaultencoding()))

    return info


def parse_options():
    """
    Parse options from command-line.
    """
    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description=tourbillon.__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("filename", help="path to tournament file to load",
                        nargs='?', default=None)
    parser.add_argument('--version', help="show program's version number and exit",
                        action='version', version=tourbillon.__version__)
    parser.add_argument("-b", "--backend", help="Start TourBillon as a HTTP RESTful server",
                        action='store_true', default=False)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", help="report more information about operations",
                       dest='logging_level', action='store_const', const=logging.DEBUG, default=None)
    group.add_argument("-q", "--quiet", help="report only errors and warnings",
                       dest='logging_level', action='store_const', const=logging.WARNING, default=None)

    return parser.parse_args()


def save():
    """
    Sauver la configuration utilisateur.
    """
    cfg = TypedConfigParser()
    with open(configdir('cfg'), 'w', encoding='utf-8') as fp:
        cfg.write(fp)


def load(dossier=None):
    """
    Charger la configuration utilisateur. (créée si non existante)
    """
    global CONFIGPATH
    cfg = TypedConfigParser()
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
            cfg.read_file(fp)
    else:
        logger.debug("Création de la configuration...")

    # Création du fichier de configuration interface
    for section, options in list(DEFAUT.items()):
        if not cfg.has_section(section):
            cfg.add_section(section)
        for opt, val in list(options.items()):
            if not cfg.has_option(section, opt):
                cfg.set(section, opt, str(val))

    for section, generateur in list(draws.TIRAGES.items()):
        if not cfg.has_section(section):
            cfg.add_section(section)
        for opt, val in list(generateur.DEFAUT.items()):
            if not cfg.has_option(section, opt):
                cfg.set(section, opt, str(val))

    # Création du fichier d'historique des joueurs
    fichier_hist = configdir('hist_jrs')
    if not osp.isfile(fichier_hist):
        with open(fichier_hist, 'w', encoding='utf-8') as fp:
            pass # Create empty file

    # Traitement des chemins
    cfg.set('INTERFACE', 'enregistrement', osp.abspath(osp.expanduser(cfg.get('INTERFACE', 'enregistrement'))))
    if cfg.get('INTERFACE', 'image'):
        cfg.set('INTERFACE', 'image', osp.abspath(osp.expanduser(cfg.get('INTERFACE', 'image'))))
    cfg.set('TOURNOI', 'historique', osp.abspath(osp.expanduser(cfg.get('TOURNOI', 'historique'))))

    # Enregistrer la configuration avant de quitter
    atexit.register(save)
    return cfg


class Singleton(ABCMeta):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TypedConfigParser(configparser.SafeConfigParser, metaclass=Singleton):

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
        """Get a value from config and try to convert it in a native Python
        type (using the :py:mod:`ast` module).

        :param section: config section name
        :type section: str
        :param option: option name
        :type option: str
        """
        value = self.get(section, option)
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value
