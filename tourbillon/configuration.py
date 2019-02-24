#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Configuration du logiciel."""

#--- Import --------------------------------------------------------------------

import os, sys
import os.path as osp
import atexit
import codecs
from compiler import parse
from compiler.ast import *
from optparse import OptionParser, Option
import ConfigParser as cfg
import tourbillon
from tourbillon.trb_core.exceptions import ConfigError
from tourbillon.trb_core import tirages

#--- Variables globales -------------------------------------------------------

USERPATH = osp.join(osp.expanduser("~"), '.trb')
CONFIG = None
OPTIONS = None
ARGS = []

DEFAUT = {'INTERFACE': {'GEOMETRIE'             : (0, 0, 1000, 600),
                        'MAXIMISER'             : True,
                        'PLEIN_ECRAN'           : False,
                        'HISTORIQUE'            : u"~/.trb/hist_cmd",
                        'ENREGISTREMENT'        : u"~/",
                        'ENREGISTREMENT_AUTO'   : False,
                        'NOUVEAU_AFFICHE_PREFERENCES': True,
                        'AFFICHER_STATISTIQUES' : False,
                        'BAVARDE'               : True,
                        'IMAGE'                 : u"",
                        'CUMULE_STATISTIQUES'   : 0},

          'AFFICHAGE': {'DIMENSION_AUTO'        : True,
                        'MESSAGE'               : u"Tournoi de Billon - %(date)s",
                        'MESSAGE_VISIBLE'       : True,
                        'MESSAGE_VITESSE'       : 20,
                        'MESSAGE_POLICE'        : u"12;90;90;90;0;Times New Roman;-1",
                        'MESSAGE_COULEUR'       : (0, 0, 0, 255),
                        'TEXTE_INSCRIPTION'     : u"Inscriptions en cours...",
                        'TEXTE_TIRAGE'          : u"Tirage n°%(partie suivante)s en cours...",
                        'TEXTE_POLICE'          : u"12;90;90;90;0;Times New Roman;-1",
                        'TEXTE_COULEUR'         : (34, 68, 13, 255),
                        'TITRE_POLICE'          : u"12;90;90;90;0;Times New Roman;-1",
                        'TITRE_COULEUR'         : (34, 68, 13, 255),
                        'GRILLE_LIGNES'         : 15,
                        'GRILLE_POLICE'         : u"12;90;90;90;0;Times New Roman;-1",
                        'GRILLE_DUREE_AFFICHAGE': 20000,
                        'GRILLE_TEMPS_DEFILEMENT': 100,
                        'GRILLE_DEFILEMENT_VERTICAL': True},

          'TOURNOI': {  'HISTORIQUE'            : u"~/.trb/hist_jrs",
                        'JOUEUR_COMPLETION'     : True,
                        'JOUEURS_PAR_EQUIPE'    : 2,
                        'CLASSEMENT_VICTOIRES'  : True,
                        'CLASSEMENT_DUREE'      : False,
                        'POINTS_PAR_MANCHE'     : 12,
                        'EQUIPES_PAR_MANCHE'    : 2,
                        'ALGORITHME_TIRAGE'     : 'niveau2008_dt', }
        }

#--- Fonctions -----------------------------------------------------------------


def systeme_config():
    info = []
    try:
        import platform
        info.append(('Plateforme', platform.platform()))
    except:
        info.append(('Plateforme', 'Inconnu'))

    try:
        info.append(('Python version', platform.python_version()))
    except:
        info.append(('Python version', 'Inconnu'))

    try:
        import wx
        info.append(('WxPython version', wx.__version__))
    except:
        info.append(('WxPython version', 'Inconnu'))

    try:
        import yaml
        info.append(('PyYAML version', yaml.__version__))
    except:
        info.append(('PyYAML version', 'Inconnu'))

    info.append(('Encoding', sys.getdefaultencoding()))

    return info


