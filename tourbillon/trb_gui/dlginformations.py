#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

from random import choice
from datetime import datetime

import wx
from wx import grid
from wx.lib import ticker

from tourbillon.trb_core import constantes as cst
from tourbillon.trb_core import tournoi
from tourbillon.trb_core.tirages import utile

from tourbillon import images
from tourbillon.trb_gui import grille as grl

#--- Variables globales -------------------------------------------------------

VARIABLES = {'date': '',
             'partie': 0,
             'partie suivante': 1}

#--- Fonctions ----------------------------------------------------------------


def tournoi_factice(equipes_par_manche, joueurs_par_equipe, nombre_equipes):
    prenoms = ['Antoine', 'Aurelien', 'Christophe', 'Corentin', 'Corinne', 'Eric', 'Florian', 'Gabriel',
             'Guillaume', 'Isabelle', 'Julien', 'Justine', 'Laetitia', 'Laurent', 'louis', 'Ludivine',
             'Marc', 'Mathieu', 'Nicolas', 'Olivier', 'Pascal', 'Pascaline', 'Philippe', 'Pierre', 'Quentin',
             'Richard', 'Samantha', 'Samuel', 'Thierry', 'Thomas', 'Valerie', 'Xavier', 'Yannick', 'Yohann']

    noms = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa', 'Lamda', 'Mu',
            'Nu', 'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Thau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega']

    t = tournoi.Tournoi(equipes_par_manche, 12, joueurs_par_equipe)

    # Créer les équipes
    num = 1
    while num <= nombre_equipes:
        equipe = t.ajout_equipe(num)
        for i in xrange(joueurs_par_equipe):
            equipe.ajout_joueur(choice(prenoms), choice(noms))
        num += 1

    # Créer une partie
    partie = t.ajout_partie()
    numeros = [equipe.numero for equipe in t.equipes()]
    tirage = utile.creer_manches(numeros, equipes_par_manche)
    chapeaux = []
    if len(tirage[-1]) < equipes_par_manche:
        chapeaux = tirage.pop(-1)

    partie.demarrer(dict(zip(range(len(tirage)), tirage)), chapeaux)

    i = 0
    while i < len(tirage) / 2:
        d = {}
        for j in xrange(equipes_par_manche):
            if j == 0:
                d[tirage[i][j]] = 12
            else:
                d[tirage[i][j]] = 8
        t.partie(1).resultat(d, datetime.now())
        i += 1

    return t


def wxFont_en_string(font):
    attr = []
    attr.append(str(font.GetPointSize()))
    attr.append(str(font.GetFamily()))
    attr.append(str(font.GetStyle()))
    attr.append(str(font.GetWeight()))
    attr.append(str(int(font.GetUnderlined())))
    attr.append(str(font.GetFaceName()))
    attr.append(str(font.GetEncoding()))
    return ';'.join(attr)


def string_en_wxFont(texte):
    attr = texte.split(';')
    return wx.Font(int(attr[0]), int(attr[1]), int(attr[2]),
                   int(attr[3]), int(attr[4]), attr[5], int(attr[6]))


#--- Classes -------------------------------------------------------------------


class ListeCyclique(object):
    def __init__(self, liste, nombre):
        if type(liste) == ListeCyclique:
            self._liste = liste._liste
            self._index = liste._index
            self._nombre = liste._nombre
        else:
            self._liste = liste
            self._index = 0
            self._nombre = nombre

    def __repr__(self):
        return "ListeCyclique%s" % unicode(tuple(self._liste))

    def __eq__(self, other):
        return other._liste == self._liste and self._nombre == other._nombre

    def __ne__(self, other):
        return other._liste != self._liste or self._nombre != other._nombre

    def __len__(self):
        return len(self._liste)

    def suivant(self):
        if self._liste == []:
            return []
        else:
            res = self._liste[self._index:self._index + self._nombre]
            if len(res) == self._nombre:
                self._index = self._index + self._nombre
                return res
            else:
                self._index = 0
                return res


