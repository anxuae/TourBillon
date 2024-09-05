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

          'TOURNOI': {'HISTORIQUE': '',
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


class Singleton(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TypedConfigParser(configparser.SafeConfigParser, metaclass=Singleton):

    def __init__(self, filename=None, load=True):
        super().__init__()
        self.filename = osp.abspath(osp.expanduser(filename))
        if filename and load:
            self.load(self.filename)

        # Save config before exit
        atexit.register(self.save)

    def load(self, filename: str):
        """
        Load configuration from file.
        """
        # Create config folder
        path = osp.dirname(osp.abspath(filename))
        if not osp.exists(path):
            os.makedirs(path)

        # Read file if exists
        if osp.isfile(filename):
            logger.debug("Configuration loading...")
            with open(filename, 'r', encoding='utf-8') as fp:
                self.read_file(fp)
        else:
            logger.debug("Creating configuration...")

        # Create default values for missing options
        for section, options in list(DEFAUT.items()):
            if not self.has_section(section):
                self.add_section(section)
            for opt, val in list(options.items()):
                if not self.has_option(section, opt):
                    self.set(section, opt, str(val))

        for section, generateur in list(draws.TIRAGES.items()):
            if not self.has_section(section):
                self.add_section(section)
            for opt, val in list(generateur.DEFAUT.items()):
                if not self.has_option(section, opt):
                    self.set(section, opt, str(val))

        # Traitement des chemins
        self.set('INTERFACE', 'enregistrement', osp.abspath(osp.expanduser(self.get('INTERFACE', 'enregistrement'))))
        if self.get('INTERFACE', 'image'):
            self.set('INTERFACE', 'image', osp.abspath(osp.expanduser(self.get('INTERFACE', 'image'))))

        return self

    def save(self) -> None:
        """
        Save the current or default values into the configuration file.
        """
        if self.filename:
            with open(self.filename, 'w', encoding='utf-8') as fp:
                self.write(fp)

    def get_options(self, section: str, typed: bool = True, upper_keys: bool = False) -> dict:
        """
        Return all options from a given section.
        """
        d = {}
        for key, value in self.items(section, raw=True):

            if typed:
                try:
                    value = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    pass

            if upper_keys:
                d[key.upper()] = value
            else:
                d[key] = value

        return d

    def get_typed(self, section: str, option: str):
        """
        Get a value from config and try to convert it in a native Python
        type (using the :py:mod:`ast` module).

        :param section: config section name
        :param option: option name
        """
        value = self.get(section, option)
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    def get_path(self, section: str, option: str) -> str:
        """
        Get a path from config. If option is a relative path, this method return
        an absolute path evaluated from configuration file path.

        :param section: config section name
        :param option: option name
        """
        path = self.get(section, option)
        if not path:  # Empty string, don't process it as it is not a path
            return path
        path = osp.expanduser(path)
        if not osp.isabs(path):
            path = osp.join(osp.relpath(osp.dirname(self.filename), '.'), path)
        return osp.abspath(path)

    def join_path(self, *names: str) -> str:
        """Return the directory path of the configuration file
        and join it the given names.

        :param names: names to join to the directory path
        """
        return osp.join(osp.dirname(self.filename), *names)