def literal_eval(node_or_string):
    """
    Safely evaluate an expression node or a string containing a Python
    expression.  The string or node provided may only consist of the
    following
    Python literal structures: strings, numbers, tuples, lists, dicts,
    booleans, and None.
    """
    _safe_names = {'None': None, 'True': True, 'False': False}
    if isinstance(node_or_string, basestring):
        node_or_string = parse(node_or_string, mode='eval')
    if isinstance(node_or_string, Expression):
        node_or_string = node_or_string.node

    def _convert(node):
        if isinstance(node, Const) and isinstance(node.value,
              (basestring, int, float, long, complex)):
            return node.value
        elif isinstance(node, Tuple):
            return tuple(map(_convert, node.nodes))
        elif isinstance(node, List):
            return list(map(_convert, node.nodes))
        elif isinstance(node, Dict):
            return dict((_convert(k), _convert(v)) for k, v
                    in node.items)
        elif isinstance(node, Name):
            if node.name in _safe_names:
                return _safe_names[node.name]
        elif isinstance(node, UnarySub):
            return -_convert(node.expr)
        raise ValueError('malformed string')
    return _convert(node_or_string)


def parse_options():
    """
    Parse la ligne de commande.
    """
    global OPTIONS, ARGS

    Option.ALWAYS_TYPED_ACTIONS += ('callback',)  # Display metavar also for options with callback
    parser = OptionParser(usage="TourBillon [fichier] [options]", version="TourBillon v %s.%s.%s" % tourbillon.__version__)
    parser.formatter.max_help_position = 45
    parser.add_option("-r", "--equipe_par_rencontre", metavar='<nbr>', dest="equipes_par_rencontre", default=None, help=u"Nombre d'équipes qui se rencontrent lors d'une manche")
    parser.add_option("-j", "--joueurs_par_equipe", metavar='<nbr>', dest="joueurs_par_equipes", default=None, help=u"Nombre de joueurs par équipe")
    parser.add_option("-l", "--ligne_de_commande", dest="gui_active", default=True, action="store_false", help=u"Démarrer TourBillon en ligne de commande")
    Option.ALWAYS_TYPED_ACTIONS = ('store', 'append')

    OPTIONS, ARGS = parser.parse_args()

    return OPTIONS, ARGS


def enregistrer_config():
    """
    Sauver la configuration utilisateur.
    """
    if CONFIG is not None:
        chem = osp.join(USERPATH, 'cfg')
        fp = codecs.open(chem, 'wb', 'utf-8')
        CONFIG.write(fp)
        fp.close()


def charger_config():
    """
    Charger la configuration utilisateur. (créée si non existante)
    """
    global CONFIG
    CONFIG = TypedConfigParser()

    # Création du répertoire
    if not osp.exists(USERPATH):
        os.makedirs(USERPATH)

    # Lecture du fichier existant
    chem = osp.join(USERPATH, 'cfg')
    if osp.isfile(chem):
        print u"Réparation de la configuration"
        fp = codecs.open(chem, 'rb', 'utf-8')
        CONFIG.readfp(fp)
        fp.close()
    else:
        print u"Creation de la configuration"

    # Création du fichier de configuration interface
    for section, options in DEFAUT.items():
        if not CONFIG.has_section(section):
            CONFIG.add_section(section)
        for opt, val in options.items():
            if not CONFIG.has_option(section, opt):
                CONFIG.set(section, opt, unicode(val))

    for section, module in tirages.TIRAGES.items():
        if not CONFIG.has_section(section):
            CONFIG.add_section(section)
        for opt, val in module.DEFAUT.items():
            if not CONFIG.has_option(section, opt):
                CONFIG.set(section, opt, unicode(val))

    # Création du fichier d'historique des joueurs
    chem = osp.join(USERPATH, 'hist_jrs')
    if not osp.isfile(chem):
        fp = codecs.open(chem, 'wb', 'utf-8')
        fp.close()

    # Création du fichier d'historique des commandes
    chem = osp.join(USERPATH, 'hist_cmd')
    if not osp.isfile(chem):
        fp = codecs.open(chem, 'wb', 'utf-8')
        fp.write(u"_HiStOrY_V2_\n")
        fp.close()

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
                    value = literal_eval(value)
                except Exception:
                    pass

            if upper_keys:
                d[key.upper()] = value
            else:
                d[key] = value

        return d

    def get_typed(self, section, option, raw=False, vars=None):
        value = self.get(section, option, raw, vars)
        try:
            value = literal_eval(value)
        except Exception:
            pass
        return value