class Grille(grid.Grid):
    def __init__(self, parent, lignes=1, colonnes=1):
        grid.Grid.__init__(self, parent, wx.ID_ANY)
        self.CreateGrid(1 + (lignes * 2), colonnes)

        self._horizontal_line_color = wx.Color(0, 0, 0)
        self._horizontal_line_width = 3

        # Propriétés générales de la gille
        self.SetColMinimalAcceptableWidth(0)
        self.SetRowMinimalAcceptableHeight(0)
        self.SetSelectionMode(0)
        self.SetGridLineColour(images.couleur('grille'))
        self.SetDefaultCellBackgroundColour(images.couleur('grille'))
        grid.Grid.SetColLabelSize(self, 0)
        grid.Grid.SetRowLabelSize(self, 0)
        self.EnableDragColSize(False)
        self.EnableDragRowSize(False)
        self.rafraichir()

    def rafraichir(self):
        self.SetRowPenWidth(self._horizontal_line_width)
        self.SetRowPenColor(self._horizontal_line_color)

    def GetNumberRows(self):
        return (grid.Grid.GetNumberRows(self) / 2) - 1

    def GetNumberCols(self):
        return grid.Grid.GetNumberCols(self)

    def SetColLabelSize(self, height):
        grid.Grid.SetRowSize(self, 0, height)

    def SetColLabelValue(self, col, value):
        grid.Grid.SetCellValue(self, 0, col, unicode(value))

    def SetColLabelAttr(self, attr):
        grid.Grid.SetRowAttr(self, 0, attr)

    def SetRowPenWidth(self, width):
        i = 1
        while i < grid.Grid.GetNumberRows(self):
            if i % 2 != 0:
                grid.Grid.SetRowSize(self, i, width)
            i += 1

    def SetRowPenColor(self, color):
        self._horizontal_line_color = color
        i = 1
        while i < grid.Grid.GetNumberRows(self):
            if i % 2 != 0:
                attr = grid.GridCellAttr()
                attr.SetBackgroundColour(color)
                grid.Grid.SetRowAttr(self, i, attr)
            i += 1

    def SetRowAttr(self, row, attr):
        grid.Grid.SetRowAttr(self, (row * 2) + 2, attr)

    def SetRowSize(self, row, height):
        grid.Grid.SetRowSize(self, (row * 2) + 2, height)

    def InsertRows(self, pos, numRows=1, updateLabels=False):
        grid.Grid.InsertRows(self, (pos * 2) + 2, numRows * 2, updateLabels)
        self.rafraichir()

    def DeleteRows(self, pos, numRows=1, updateLabels=False):
        grid.Grid.DeleteRows(self, (pos * 2) + 2, numRows * 2, updateLabels)

    def SetCellValue(self, row, col, value):
        grid.Grid.SetCellValue(self, (row * 2) + 2, col, value)

    def GetCellValue(self, row, col):
        return grid.Grid.GetCellValue(self, (row * 2) + 2, col)

    def SetCellTextColour(self, row, col, color):
        grid.Grid.SetCellTextColour(self, (row * 2) + 2, col, color)

    def GetCellTextColour(self, row, col):
        return grid.Grid.GetCellTextColour(self, (row * 2) + 2, col)


