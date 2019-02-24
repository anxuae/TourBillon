# -*- coding: UTF-8 -*-

"""Dessine une barre de progression annimée pour terminal (unix)
Utilisation:
    p = BarreProgression("blue")
    p.render(pourcentage, message)
"""

from tourbillon.cli.terminal import TERM
import sys


class BarreProgression(object):
    MODEL = (
        '%(valeur)3s%% %(couleur)s%(progression)s%(normal)s%(vide)s %(message)s\n')
    # Nombre de caractères de fin de ligne qui ne sont pas utilisés pour
    # l'affichage de la barre
    PADDING = 7

    def __init__(self, couleur=None, largeur=None, block='█', vide=' '):
        """
        couleur (str) : couleur (BLUE GREEN CYAN RED MAGENTA YELLOW WHITE BLACK)
        largeur (int) : largeur (optinnel)
        block   (str) : charactère affiché pour la progression (defaut '█')
        vide    (str) : charactère affiché pour le vide (defaut ' ')
        """
        if couleur:
            self.couleur = getattr(TERM, couleur.upper())
        else:
            self.couleur = ''
        if largeur and largeur < TERM.COLUMNS - self.PADDING:
            # Largeur par defaut
            self.largeur = largeur
            # Largeur en cas de message trop long
            self._largeur = largeur
        else:
            # Ajuster à la largeur du Terminal terminal
            self.largeur = TERM.COLUMNS - self.PADDING
        self.block = block
        self.vide = vide
        self.progression = None
        self.lignes = 0

    def valeur(self):
        if self.progression is not None:
            return self.progression * 100 / self._largeur
        else:
            return 0

    def texte(self):
        if self.progression is not None:
            return self.message
        else:
            return ''

    def afficher(self, valeur, message=''):
        """
        Afficher la barre de progression
        valeur (int)  : valeur en %
        message (str) : message (optionel)
        """
        inline_msg_len = 0
        if message:
            # Longueur de la première ligne du message
            self.message = message
            inline_msg_len = len(message.splitlines()[0])
        if inline_msg_len + self.largeur + self.PADDING > TERM.COLUMNS:
            # Le message est trop long pour être affiché en une ligne
            # Ajuster la largeur de la barre à la bonne taille.
            self._largeur = TERM.COLUMNS - inline_msg_len - self.PADDING
        else:
            self._largeur = self.largeur

        # Verifier si 'afficher' est appelé pour la première fois
        if self.progression != None:
            self.effacer()

        # Calcul de la progression
        self.progression = (self._largeur * valeur) / 100

        data = self.MODEL % {'valeur': valeur,
                             'couleur': self.couleur,
                             'progression': self.block * self.progression,
                             'normal': TERM.NORMAL,
                             'vide': self.vide * (self._largeur - self.progression),
                             'message': message}

        sys.stdout.write(data)
        sys.stdout.flush()
        # Nombre de lignes affichées
        self.lignes = len(data.splitlines())

    def effacer(self):
        """
        Effacer toutes les lignes affichées.
        """
        sys.stdout.write(
            self.lignes * (TERM.UP + TERM.BOL + TERM.CLEAR_EOL))

if __name__ == '__main__':

    import time

    p = BarreProgression('green', largeur=20, block='▣', vide='□')
    for i in range(101):
        p.afficher(
            i, '%s %%\nProcessing...\nDescription: Toto est aux cabinets.' % i)
        time.sleep(0.1)

    p = BarreProgression()
    for i in range(101):
        p.afficher(i, '%s %%' % i)
        time.sleep(0.1)
