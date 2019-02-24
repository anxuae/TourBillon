#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import sys, os

import wx
from wx import grid
from  wx.lib import scrolledpanel as scrolled

from tourbillon import images
from tourbillon.trb_core import constantes as cst
from tourbillon.trb_core import equipes, parties
from tourbillon.trb_core import exceptions as expt

#--- Variables globales --------------------------------------------------------

TITRES = [(u"Equipe", 50),
          (u"Noms", 300),
          (u"Etat", 50),
          (u"Score", 50),
          (u"Durée", 80),
          (u"", 70),
          (u"Victoires", 70),
          (u"Points", 70),
          (u"Classement", 70),
          (u"min Billons", 80),
          (u"max Billons", 80),
          (u"moy Billons", 80),
          (u"min Durée", 80),
          (u"max Durée", 80),
          (u"moy Durée", 80)]

#--- Fonctions -----------------------------------------------------------------

def etat_style(valeur):
    police = wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD)
    couleur = images.couleur(valeur)

    if valeur == cst.FORFAIT:
        texte = u"F"
    elif valeur == cst.CHAPEAU:
        texte = u"C"
    elif valeur == cst.GAGNE:
        texte = u"G"
    elif valeur == cst.PERDU:
        texte = u"P"
    else:
        texte = u""

    return texte, couleur, police

def points_style(valeur):
    couleur = wx.Color(0, 0, 255)
    police = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)

    if valeur == None:
        texte = u""
    else:
        texte = unicode(valeur)

    return texte, couleur, police

def duree_style(valeur):
    couleur = wx.Color(0, 0, 0)
    police = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)

    if valeur == None:
        texte = u""
    else:
        texte = unicode_timedelta(valeur)

    return texte, couleur, police

def unicode_timedelta(timedelta):
    jours = timedelta.days
    heures, reste = divmod(timedelta.seconds, 3600)
    minutes, secondes = divmod(reste, 60)
    if jours == 0:
        return u'%02d:%02d:%02d' % (heures, minutes, secondes)
    else:
        return u'%sj %02d:%02d:%02d' % (jours, heures, minutes, secondes)

#--- Classes -------------------------------------------------------------------

class Grille(grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, wx.ID_ANY)
        self.CreateGrid(2, 15)

        # Selection précédente
        self.selection_prec = 0

        # Propriétés générales de la gille
        self.SetDefaultCellBackgroundColour(images.couleur('grille'))
        self.SetGridLineColour(images.couleur('grille'))
        self.SetColMinimalAcceptableWidth(0)
        self.SetColLabelSize(0)            # Supprimer ligne d'entête
        self.SetRowLabelSize(0)            # Supprimer colonne d'entête

        # Création de l'entête: 1ème ligne
        self.SetRowSize(0, 30)
        self.SetRowAttr(0, self.attribut('entete1'))
        self.SetCellSize(0, 6, 1, 9)    # Cellule fusionnée
        self.SetCellValue(0, 6, u"Informations générales")

        # Création de l'entête: 2ème ligne
        self.SetRowSize(1, 35)
        self.SetRowAttr(1, self.attribut('entete2'))
        self.SetColAttr(5, self.attribut('espace'))

        colonne = 0
        for titre, largeur in TITRES:
            if colonne < 6:
                ligne = 0
                self.SetCellSize(0, colonne, 2, 1)
            else:
                ligne = 1

            self.SetCellValue(ligne, colonne, titre)
            self.SetColSize(colonne, largeur)
            colonne += 1

        self.EnableDragColSize(False)
        self.EnableDragRowSize(False)
        self.Layout()

        # Evénements
        self.Bind(grid.EVT_GRID_CELL_LEFT_CLICK, self.selectionner)
        self.Bind(wx.EVT_KEY_DOWN, self._touche)

    def _rafraichir_couleur(self):
        i = 2
        self.Freeze()
        while i < self.GetNumberRows():
            if i % 2 == 0:
                self.SetRowAttr(i, self.attribut('paire'))
            else:
                self.SetRowAttr(i, self.attribut('impaire'))
            i += 1

        self.SetColAttr(5, self.attribut('espace'))

        self.Thaw()
        self.Refresh()

    def _touche(self, event):
        if event.GetKeyCode() == wx.WXK_DOWN:
            event.GetRow = lambda:self.GetGridCursorRow() + 1
            self.selectionner(event)
            event.Skip()
        elif event.GetKeyCode() == wx.WXK_UP:
            event.GetRow = lambda:self.GetGridCursorRow() - 1
            self.selectionner(event)
            event.Skip()
        else:
            event.Skip()

    def selectionner(self, event):
        if self.selection_prec != event.GetRow() and self.selection_prec > 1:
            # Restaurer le style original
            if self.selection_prec % 2 == 0:
                self.SetRowAttr(self.selection_prec, self.attribut('paire'))
            else:
                self.SetRowAttr(self.selection_prec, self.attribut('impaire'))
            self.Refresh()

        self.selection_prec = event.GetRow()

        if self.selection_prec > 1:
            # Appliquer le style de selection si la ligne n'est pas l'entête
            self.SetRowAttr(self.selection_prec, self.attribut('selection'))
            self.Refresh()
        event.Skip()

    def attribut(self, ref = 'paire'):
        attr = wx.grid.GridCellAttr()
        if ref == 'paire':
            attr.SetBackgroundColour(images.couleur('grille_paire'))
            attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        elif ref == 'impaire':
            attr.SetBackgroundColour(images.couleur('grille_impaire'))
            attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        elif ref == 'selection':
            attr.SetBackgroundColour(images.couleur('selection'))
            attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        elif ref == 'espace':
            attr.SetBackgroundColour(images.couleur('grille'))
            attr.SetAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        elif ref == 'entete1':
            attr.SetBackgroundColour(images.couleur('gradient1'))
            attr.SetTextColour(images.couleur('texte'))
            attr.SetFont(wx.Font(16, wx.ROMAN, wx.ITALIC, wx.BOLD))
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        elif ref == 'entete2':
            attr.SetBackgroundColour(images.couleur('gradient1'))
            attr.SetTextColour(images.couleur('texte'))
            attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetReadOnly(True)
        return attr