class GrilleTirage(Grille):
    def __init__(self, parent):
        Grille.__init__(self, parent, 1, 4)

        self.nombre_lignes_max = 15
        self.font = wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        self._compteur = self.nombre_lignes_max
        # Timer pour le temps de défilement
        self._timer = wx.Timer(self)
        self._liste = ListeCyclique([], self.nombre_lignes_max)
        self._largeur_clonne = [2, 4, 0.6, 3]

        # Propriétés générales de la gille
        self.SetColLabelAttr(self.attribut('entete'))
        self.SetColLabelSize(30)
        self.SetColLabelValue(0, u"N°")
        self.SetColLabelValue(1, u"Adversaire(s)")
        self.SetColLabelValue(2, u"")
        self.SetColLabelValue(3, u"Piquet")

        self.Bind(wx.EVT_TIMER, self._tourner, self._timer)

    def _tourner(self, event):
        """
        Tourner d'un pas les données.
        """
        if self._compteur < self.GetNumberRows():
            i = 0
            while i < self.GetNumberRows():
                for j in range(4):
                    self.SetCellTextColour(i, 0, wx.Color(0, 0, 200))
                    self.SetCellTextColour(i, 1, wx.Color(126, 126, 126))
                    self.SetCellTextColour(i, 3, wx.Color(0, 0, 0))
                    if i < self.GetNumberRows() - 1:
                        self.SetCellValue(i, j, self.GetCellValue(i + 1, j))
                    else:
                        if self._compteur < len(self.manches):
                            equipe = self.manches[self._compteur][0]
                            adversaires = self.manches[self._compteur][1:]
                            # Equipe
                            self.SetCellValue(i, 0, unicode(equipe))
                            # Adversaires
                            if adversaires:
                                self.SetCellValue(i, 1, " - ".join([unicode(num) for num in adversaires]))
                            else:
                                self.SetCellValue(i, 1, u"C")
                                self.SetCellTextColour(i, 1, images.couleur(cst.CHAPEAU))
                            # Piquet
                            piquet = tournoi.tournoi().equipe(equipe).resultat(tournoi.tournoi().partie_courante().numero).piquet
                            if not piquet:
                                piquet = "-"
                            self.SetCellValue(i, 3, unicode(piquet))
                        else:
                            self.SetCellValue(i, j, u"")
                i += 1
            self._compteur += 1
        else:
            self._timer.Stop()

    def redim(self, largeur, hauteur, redim_police=True):
        h = (hauteur - 100) / (self.GetNumberRows() + 1)
        l = (largeur - 100)
        if h > 80:
            h = 80

        if redim_police:
            self.font.SetPointSize(h * 0.70)

        self.SetColLabelAttr(self.attribut('entete'))
        self.SetColLabelSize(h * 0.80)

        self.SetColAttr(2, self.attribut('espace'))
        for colonne in range(self.GetNumberCols()):
            self.SetColSize(colonne, (self._largeur_clonne[colonne] * l) / sum(self._largeur_clonne))

        for ligne in range(self.GetNumberRows()):
            self.SetRowSize(ligne, h)
            # Coloration lignes paire/impaire
            if ligne % 2 == 0:
                self.SetRowAttr(ligne, self.attribut('paire'))
            else:
                self.SetRowAttr(ligne, self.attribut('impaire'))

    def maj_grille(self, liste, nombre_lignes, font):
        self._timer.Stop()
        self._compteur = self.GetNumberRows()
        self.nombre_lignes_max = nombre_lignes
        self.font = font

        l = ListeCyclique(liste, self.nombre_lignes_max)
        if l != self._liste:
            self._liste = l

            # Suppression des lignes
            self.DeleteRows(0, self.GetNumberRows())

            # Ajouter les lignes
            if len(self._liste) <= self.nombre_lignes_max:
                self.InsertRows(0, len(self._liste))
            else:
                self.InsertRows(0, self.nombre_lignes_max)

            self.changer(forcer=True)

    def changer(self, temps_defilement=0, forcer=False):
        if forcer or (self._compteur == self.GetNumberRows() and len(self._liste) > self.nombre_lignes_max):
            # Rotation de l'affichage précédent terminé et utilité de tourner
            self.manches = self._liste.suivant()
            self._compteur = 0
            if temps_defilement > 0:
                self._timer.Start(temps_defilement)
            else:
                i = 0
                while i < self.GetNumberRows():
                    self._tourner(None)
                    i += 1

    def attribut(self, ref):
        attr = wx.grid.GridCellAttr()
        if ref == 'paire':
            attr.SetBackgroundColour(images.couleur('grille_paire'))
            attr.SetFont(self.font)
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        elif ref == 'impaire':
            attr.SetBackgroundColour(images.couleur('grille_impaire'))
            attr.SetFont(self.font)
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        elif ref == 'espace':
            attr.SetBackgroundColour(images.couleur('grille'))
            attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        elif ref == 'entete':
            attr.SetBackgroundColour(images.couleur('texte_bouton'))
            attr.SetFont(self.font)
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        return attr


