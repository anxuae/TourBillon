# -*- coding: UTF-8 -*-

"""Configuration du logiciel."""


import os
import sys
import os.path as osp
import atexit
import codecs
from compiler import parse
from compiler import ast
from optparse import OptionParser, OptionGroup, Option
import ConfigParser as cfg
import tourbillon
from tourbillon.core import tirages


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
                        'IMAGE': u"",
                        'CUMULE_STATISTIQUES': 0},

          'AFFICHAGE': {'DIMENSION_AUTO': True,
                        'MESSAGE': u"Tournoi de Billon - %(date)s",
                        'MESSAGE_VISIBLE': True,
                        'MESSAGE_VITESSE': 20,
                        'MESSAGE_POLICE': u"12;70;90;90;0;Times New Roman;-1",
                        'MESSAGE_COULEUR': (0, 0, 0, 255),
                        'TEXTE_INSCRIPTION': u"Inscriptions en cours...",
                        'TEXTE_TIRAGE': u"Tirage n°%(partie suivante)s en cours...",
                        'TEXTE_POLICE': u"12;70;90;90;0;Times New Roman;-1",
                        'TEXTE_COULEUR': (34, 68, 13, 255),
                        'TITRE_POLICE': u"12;70;90;90;0;Times New Roman;-1",
                        'TITRE_COULEUR': (34, 68, 13, 255),
                        'GRILLE_LIGNES': 15,
                        'GRILLE_POLICE': u"12;70;90;90;0;Times New Roman;-1",
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
                      'ALGORITHME_DEFAUT': 'niveau2008_dt', }
          }


def systeme_config():
    info = []
    try:
        import platform
        info.append(('Plateforme', platform.platform()))
    except:
        info.append(('Plateforme', 'Non installé'))

    try:
        info.append(('Python', platform.python_version()))
    except:
        info.append(('Python', 'Non installé'))

    try:
        import wx
        info.append(('WxPython', wx.__version__))
    except:
        info.append(('WxPython', 'Non installé'))

    try:
        import yaml
        info.append(('PyYAML', yaml.__version__))
    except:
        info.append(('PyYAML', 'Non installé'))

    try:
        import sqlite3
        info.append(('Sqlite3', sqlite3.version))
    except:
        info.append(('Sqlite3', 'Non installé'))

    try:
        import flask
        info.append(('Flask', flask.__version__))
    except:
        info.append(('Flask', 'Non installé'))

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
    if isinstance(node_or_string, ast.Expression):
        node_or_string = node_or_string.node

    def _convert(node):
        if isinstance(node, ast.Const) and isinstance(node.value,
                                                      (basestring, int, float, long, complex)):
            return node.value
        elif isinstance(node, ast.Tuple):
            return tuple(map(_convert, node.nodes))
        elif isinstance(node, ast.List):
            return list(map(_convert, node.nodes))
        elif isinstance(node, ast.Dict):
            return dict((_convert(k), _convert(v)) for k, v
                        in node.items)
        elif isinstance(node, ast.Name):
            if node.name in _safe_names:
                return _safe_names[node.name]
        elif isinstance(node, ast.UnarySub):
            return - _convert(node.expr)
        raise ValueError('malformed string')
    return _convert(node_or_string)


def parse_options():
    """
    Parse la ligne de commande.
    """
    Option.ALWAYS_TYPED_ACTIONS += ('callback',)  # Display metavar also for options with callback
    parser = OptionParser(usage="TourBillon [fichier] [options]",
                          version="TourBillon v %s.%s.%s" % tourbillon.__version__)
    parser.formatter.max_help_position = 45
    parser.add_option("-p", "--prolixe", action="store_true", dest="verbose",
                      help=u"afficher tous les messages d'activité et de debug")
    parser.add_option("-l", "--lapidaire", action="store_false", dest="verbose",
                      help=u"afficher uniquement les alertes et les erreurs")

    group = OptionGroup(parser, "Type d'interface",
                        "TourBillon embarque plusieurs interfaces utilisateur"
                        " pour répondre aux divers besoins des infrastructures."
                        " Par défaut, il demarrera en mode `standalone` (interface graphique).")
    group.add_option("-s", "--shell", action='store_true', default=False,
                     help=u"démarrer TourBillon en ligne de commandes")
    group.add_option("-b", "--backend", action='store_true', default=False,
                     help=u"démarrer TourBillon en tant que serveur HTTP REST (backend)")
    parser.add_option_group(group)
    Option.ALWAYS_TYPED_ACTIONS = ('store', 'append')

    options, args = parser.parse_args()

    if [options.shell, options.backend].count(True) > 1:
        parser.error("Les options `--backend` et `--shell` sont mutuellement exclusives")

    return options, args


def enregistrer_config():
    """
    Sauver la configuration utilisateur.
    """
    if CONFIG is not None:
        chem = configdir('cfg')
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
    if not osp.exists(configdir()):
        os.makedirs(configdir())

    # Lecture du fichier existant
    chem = configdir('cfg')
    if osp.isfile(chem):
        print u"Chargement de la configuration..."
        fp = codecs.open(chem, 'rb', 'utf-8')
        CONFIG.readfp(fp)
        fp.close()
    else:
        print u"Création de la configuration..."

    # Création du fichier de configuration interface
    for section, options in DEFAUT.items():
        if not CONFIG.has_section(section):
            CONFIG.add_section(section)
        for opt, val in options.items():
            if not CONFIG.has_option(section, opt):
                CONFIG.set(section, opt, unicode(val))

    for section, generateur in tirages.TIRAGES.items():
        if not CONFIG.has_section(section):
            CONFIG.add_section(section)
        for opt, val in generateur.DEFAUT.items():
            if not CONFIG.has_option(section, opt):
                CONFIG.set(section, opt, unicode(val))

    # Création du fichier d'historique des joueurs
    chem = configdir('hist_jrs')
    if not osp.isfile(chem):
        fp = codecs.open(chem, 'wb', 'utf-8')
        fp.close()

    # Création du fichier d'historique des commandes
    chem = configdir('hist_cmd')
    if not osp.isfile(chem):
        fp = codecs.open(chem, 'wb', 'utf-8')
        fp.write(u"_HiStOrY_V2_\n")
        fp.write(u"%alias\n")
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

    def get_typed(self, section, option, raw=False, variables=None):
        value = self.get(section, option, raw, variables)
        try:
            value = literal_eval(value)
        except Exception:
            pass
        return value