class GrillePanel(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent, wx.ID_ANY, style = wx.TAB_TRAVERSAL)
        self._colonne_recherche = 0
        self.grille = Grille(self)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.grille, 1, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 20)
        self.SetSizer(box)

        self.SetAutoLayout(True)
        self.SetupScrolling(scrollToTop = False)

        self.grille.Bind(wx.EVT_MOUSEWHEEL, self.teste)

    def teste(self, event):
        event.SetId(self.GetId())
        wx.PostEvent(self, event)
        event.Skip()

    def OnChildFocus(self, event):
        self.SetFocus()
        event.Skip()

    def _rafraichir(self, partie = None, equipe = None, classement = None):
        """
        NE PAS UTILISER !!!!! (Manipulé par la fenêtre principale)
        """
        self.grille.Freeze()
        if partie == 0:
            # Vider la partie
            l = 2
            while l < self.grille.GetNumberRows():
                self.grille.SetCellValue(l, 2, u"")
                self.grille.SetCellValue(l, 3, u"")
                self.grille.SetCellValue(l, 4, u"")
                l += 1

        if classement is not None:
            # Classement
            if classement == []:
                l = 2
                while l < self.grille.GetNumberRows():
                    self.grille.SetCellValue(l, 8, u"")
                    l += 1
            else:
                for eq, place in classement:
                    l = self.ligne(eq)
                    self.grille.SetCellValue(l, 8, u"%s" % place)

        if equipe is not None and partie is not None:
            l = self.ligne(equipe)
            # Numero
            self.grille.SetCellValue(l, 0, u"%s" % equipe.numero)
            self.grille.SetCellFont(l, 0, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            # Noms
            noms = [unicode(joueur) for joueur in equipe.joueurs()]
            noms = " / ".join(noms)
            self.grille.SetCellValue(l, 1, u"%s" % noms)
            # Etat
            try:
                texte, couleur, police = etat_style(equipe.resultat(partie)['etat'])
                self.grille.SetCellTextColour(l, 2, couleur)
                self.grille.SetCellFont(l, 2, police)
            except expt.NumeroError, e:
                texte = u""
            self.grille.SetCellValue(l, 2, u"%s" % texte)
            # Point
            try:
                texte, couleur, police = points_style(equipe.resultat(partie)['points'])
                self.grille.SetCellTextColour(l, 3, couleur)
                self.grille.SetCellFont(l, 3, police)
            except expt.NumeroError, e:
                texte = u""
            self.grille.SetCellValue(l, 3, u"%s" % texte)
            # Durée
            try:
                texte, couleur, police = duree_style(equipe.resultat(partie)['duree'])
                self.grille.SetCellTextColour(l, 4, couleur)
                self.grille.SetCellFont(l, 4, police)
            except expt.NumeroError, e:
                texte = u""
            self.grille.SetCellValue(l, 4, u"%s" % texte)
            # Victoires
            self.grille.SetCellValue(l, 6, u"%s" % (equipe.total_victoires() + equipe.total_chapeaux()))
            # Points
            self.grille.SetCellValue(l, 7, u"%s" % equipe.total_points())
            # Statistiques
            self.grille.SetCellValue(l, 9, u"%s" % equipe.min_billon())
            self.grille.SetCellValue(l, 10, u"%s" % equipe.max_billon())
            self.grille.SetCellValue(l, 11, u"%s" % equipe.moyenne_billon())
            self.grille.SetCellValue(l, 12, u"%s" % unicode_timedelta(equipe.min_duree()))
            self.grille.SetCellValue(l, 13, u"%s" % unicode_timedelta(equipe.max_duree()))
            self.grille.SetCellValue(l, 14, u"%s" % unicode_timedelta(equipe.moyenne_duree()))

#            # Indication équipe incomplète
#            if equipe.resultat(partie)['etat'] == None:
#                self.grille.SetCellValue(l, 5, u"*")
#            else:
#                self.grille.SetCellValue(l, 5, u"")

        self.grille.Thaw()

    def rechercher(self, event, precedent = -1):
        i = 2
        trouve = False
        trouve_avant_precedent = -1
        texte = event.GetString().strip()

        while i < self.grille.GetNumberRows():
            if  texte.lower() in self.grille.GetCellValue(i, self._colonne_recherche).lower() and texte != u'':
                if  i <= precedent:
                    if trouve_avant_precedent == -1:
                       trouve_avant_precedent = i
                else:
                    trouve = True
                    break
            i += 1

        if not trouve:
            if precedent == -1:
                self.Scroll(0, 0)
                i = 0
            else:
                if trouve_avant_precedent == -1:
                    i = precedent
                else:
                    i = trouve_avant_precedent

        event = grid.GridEvent(self.grille.GetId(), 10209, self.grille, row = i)
        event.GetRect = lambda:self.grille.CellToRect(i, 0)

        self.grille.selectionner(event)
        self.ScrollChildIntoView(event)

    def rechercher_suivant(self, event):
        if event.GetString().strip() == u"":
            precedent = -1
        else:
            precedent = self.grille.selection_prec
        self.rechercher(event, precedent)

    def chg_recherche_colonne(self, event):
        if event.index >= 5:
            event.index += 1
        self._colonne_recherche = event.index

    def ligne(self, equipe):
        """
        Recherche de l'indice de ligne de l'équipe par dichotomie.
        (Il est important que que la grille soit triée par ordre
        croissant de numéro d'équipe')
        """
        debut, fin = 2, self.grille.GetNumberRows() - 1
        while debut <= fin :
            milieu = (debut + fin) / 2
            num = int(self.grille.GetCellValue(milieu, 0))
            if  num == equipe.numero :
                # L'élément du milieu de l'intervalle [debut, fin] correspond
                return milieu
            elif num > equipe.numero:
                # Recherche avant le milieu
                fin = milieu - 1
            else :
                # Recherche après le milieu
                debut = milieu + 1
        return None

    def nb_lignes(self):
        return self.grille.GetNumberRows()

    def selection(self):
        if self.grille.selection_prec < 2:
            return None
        else:
            return self.grille.GetCellValue(self.grille.selection_prec, 0)

    def ajout_equipe(self, equipe):
        i = 2
        while i < self.grille.GetNumberRows():
            if int(self.grille.GetCellValue(i, 0)) > equipe.numero:
                break
            i += 1

        self.grille.InsertRows(i, 1, False)
        self.grille.SetRowSize(i, 20)

        # Le numéro qui permet de retrouver la ligne de l'équipe
        self.grille.SetCellValue(i, 0, u"%s" % equipe.numero)
        self.grille._rafraichir_couleur()
        self.SetupScrolling(scrollToTop = False)

    def suppr_equipe(self, equipe):
        self.grille.DeleteRows(self.ligne(equipe), 1, False)
        self.grille._rafraichir_couleur()
        self.SetupScrolling(scrollToTop = False)

    def effacer(self):
        if self.grille.GetNumberRows() > 2:
            self.grille.DeleteRows(2, self.grille.GetNumberRows(), False)