class DoubleGrilleTirage(wx.BoxSizer):
    """
    BoxSizer contenant les deux grilles utilisées pour afficher
    les tirages de la partie en cours.
    """
    def __init__(self, parent):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        self.grilles = [GrilleTirage(parent), GrilleTirage(parent)]
        self.separateur = wx.StaticText(parent, size=(10, -1))
        self.separateur.SetBackgroundColour(parent.titre_couleur)

        self.AddSpacer((50, 10), 1, wx.EXPAND)
        self.Add(self.grilles[0])
        self.AddSpacer((10, 10), 1, wx.EXPAND)
        self.Add(self.separateur, 0, wx.EXPAND | wx.BOTTOM, 10)
        self.AddSpacer((10, 10), 1, wx.EXPAND)
        self.Add(self.grilles[1])
        self.AddSpacer((50, 10), 1, wx.EXPAND)

        self.nombre_lignes_max = 30
        self._liste = ListeCyclique([], self.nombre_lignes_max)

    def Show(self, value=True):
        """
        Afficher les éléments en fonction de la taille
        de la liste à afficher dans las deux grilles.
        Masquer tous les éléments si value est faux.

        value (bool)
        """
        i = 0
        for element in self.GetChildren():
            if value == False:
                element.Show(value)
            else:
                if len(self.grilles[1]._liste) > 0:
                    element.Show(value)
                else:
                    if 1 < i < 6:
                        element.Show(False)
                    else:
                        element.Show(True)
            i += 1

    def IsShown(self):
        return self.grilles[0].IsShown()

    def split_liste(self, liste, taille_liste, defilement_vertical=True):
        l0 = []
        l1 = []
        if defilement_vertical:
            i = 0
            while taille_liste * i < len(liste):
                if i % 2 == 0:
                    l0 += liste[taille_liste * i:taille_liste * (i + 1)]
                else:
                    l1 += liste[taille_liste * i:taille_liste * (i + 1)]
                i += 1
        else:
            l0 = liste
            if len(liste) > taille_liste:
                l1 = ListeCyclique(liste, taille_liste)
                l1.suivant()
        return l0, l1

    def redim(self, largeur, hauteur, redim_police=True):
        largeur = (largeur - 150) / 2
        for grille in self.grilles:
            grille.redim(largeur, hauteur, redim_police)

    def maj_grille(self, liste, nombre_lignes, font, defilement_vertical):
        self.nombre_lignes_max = 2 * nombre_lignes
        self._liste = ListeCyclique(liste, self.nombre_lignes_max)
        l0, l1 = self.split_liste(liste, nombre_lignes, defilement_vertical)
        self.grilles[0].maj_grille(l0, nombre_lignes, font)
        self.grilles[1].maj_grille(l1, nombre_lignes, font)

    def changer(self, temps_defilement=0, forcer=False):
        if forcer or len(self._liste) > self.nombre_lignes_max:
            for grille in self.grilles:
                grille.changer(temps_defilement, forcer)


