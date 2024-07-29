# -*- coding: UTF-8 -*-

"""Module de control du terminal (console texte). La variable TERM...

    1) fournit la version 'correcte' de readline en fonction de
       la plateforme ainsi que les variables `utilise_libedit` et `stdout`.

    2) importe des variables pour le controle des polices et couleurs
       du terminal.

       Exemple d'utilisation:
            TERM.formater("{BG_BLUE}Texte en fond ble")
            TERM.formater("{BLUE}{UNDERLINE}Texte bleu souligné")
            TERM.formater("{BLUE}{BG_YELLOW}{BOLD}Texte")
"""

import os
import sys
from tourbillon import logger


class _Terminal(object):

    # Liste des couleurs disponibles dans le terminal.TERM.
    COLORS = ['BLUE', 'GREEN', 'CYAN', 'RED', 'MAGENTA', 'YELLOW', 'WHITE', 'BLACK']

    # Liste des controls du terminal (possibilité d'en ajouter plus).
    CONTROLS = {'BOL': 'cr',
                'UP': 'cuu1',
                'DOWN': 'cud1',
                'LEFT': 'cub1',
                'RIGHT': 'cuf1',
                'CLEAR_SCREEN': 'clear',
                'CLEAR_EOL': 'el',
                'CLEAR_BOL': 'el1',
                'CLEAR_EOS': 'ed',
                'BOLD': 'bold',
                'BLINK': 'blink',
                'DIM': 'dim',
                'REVERSE': 'rev',
                'UNDERLINE': 'smul',
                'NORMAL': 'sgr0',
                'HIDE_CURSOR': 'cinvis',
                'SHOW_CURSOR': 'cnorm'}

    # Liste des capacités numériques
    VALUES = {'COLUMNS': 'cols',        # Largeur du terminal (None pour inconnue)
              'LINES': 'lines',         # Hauteur du terminal (None pour inconnue)
              'MAX_COLORS': 'colors', }

    def __init__(self):
        # `curses` installé?
        self.curses = None
        try:
            import curses
            self.curses = curses
            self._setup_curses()
        except Exception, e:
            logger.warning("'curses' n'est pas installé (%s)" % e)
            self._setup_basic()

        # `readline` installé?
        self.readline = None
        try:
            import readline
            self.readline = readline
        except ImportError:
            try:
                import pyreadline
                self.readline = pyreadline
            except ImportError:
                logger.warning("'readline' n'est pas installé")

        if sys.platform == 'win32' and self.readline:
            try:
                self.stdout = self.readline.GetOutputFile()
            except AttributeError:
                logger.warning("'readline.GetOutputFile()' a échoué")
                self.stdout = sys.stdout
                self.readline = None
        else:
            self.stdout = sys.stdout

        # Test to see if `libedit` is being used instead of GNU readline.
        # `libedit` is a non-GPL replacement for readline library (used on OSX).
        self.utilise_libedit = False
        if sys.platform == 'darwin' and self.readline:
            status, result = None, []
            import commands
            for _i in range(10):
                try:
                    (status, result) = commands.getstatusoutput(
                        "otool -L %s | grep libedit" % readline.__file__)
                    break
                except IOError, (errno, _strerror):
                    if errno == 4:
                        continue
                    else:
                        break

            if status == 0 and len(result) > 0:
                # we are bound to libedit - new in Leopard
                logger.debug("Utilisation de 'libedit' detecté.")
                self.utilise_libedit = True

    def _setup_basic(self):
        """
        Ecriture des controls du terminal, seulement les couleurs et quelques
        paramètres sont disponibles. Pour plus de contrôle sur le terminal,
        l'installation de la bibliothèque `curses` est nécessaire.
        """
        for color in self.COLORS:
            setattr(self, color, '')
            setattr(self, 'BG_%s' % color, '')
        for control in self.CONTROLS:
            setattr(self, control, '')
        for value in self.VALUES:
            setattr(self, value, None)

    def _setup_curses(self):
        """
        Ecriture des controls du terminal et paramètrage de la bibliothèque
        `curses`.
        """
        # Initializing terminal
        try:
            self.curses.setupterm()
        except Exception:
            # Hack if the path to terminfo database is not set
            os.environ['TERM'] = "xterm-256color"
            self.curses.setupterm()
            os.environ.pop('TERM')

        # Get the color escape sequence template or '' if not supported
        # setab and setaf are for ANSI escape sequences
        bgColorSeq = self.curses.tigetstr('setab') or self.curses.tigetstr('setb') or ''
        fgColorSeq = self.curses.tigetstr('setaf') or self.curses.tigetstr('setf') or ''

        for color in self.COLORS:
            # Get the color index from curses
            colorIndex = getattr(self.curses, 'COLOR_%s' % color)
            # Set the color escape sequence after filling the template with index
            setattr(self, color, self.curses.tparm(fgColorSeq, colorIndex))
            # Set background escape sequence
            setattr(self, 'BG_%s' % color, self.curses.tparm(bgColorSeq, colorIndex))

        for control in self.CONTROLS:
            # Set the control escape sequence
            setattr(self, control, self.curses.tigetstr(self.CONTROLS[control]) or '')

        for value in self.VALUES:
            # Set terminal related values
            setattr(self, value, self.curses.tigetnum(self.VALUES[value]))

    def formater(self, text, fin='{NORMAL}'):
        """
        Fonction pour faciliter l'usage des controls
        Exemple:
            formater("{GREEN}{BOLD}text") -> un texte vert en gras
        """
        text += fin
        return text.format(**self.__dict__)

TERM = _Terminal()
