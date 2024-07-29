# -*- coding: UTF-8 -*-

import sys
import code
from tourbillon import logger
from tourbillon.cli.terminal import TERM
from tourbillon.cli.completer import TrbCompleter
import atexit


class Interpreteur(code.InteractiveConsole):

    def __init__(self, shell, environ):
        self.shell = shell
        self.namespace = environ
        code.InteractiveConsole.__init__(self, self.namespace)
        self.fichier_historique = None
        self.completer = None
        self.tab = '    '
        self.initialise()

    def initialise(self):
        if TERM.readline:
            self.completer = TrbCompleter(self.shell,
                                          namespace=self.namespace,
                                          global_namespace=self.namespace,
                                          omit__names=False)

            TERM.readline.set_completer(self.completer.complete)

            rlcmds = []

            if sys.platform == 'darwin':
                rlcmds.append(r'"\C-[[5D": history-search-backward')
                rlcmds.append(r'"\C-[[5C": history-search-forward')
                if TERM.utilise_libedit:
                    rlcmds.append("bind ^I rl_complete")
                else:
                    rlcmds.append('tab: complete')
            else:
                rlcmds.append('tab: complete')
                rlcmds.append(r'"\C-up": history-search-backward')
                rlcmds.append(r'"\C-down": history-search-forward')
                if sys.platform == 'win32':
                    rlcmds.append('set show-all-if-ambiguous on')

            rlcmds.append(r'"\C-l": possible-completions')

            map(TERM.readline.parse_and_bind, rlcmds)

    def charger_historique(self, fichier):
        if TERM.readline:
            TERM.readline.set_history_length(1000)
            try:
                TERM.readline.read_history_file(fichier)
            except Exception, e:
                logger.warning("L'historique des commandes ne peut pas être lu (%s)" % e)
            self.fichier_historique = fichier
            atexit.register(self.enregistrer_historique)

    def enregistrer_historique(self):
        if not TERM.readline or self.fichier_historique is None:
            return
        try:
            TERM.readline.write_history_file(self.fichier_historique)
        except:
            logger.warning("Impossible d'enregistrer l'historique des commandes dans: %s" % self.fichier_historique)

    def push(self, ligne):
        return code.InteractiveConsole.push(self, ligne)

    def complete(self, text):
        """Return a sorted list of all possible completions on text.

        Inputs:

          - text: a string of text to be completed on.

        This is a wrapper around the completion mechanism, similar to what
        readline does at the command line when the TAB key is hit.  By
        exposing it as a method, it can be used by other non-readline
        environments (such as GUIs) for text completion.

        Exemple:
                  x = 'hello'
                  Interpreteur.complete('x.l')
                                       => ['x.ljust', 'x.lower', 'x.lstrip']
        """
        complete = self.completer.complete
        state = 0
        # use a dict so we get unique keys, since ipyhton's multiple
        # completers can return duplicates.  When we make 2.4 a requirement,
        # start using sets instead, which are faster.
        comps = {}
        while True:
            newcomp = complete(text, state, line_buffer=text)
            if newcomp is None:
                break
            comps[newcomp] = 1
            state += 1
        outcomps = comps.keys()
        outcomps.sort()
        return outcomps
