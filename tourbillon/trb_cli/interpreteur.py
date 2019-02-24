#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import sys, os
import code
import _completer
import readline
import atexit

#--- Classes -------------------------------------------------------------------

class Interpreteur(code.InteractiveConsole):
    def __init__(self, environ, commandes):
        self.namespace = environ
        code.InteractiveConsole.__init__(self, self.namespace)
        self.commandes = commandes
        self.fichier_historique = None
        self.tab = '    '

        self.initialise()

    def initialise(self):
        readline.set_completer(self.get_completions)
        rlcmds = ['tab: complete',
                   r'"\C-[[5D": history-search-backward',
                   r'"\C-[[5C": history-search-forward']

        map(readline.parse_and_bind, rlcmds)

    def charger_historique(self, fichier):
        readline.set_history_length(1000)
        readline.read_history_file(fichier)
        self.fichier_historique = fichier
        # Enregistrer l'historique avant de quitter
        atexit.register(self.enregistrer_historique)

    def enregistrer_historique(self):
        if self.fichier_historique is not None:
            readline.write_history_file(self.fichier_historique)

    def get_commande(self, cmd):
        est_commande = False
        for commande in self.commandes:
            if cmd == commande['short'] or cmd == commande['long']:
                est_commande = True
                break

        if est_commande:
            cmd = commande['cmd']

        return cmd

    def push(self, ligne):
        ligne = self.get_commande(ligne)
        return code.InteractiveConsole.push(self, ligne)

    def get_completions(self, text, state):
        if text == '':
            readline.insert_text(self.tab)
            return None

        completer = _completer.Completer(self.namespace, None)
        choix = completer.complete(text)
        if state < len(choix):
            if '.' in text:
                l = text.split('.')
                if len(l) > 1:
                    l = l[:-1]
                    text = ''
                    for i in l:
                        text += i + '.'

                return  text + choix[state][0]
            else:
                return  choix[state][0]
        else:
            return None

    def get_description(self, text):
        obj = None
        if '.' not in text:
            try:
                obj = self.namespace[text]
            except KeyError:
                return ''

        else:
            try:
                splitted = text.split('.')
                obj = self.namespace[splitted[0]]
                for t in splitted[1:]:
                    obj = getattr(obj, t)
            except:
                return ''


        if obj is not None:
            try:
                #Python and Iron Python
                import inspect #@UnresolvedImport
                doc = inspect.getdoc(obj)
                if doc is not None:
                    return doc
            except:
                pass

        try:
            #if no attempt succeeded, try to return repr()... 
            return repr(obj)
        except:
            try:
                #otherwise the class 
                return str(obj.__class__)
            except:
                #if all fails, go to an empty string 
                return ''