class GrilleResultats(Grille):
    def __init__(self, parent):
        Grille.__init__(self, parent, 2, 6)

        self.nombre_lignes_max = 15
        self.tournoi = None
        self.font = wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        self._compteur = self.nombre_lignes_max
        # Timer pour le temps de défilement
        self._timer = wx.Timer(self)
        self._liste = ListeCyclique([], self.nombre_lignes_max)
        self._largeur_clonne = [1, 6, 0.8, 0.8, 0.6, 0.8]

        # Propriétés générales de la gille
        self.SetColLabelAttr(self.attribut('entete'))
        self.SetColLabelSize(30)
        self.SetColLabelValue(0, u"N°")
        self.SetColLabelValue(1, u"Noms")
        self.SetColLabelValue(2, u"Etat")
        self.SetColLabelValue(3, u"Pts")
        self.SetColLabelValue(4, u"")
        self.SetColLabelValue(5, u"Vic")

        self.Bind(wx.EVT_TIMER, self._tourner, self._timer)

    def _tourner(self, event):
        """
        Tourner d'un pas les données.
        """
        if self._compteur < self.GetNumberRows():
            i = 0
            while i < self.GetNumberRows():
                if i < self.GetNumberRows() - 1:
                    self.SetCellValue(i, 0, self.GetCellValue(i + 1, 0))
                    self.SetCellValue(i, 1, self.GetCellValue(i + 1, 1))

                    self.SetCellValue(i, 2, self.GetCellValue(i + 1, 2))
                    self.SetCellTextColour(i, 2, self.GetCellTextColour(i + 1, 2))

                    self.SetCellValue(i, 3, self.GetCellValue(i + 1, 3))
                    self.SetCellTextColour(i, 3, wx.Color(0, 0, 255))

                    self.SetCellValue(i, 5, self.GetCellValue(i + 1, 5))
                else:
                    if self._compteur < len(self.num_equipes):
                        num = self.num_equipes[self._compteur]
                        equipe = self.tournoi.equipe(num)
                        # Numéro
                        self.SetCellValue(i, 0, unicode(num))
                        # Noms
                        noms = [unicode(joueur) for joueur in equipe.joueurs()]
                        noms = u" / ".join(noms)
                        self.SetCellValue(i, 1, noms)
                        # Etat
                        texte, couleur, _police = grl.etat_style(equipe.resultat(self.tournoi.partie_courante().numero).etat)
                        self.SetCellValue(i, 2, texte)
                        self.SetCellTextColour(i, 2, couleur)
                        # Points
                        self.SetCellValue(i, 3, unicode(equipe.resultat(self.tournoi.partie_courante().numero).points))
                        self.SetCellTextColour(i, 3, wx.Color(0, 0, 255))
                        # Nombre de victoires
                        self.SetCellValue(i, 5, unicode(equipe.total_victoires()))
                    else:
                        self.SetCellValue(i, 0, u"")
                        self.SetCellValue(i, 1, u"")
                        self.SetCellValue(i, 2, u"")
                        self.SetCellValue(i, 3, u"")
                        self.SetCellValue(i, 5, u"")
                i += 1
            self._compteur += 1
        else:
            self._timer.Stop()

    def redim(self, largeur, hauteur, redim_police=True):
        h = (hauteur - 100) / (self.GetNumberRows() + 1)
        l = (largeur - 100)
        if h > 80:
            h = 80

        if redim_police:
            self.font.SetPointSize(h * 0.70)

        self.SetColLabelAttr(self.attribut('entete'))
        self.SetColLabelSize(h * 0.80)

        self.SetColAttr(4, self.attribut('espace'))
        for colonne in range(self.GetNumberCols()):
            self.SetColSize(colonne, (self._largeur_clonne[colonne] * l) / sum(self._largeur_clonne))

        for ligne in range(self.GetNumberRows()):
            self.SetRowSize(ligne, h)
            # Coloration lignes paire/impaire
            if ligne % 2 == 0:
                self.SetRowAttr(ligne, self.attribut('paire'))
            else:
                self.SetRowAttr(ligne, self.attribut('impaire'))

    def maj_grille(self, tournoi, nombre_lignes, font):
        self._timer.Stop()
        self._compteur = self.GetNumberRows()
        self.nombre_lignes_max = nombre_lignes
        self.font = font
        self.tournoi = tournoi

        # Lecture des équipes
        l = []
        for equipe in self.tournoi.equipes():
            m = equipe.resultat(self.tournoi.partie_courante().numero)
            if m.etat != cst.FORFAIT:
                l.append(equipe.numero)
        l.sort()
        l = ListeCyclique(l, self.nombre_lignes_max)
        if l != self._liste:
            self._liste = l

            # Suppression des lignes
            self.DeleteRows(0, self.GetNumberRows())

            # Ajouter les lignes
            if len(self._liste) <= self.nombre_lignes_max:
                self.InsertRows(0, len(self._liste))
            else:
                self.InsertRows(0, self.nombre_lignes_max)

            self.changer(forcer=True)
        else:
            i = 0
            while i < self.GetNumberRows():

                num = self.GetCellValue(i, 0)
                if num != '':
                    num = int(num)
                    equipe = self.tournoi.equipe(num)
                    # Noms
                    noms = [unicode(joueur) for joueur in equipe.joueurs()]
                    noms = u" / ".join(noms)
                    self.SetCellValue(i, 1, noms)
                    # Etat
                    texte, couleur, _police = grl.etat_style(equipe.resultat(self.tournoi.partie_courante().numero).etat)
                    self.SetCellValue(i, 2, texte)
                    self.SetCellTextColour(i, 2, couleur)
                    # Points
                    self.SetCellValue(i, 3, unicode(equipe.resultat(self.tournoi.partie_courante().numero).points))
                    self.SetCellTextColour(i, 3, wx.Color(0, 0, 255))
                    # Nombre de victoires
                    self.SetCellValue(i, 5, unicode(equipe.total_victoires()))

                i += 1

    def changer(self, temps_defilement=0, forcer=False):
        if forcer or (self._compteur == self.GetNumberRows() and len(self._liste) > self.nombre_lignes_max):
            # Rotation de l'affichage précédent terminé et utilité de tourner
            self.num_equipes = self._liste.suivant()
            self._compteur = 0
            if temps_defilement > 0:
                self._timer.Start(temps_defilement)
            else:
                i = 0
                while i < self.GetNumberRows():
                    self._tourner(None)
                    i += 1

    def attribut(self, ref):
        attr = wx.grid.GridCellAttr()
        if ref == 'paire':
            attr.SetBackgroundColour(images.couleur('grille_paire'))
            attr.SetFont(self.font)
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        elif ref == 'impaire':
            attr.SetBackgroundColour(images.couleur('grille_impaire'))
            attr.SetFont(self.font)
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        elif ref == 'espace':
            attr.SetBackgroundColour(images.couleur('grille'))
            attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        elif ref == 'entete':
            attr.SetBackgroundColour(images.couleur('texte_bouton'))
            attr.SetFont(self.font)
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        return attr


