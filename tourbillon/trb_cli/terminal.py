#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = """Module de control du Terminal

1) Importe et fournit la version 'correcte' de readline en fonction de
la plateforme.
Readline est utilisé dans TourBillon de la manière suivante:
            'from tourbillon.trb_cli import terminal
             terminal.readline... '.

Ce module fournis aussi les variables has_readline, has_curses,
uses_libedit et _outputfile.

2) Importe des variables pour le controle des cpolices et couleurs
du terminal.
Exemple d'utilisation:
    print BG_BLUE + 'Texte en fond bleu' + NORMAL
    print BLUE + UNDERLINE + 'Texte bleu souligné' + NORMAL
    print BLUE + BG_YELLOW + BOLD + 'Texte' + NORMAL
"""

#--- Import --------------------------------------------------------------------

import sys
import os

#--- Variables Globales -------------------------------------------------------

# Module courant
MODULE = sys.modules[__name__]

# Liste des couleurs disponibles dans le terminal.
COLORS = "BLUE GREEN CYAN RED MAGENTA YELLOW WHITE BLACK".split()

# Liste des controls du terminal (possibilité d'en ajouter plus).
CONTROLS = {'BOL':'cr',
            'UP':'cuu1',
            'DOWN':'cud1',
            'LEFT':'cub1',
            'RIGHT':'cuf1',
            'CLEAR_SCREEN':'clear',
            'CLEAR_EOL':'el',
            'CLEAR_BOL':'el1',
            'CLEAR_EOS':'ed',
            'BOLD':'bold',
            'BLINK':'blink',
            'DIM':'dim',
            'REVERSE':'rev',
            'UNDERLINE':'smul',
            'NORMAL':'sgr0',
            'HIDE_CURSOR':'cinvis',
            'SHOW_CURSOR':'cnorm'}

# Liste des capacités numériques
VALUES = {'COLUMNS':'cols', # Largeur du terminal (None pour inconnue)
          'LINES':'lines', # Hauteur du terminal (None pour inconnue)
          'MAX_COLORS': 'colors', }

#--- Fonctions -----------------------------------------------------------------

def default():
    """
    Ecriture des attributs par défaut
    """
    for color in COLORS:
        setattr(MODULE, color, '')
        setattr(MODULE, 'BG_%s' % color, '')
    for control in CONTROLS:
        setattr(MODULE, control, '')
    for value in VALUES:
        setattr(MODULE, value, None)

def setup():
    """
    Ecriture des controls du terminal
    """
    # Initializing terminal
    curses.setupterm()
    # 
    # Get the color escape sequence template or '' if not supported
    # setab and setaf are for ANSI escape sequences
    bgColorSeq = curses.tigetstr('setab') or curses.tigetstr('setb') or ''
    fgColorSeq = curses.tigetstr('setaf') or curses.tigetstr('setf') or ''

    for color in COLORS:
        # Get the color index from curses
        colorIndex = getattr(curses, 'COLOR_%s' % color)
        # Set the color escape sequence after filling the template with index
        setattr(MODULE, color, curses.tparm(fgColorSeq, colorIndex))
        # Set background escape sequence
        setattr(MODULE, 'BG_%s' % color, curses.tparm(bgColorSeq, colorIndex))

    for control in CONTROLS:
        # Set the control escape sequence
        setattr(MODULE, control, curses.tigetstr(CONTROLS[control]) or '')

    for value in VALUES:
        # Set terminal related values
        setattr(MODULE, value, curses.tigetnum(VALUES[value]))

def render(text):
    """
    Fonction pour faciliter l'usage des controls
    Exemple:
        apply("%(GREEN)s%(BOLD)stext%(NORMAL)s") -> un texte vert en gras
    """
    return text % MODULE.__dict__

#--- Main ---------------------------------------------------------------------

has_curses = False
try:
    import curses
    setup()
    has_curses = True
except Exception, e:
    # There is a failure; set all attributes to default
    print "Warning: %s" % e
    default()

try:
    import readline
    has_readline = True
except ImportError:
    try:
        import pyreadline as readline
        has_readline = True
    except ImportError:
        has_readline = False
        print "Warning: Library readline not installed"

if sys.platform == 'win32' and has_readline:
    try:
        _outputfile = readline.GetOutputFile()
    except AttributeError:
        print "Warning: Failed GetOutputFile"
        _outputfile = sys.stdout
        has_readline = False
else:
    _outputfile = sys.stdout

# Test to see if libedit is being used instead of GNU readline.
uses_libedit = False
if sys.platform == 'darwin' and has_readline:
    import commands
    for i in range(10):
        try:
            (status, result) = commands.getstatusoutput("otool -L %s | grep libedit" % readline.__file__)
            break
        except IOError, (errno, strerror):
            if errno == 4:
                continue
            else:
                break

    if status == 0 and len(result) > 0:
        # we are bound to libedit - new in Leopard
        print "Info: Leopard libedit detected."
        uses_libedit = True