class DialogueInformations(wx.Dialog):
    def __init__(self, parent, config):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title=u"Informations", style=wx.DEFAULT_FRAME_STYLE, pos=wx.DefaultPosition)
        w, h = wx.ScreenDC().GetSizeTuple()
        self.SetSize((w * 0.5, h * 0.5))
        self.SetBackgroundColour(images.couleur('grille'))

        # Timer pour durée d'affichage des données
        self._timer = wx.Timer(self)
        self._test_statut = "test inscription"

        # Configuration
        self.config = config
        self.configurer(config.get_options('AFFICHAGE', upper_keys=True))

        # Titre
        self.txt_titre = wx.StaticText(self, wx.ID_ANY, u"", style=wx.ALIGN_CENTER)

        # Texte
        self.txt_interlude = wx.StaticText(self, wx.ID_ANY, u"", style=wx.ALIGN_CENTER)

        # Grilles tirages
        self.gri_tirages = DoubleGrilleTirage(self)
        self.gri_tirages.Show(False)

        # Grille resultats
        self.gri_resultats = GrilleResultats(self)
        gri_resultats_box = wx.BoxSizer(wx.HORIZONTAL)
        gri_resultats_box.AddSpacer((20, 10), 1, wx.EXPAND)
        gri_resultats_box.Add(self.gri_resultats)
        gri_resultats_box.AddSpacer((20, 10), 1, wx.EXPAND)
        self.gri_resultats.Show(False)

        # Texte défilant
        self.ticker = ticker.Ticker(self)

        # Position des widgets
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add((10, 10), 0, wx.EXPAND)
        self.sizer.Add(self.txt_titre, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add((20, 20), 1)
        self.sizer.Add(self.txt_interlude, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add(self.gri_tirages, 0, wx.EXPAND | wx.ALIGN_CENTER)
        self.sizer.Add(gri_resultats_box, 0, wx.EXPAND | wx.ALIGN_CENTER)
        self.sizer.Add((20, 20), 1)
        self.sizer.Add(self.ticker, 0, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.Bind(wx.EVT_TIMER, self._suivant, self._timer)
        self.Bind(wx.EVT_LEFT_DCLICK, self.plein_ecran)
        self.txt_titre.Bind(wx.EVT_LEFT_DCLICK, self.plein_ecran)
        self.Bind(wx.EVT_CLOSE, self.stop_timer)
        self.Bind(wx.EVT_CHAR, self.echappe)
        self.Bind(wx.EVT_SIZE, self.redim, self)

    def _suivant(self, event):
        if self.gri_tirages.IsShown():
            self.gri_tirages.changer(self.grille_temps_defilement)
        elif self.gri_resultats.IsShown():
            self.gri_resultats.changer(self.grille_temps_defilement)

    def _rafraichir(self, statut):
        """
        NE PAS UTILISER !!!!! (Manipulé par la fenêtre principale)
        """
        partie = tournoi.tournoi().partie_courante()
        VARIABLES['date'] = tournoi.tournoi().debut.strftime("%d / %m / %Y")
        VARIABLES['partie'] = getattr(partie, 'numero', 0)
        VARIABLES['partie suivante'] = getattr(partie, 'numero', 0) + 1

        # Style des widgets
        self.txt_titre.SetFont(self.titre_police)
        self.txt_titre.SetForegroundColour(self.titre_couleur)

        self.txt_interlude.SetFont(self.texte_police)
        self.txt_interlude.SetForegroundColour(self.texte_couleur)

        self.ticker.SetFPS(self.message_vitesse)
        self.ticker.SetFont(self.message_police)
        self.ticker.SetForegroundColour(self.message_couleur)
        self.ticker.SetText(self.message % VARIABLES)

        if self.message_visible:
            self.ticker.Show(True)
        else:
            self.ticker.Show(False)

        if statut == cst.T_PARTIE_EN_COURS or statut in ['test tirage', 'test resultats']:

            # Ajustement timer
            if self._timer.GetInterval() != self.grille_duree_affichage:
                self._timer.Stop()
                self._timer.Start(self.grille_duree_affichage)

            if partie.nb_equipes() == len(partie.equipes_incompletes()) or statut == 'test tirage':
                # Afficher le grille du tirage
                self.txt_titre.SetLabel(u"Partie n°%s - Tirage" % tournoi.tournoi().partie_courante().numero)
                # Lecture du tirage
                l = []
                for equipe in tournoi.tournoi().equipes():
                    m = equipe.resultat(tournoi.tournoi().partie_courante().numero)
                    if m.etat != cst.FORFAIT:
                        l.append([equipe.numero] + m.adversaires)
                l.sort()

                self.gri_tirages.maj_grille(l, self.grille_lignes, self.grille_police, self.grille_defilement_vertical)
                self.txt_interlude.Show(False)
                self.gri_tirages.Show(True)
                self.gri_resultats.Show(False)
            else:
                # Afficher le grille des résultats
                self.txt_titre.SetLabel(u"Partie n°%s - Résultats" % tournoi.tournoi().partie_courante().numero)
                self.gri_resultats.maj_grille(tournoi.tournoi(), self.grille_lignes, self.grille_police)
                self.txt_interlude.Show(False)
                self.gri_tirages.Show(False)
                self.gri_resultats.Show(True)

        else:

            self.txt_interlude.Show(True)
            self.gri_tirages.Show(False)
            self.gri_resultats.Show(False)
            self.txt_titre.SetLabel(u"")

            if statut == cst.T_INSCRIPTION or statut == 'test inscription':
                # Afficher message inscription
                self.txt_interlude.SetLabel(self.texte_inscription % VARIABLES)
            elif statut == cst.T_ATTEND_TIRAGE or statut == 'test attend':
                # Afficher tirage en cours
                if partie:
                    self.txt_interlude.SetLabel(self.texte_tirage % VARIABLES)

        self.redim(None)
        self.Layout()

    def redim(self, event):
        if self.dimension_auto:
            # Titre
            font = self.txt_titre.GetFont()
            font.SetPointSize(int(self.GetSize()[1] * 0.06))
            self.txt_titre.SetFont(font)

            # Ticker
            font = self.ticker.GetFont()
            font.SetPointSize(int(self.GetSize()[1] * 0.06))
            self.ticker.SetFont(font)

            # Texte
            if self.txt_interlude.IsShown() and self.txt_interlude.GetLabel() != u"":
                font = self.txt_interlude.GetFont()
                font.SetPointSize((self.GetSize()[0] - 100) / (0.5 * len(self.txt_interlude.GetLabel())))
                self.txt_interlude.SetFont(font)

        # Grille tirages
        if self.gri_tirages.IsShown():
            self.gri_tirages.redim(self.GetSize()[0], self.GetSize()[1] * 0.8, self.dimension_auto)

        # Grille resultats
        if self.gri_resultats.IsShown():
            self.gri_resultats.redim(self.GetSize()[0], self.GetSize()[1] * 0.8, self.dimension_auto)

        if event:
            event.Skip()

    def test(self, suivant=False):
        courant = tournoi.tournoi()
        tournoi.TOURNOI = tournoi_factice(self.config.get_typed("TOURNOI", "EQUIPES_PAR_MANCHE"),
                                         self.config.get_typed("TOURNOI", "JOUEURS_PAR_EQUIPE"),
                                         self.grille_lignes * 2 + self.config.get_typed("TOURNOI", "EQUIPES_PAR_MANCHE"))
        if suivant:
            if self._test_statut == "test inscription":
                # Afficher texte tirage en cours
                self._test_statut = "test attend"
            elif self._test_statut == "test attend":
                # Afficher tirage
                self._test_statut = 'test tirage'
            elif self._test_statut == 'test tirage':
                # Afficher résultats
                self._test_statut = 'test resultats'
            elif self._test_statut == 'test resultats':
                # Boucle
                self._test_statut = "test inscription"

        self._rafraichir(self._test_statut)

        tournoi.TOURNOI = courant

    def plein_ecran(self, event):
        if not self.IsFullScreen():
            style = wx.FULLSCREEN_ALL
        else:
            style = wx.FULLSCREEN_NOBORDER
        self.ShowFullScreen(not self.IsFullScreen(), style)

    def Show(self, value=True):
        self._timer.Start(self.grille_duree_affichage)
        self.ticker.Start()
        wx.Dialog.Show(self, value)

    def stop_timer(self, event):
        self._timer.Stop()
        self.ticker.Stop()
        event.Skip()

    def echappe(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE and self.IsFullScreen():
            self.plein_ecran(event)

    def configurer(self, affichage_options):
        self.dimension_auto = affichage_options['DIMENSION_AUTO']

        # Message défilant
        self.message = affichage_options['MESSAGE']
        self.message_visible = affichage_options['MESSAGE_VISIBLE']
        self.message_vitesse = affichage_options['MESSAGE_VITESSE']
        if type(affichage_options['MESSAGE_POLICE']) == wx.Font:
            self.message_police = affichage_options['MESSAGE_POLICE']
        else:
            self.message_police = string_en_wxFont(affichage_options['MESSAGE_POLICE'])
        if type(affichage_options['MESSAGE_COULEUR']) == wx.Colour:
            self.message_couleur = affichage_options['MESSAGE_COULEUR']
        else:
            self.message_couleur = wx.Colour(*affichage_options['MESSAGE_COULEUR'])

        # Texte des interludes
        self.texte_inscription = affichage_options['TEXTE_INSCRIPTION']
        self.texte_tirage = affichage_options['TEXTE_TIRAGE']
        if type(affichage_options['TEXTE_POLICE']) == wx.Font:
            self.texte_police = affichage_options['TEXTE_POLICE']
        else:
            self.texte_police = string_en_wxFont(affichage_options['TEXTE_POLICE'])
        if type(affichage_options['TEXTE_COULEUR']) == wx.Colour:
            self.texte_couleur = affichage_options['TEXTE_COULEUR']
        else:
            self.texte_couleur = wx.Colour(*affichage_options['TEXTE_COULEUR'])

        # Titre des grilles
        if type(affichage_options['TITRE_POLICE']) == wx.Font:
            self.titre_police = affichage_options['TITRE_POLICE']
        else:
            self.titre_police = string_en_wxFont(affichage_options['TITRE_POLICE'])
        if type(affichage_options['TITRE_COULEUR']) == wx.Colour:
            self.titre_couleur = affichage_options['TITRE_COULEUR']
        else:
            self.titre_couleur = wx.Colour(*affichage_options['TITRE_COULEUR'])

        # Grilles
        self.grille_lignes = affichage_options['GRILLE_LIGNES']
        if type(affichage_options['GRILLE_POLICE']) == wx.Font:
            self.grille_police = affichage_options['GRILLE_POLICE']
        else:
            self.grille_police = string_en_wxFont(affichage_options['GRILLE_POLICE'])
        self.grille_duree_affichage = affichage_options['GRILLE_DUREE_AFFICHAGE']
        self.grille_temps_defilement = affichage_options['GRILLE_TEMPS_DEFILEMENT']
        self.grille_defilement_vertical = affichage_options['GRILLE_DEFILEMENT_VERTICAL']
