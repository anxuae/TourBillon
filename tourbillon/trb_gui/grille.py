#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import sys, os
import datetime
from functools import partial

import wx
from wx import grid
from  wx.lib import scrolledpanel as scrolled

from tourbillon import images
from tourbillon.trb_core import constantes as cst
from tourbillon.trb_core import equipe, partie
from tourbillon.trb_core import exceptions as expt

#--- Variables globales --------------------------------------------------------

TITRES = {'partie':      [(u"Equipe", 60),
                          (u"Noms", 300),
                          (u"Etat", 50),
                          (u"Score", 50),
                          (u"Durée", 80)],

          'statistiques':[(u"Victoires", 70),
                          (u"Points", 70),
                          (u"Place", 70),
                          (u"min Billons", 80),
                          (u"max Billons", 80),
                          (u"moy Billons", 80),
                          (u"min Durée", 80),
                          (u"max Durée", 80),
                          (u"moy Durée", 80)]}

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

class Grille(wx.BoxSizer):
    """
    BoxSizer contenant les deux grilles utilisées pour afficher
    les informations de la partie en cours et du tournoi.
    """
    def __init__(self, parent):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)

        # Initialisation de la grille de resumé de partie
        self._grille_partie = wx.grid.Grid(parent, wx.ID_ANY)
        self._grille_partie.CreateGrid(2, 5)
        self._grille_partie.nom = 'partie'
        self.Add(self._grille_partie)

        # Espace entre grilles
        self.AddSpacer((50, 50), 1)

        # Initialisation de la grille des statistiques du tournoi
        self._grille_statistiques = wx.grid.Grid(parent, wx.ID_ANY)
        self._grille_statistiques.CreateGrid(2, 9)
        self._grille_statistiques.nom = 'statistiques'
        self.Add(self._grille_statistiques)

        self._grilles = [self._grille_partie, self._grille_statistiques]

        # Selection précédente
        self.selection_prec = 0

        # Propriétés générales des gilles
        for grille in self._grilles:
            grille.SetDefaultCellBackgroundColour(images.couleur('grille'))
            grille.SetGridLineColour(images.couleur('grille'))
            grille.SetColMinimalAcceptableWidth(0)
            grille.EnableDragColSize(False)
            grille.EnableDragRowSize(False)
            # Supprimer ligne d'entête
            grille.SetColLabelSize(0)
            # Supprimer colonne d'entête
            grille.SetRowLabelSize(0)
            # Création de l'entête: 1ème ligne
            grille.SetRowSize(0, 30)
            grille.SetRowAttr(0, self.attribut('entete1'))
            # Création de l'entête: 2ème ligne
            grille.SetRowSize(1, 35)
            grille.SetRowAttr(1, self.attribut('entete2'))
            colonne = 0
            for titre, largeur in TITRES[grille.nom]:
                if grille.nom == 'partie':
                    ligne = 0
                    grille.SetCellSize(0, colonne, 2, 1)
                else:
                    ligne = 1
                grille.SetCellValue(ligne, colonne, titre)
                grille.SetColSize(colonne, largeur)
                colonne += 1
            # Evénements
            grille.Bind(grid.EVT_GRID_CELL_LEFT_CLICK, self.selectionner)
            grille.Bind(wx.EVT_KEY_DOWN, partial(self._touche, grille=grille))

        # Cellule fusionnée
        self._grille_statistiques.SetCellSize(0, 0, 1, 9)
        self._grille_statistiques.SetCellValue(0, 0, u"Statistiques du tournoi")

        self.Layout()

    def Bind(self, *args, **kwrds):
        for grille in self._grilles:
            grille.Bind(*args, **kwrds)

    def Freeze(self):
        for grille in self._grilles:
            grille.Freeze()

    def Thaw(self):
        for grille in self._grilles:
            grille.Thaw()

    def Refresh(self):
        for grille in self._grilles:
            grille.Refresh()

    def InsertRows(self, pos, numRows=1, updateLabels=False):
        """
        Appelé depuis l'exterieur de l'objet. (Prend en compte l'entête)
        """
        for grille in self._grilles:
            grille.InsertRows(pos + 2, numRows, updateLabels)
            grille.SetRowSize(pos + 2, 20)
        self._rafraichir()

    def GetNumberRows(self):
        """
        Appelé depuis l'exterieur de l'objet. (Prend en compte l'entête)
        """
        return self._grille_partie.GetNumberRows() - 2

    def DeleteRows(self, pos, numRows=1, updateLabels=False):
        """
        Appelé depuis l'exterieur de l'objet. (Prend en compte l'entête)
        """
        for grille in self._grilles:
            grille.DeleteRows(pos + 2, numRows, updateLabels)
        self._rafraichir()

    def CellToRect(self, row, col):
        """
        Appelé depuis l'exterieur de l'objet. (Prend en compte l'entête)
        """
        if col < 5:
            return self._grille_partie.CellToRect(row + 2, col)
        else:
            return self._grille_statistiques.CellToRect(row + 2, col - 5)

    def GetCellValue(self, row, col):
        """
        Appelé depuis l'exterieur de l'objet. (Prend en compte l'entête)
        """
        if col < 5:
            return self._grille_partie.GetCellValue(row + 2, col)
        else:
            return self._grille_statistiques.GetCellValue(row + 2, col - 5)

    def SetCellValue(self, row, col, value):
        """
        Appelé depuis l'exterieur de l'objet. (Prend en compte l'entête)
        """
        texte = value
        if col == 0:
            self._grille_partie.SetCellFont(row + 2, col, wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        elif col == 2 and texte not in [None, u""]:
            texte, couleur, police = etat_style(texte)
            self._grille_partie.SetCellTextColour(row + 2, col, couleur)
            self._grille_partie.SetCellFont(row + 2, col, police)
        elif col == 3 and texte not in [None, u""]:
            texte, couleur, police = points_style(texte)
            self._grille_partie.SetCellTextColour(row + 2, col, couleur)
            self._grille_partie.SetCellFont(row + 2, col, police)
        elif col == 4 and texte not in [None, u""]:
            texte, couleur, police = duree_style(texte)
            self._grille_partie.SetCellTextColour(row + 2, col, couleur)
            self._grille_partie.SetCellFont(row + 2, col, police)

        if type(texte) == datetime.timedelta:
            texte = unicode_timedelta(texte)
        elif texte is None:
            texte = u""

        if col < 5:
            self._grille_partie.SetCellValue(row + 2, col, unicode(texte))
        else:
            self._grille_statistiques.SetCellValue(row + 2, col - 5, unicode(texte))

    def GetGridEvent(self, row, col):
        """
        Appelé depuis l'exterieur de l'objet. (Prend en compte l'entête)
        """
        r = row + 2
        if col < 5:
            g = self._grille_partie
            c = col
        else:
            g = self._grille_statistiques
            c = col - 5
        event = grid.GridEvent(g.GetId(), 10209, g, row=r, col=c)
        event.GetRect = lambda:g.CellToRect(r, c)
        return event

    def GetSelectedRows(self):
        """
        Appelé depuis l'exterieur de l'objet. (Prend en compte l'entête)
        """
        return self.selection_prec - 2

    def _rafraichir(self):
        i = 2
        self.Freeze()
        while i < self._grille_partie.GetNumberRows():
            for grille in self._grilles:
                if i % 2 == 0:
                    grille.SetRowAttr(i, self.attribut('paire'))
                else:
                    grille.SetRowAttr(i, self.attribut('impaire'))
            i += 1
        self.Thaw()
        self.Refresh()

    def _touche(self, event, grille):
        """
        Déplacer la selection via les touches BAS et HAUT
        du clavier.
        """
        valeur = grille.GetGridCursorRow()
        if event.GetKeyCode() == wx.WXK_DOWN:
            if valeur < grille.GetNumberRows() - 1:
                valeur += 1
        elif event.GetKeyCode() == wx.WXK_UP:
            valeur -= 1
        else:
            event.Skip()
            return
        event.GetRow = lambda:valeur
        self.selectionner(event)
        event.Skip()

    def ligne(self, numero):
        """
        Recherche de l'indice de ligne de l'équipe par dichotomie.
        (Il est important que que la grille soit triée par ordre
        croissant de numéro d'équipe')
        Appelé depuis l'exterieur de l'objet. (Prend en compte l'entête)
        
        numero (int)   : numéro recherché dans le première colonne
        """
        debut, fin = 2, self._grille_partie.GetNumberRows() - 1
        while debut <= fin :
            milieu = (debut + fin) / 2
            num = int(self._grille_partie.GetCellValue(milieu, 0))
            if  num == numero :
                # L'élément du milieu de l'intervalle [debut, fin] correspond
                return milieu - 2
            elif num > numero:
                # Recherche avant le milieu
                fin = milieu - 1
            else :
                # Recherche après le milieu
                debut = milieu + 1
        return None

    def afficher_statistiques(self, valeur):
        """
        Afficher/Masquer la grille des statistiques.
        """
        self._grille_statistiques.Show(valeur)
        self.GetChildren()[1].Show(valeur)

    def selectionner(self, event):
        # Deselectionner la selection courrante
        for grille in self._grilles:
            if self.selection_prec != event.GetRow() and self.selection_prec > 1:
                if self.selection_prec % 2 == 0:
                    grille.SetRowAttr(self.selection_prec, self.attribut('paire'))
                else:
                    grille.SetRowAttr(self.selection_prec, self.attribut('impaire'))
                grille.Refresh()

        # Appliquer le style de selection si la ligne n'est pas l'entête
        for grille in self._grilles:
            self.selection_prec = event.GetRow()
            if self.selection_prec > 1:
                grille.SetRowAttr(self.selection_prec, self.attribut('selection'))
                grille.Refresh()

        event.Skip()

    def attribut(self, ref='paire'):
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
        elif ref == 'entete1':
            attr.SetBackgroundColour(images.couleur('gradient1'))
            attr.SetTextColour(images.couleur('texte'))
            attr.SetFont(wx.Font(14, wx.ROMAN, wx.ITALIC, wx.BOLD))
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
    def __init__(self, parent, fond):
        scrolled.ScrolledPanel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self._colonne_recherche = 0
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.chg_fond(fond)

        self.grille = Grille(self)
        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSpacer((1, 20), 0, wx.ALL)
        box.Add(self.grille, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 20)
        self.SetSizer(box)

        self.SetAutoLayout(True)
        self.SetupScrolling(scrollToTop=False)

        self.grille.Bind(wx.EVT_MOUSEWHEEL, self._roulette)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.dessiner_fond)

    def _roulette(self, event):
        x, y = self.GetViewStart()
        sens = event.GetWheelRotation() / abs(event.GetWheelRotation())
        self.Scroll(x, y - (self.GetScaleY() * sens))

    def chg_fond(self, bmp):
        """
        Modifier l'image du fond.
        """
        sz = wx.GetDisplaySize()
        self._fond = images.scale_bitmap(bmp, sz.width, sz.height)
        self.Refresh()

    def dessiner_fond(self, event):
        """
        Ajouter une imagne en fond d'écran.
        """
        dc = event.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.DrawBitmap(self._fond, 0, 0)
        event.Skip()

    def OnChildFocus(self, event):
        self.SetFocus()
        event.Skip()

    def _rafraichir(self, partie=None, equipe=None, classement=None, partie_limite=None):
        """
        NE PAS UTILISER !!!!! (Manipulé par la fenêtre principale)
        """
        self.grille.Freeze()

        # Vider les info de la partie
        if partie == 0:
            i = 0
            while i < self.grille.GetNumberRows():
                self.grille.SetCellValue(i, 2, u"")
                self.grille.SetCellValue(i, 3, u"")
                self.grille.SetCellValue(i, 4, u"")
                i += 1

        # MAJ du classement Classement
        if classement is not None:
            if classement == []:
                i = 0
                while i < self.grille.GetNumberRows():
                    self.grille.SetCellValue(i, 7, u"")
                    i += 1
            else:
                for eq, place in classement:
                    i = self.grille.ligne(eq.numero)
                    self.grille.SetCellValue(i, 7, u"%s" % place)

        if equipe is not None and partie is not None:
            ligne = self.grille.ligne(equipe.numero)
            # Numero
            self.grille.SetCellValue(ligne, 0, equipe.numero)
            # Noms
            noms = [unicode(joueur) for joueur in equipe.joueurs()]
            noms = u" / ".join(noms)
            self.grille.SetCellValue(ligne, 1, noms)
            # Etat
            if equipe.partie_existe(partie):
                texte = equipe.resultat(partie).etat
            else:
                texte = ''
            self.grille.SetCellValue(ligne, 2, texte)
            # Point
            if equipe.partie_existe(partie):
                texte = equipe.resultat(partie).points
            else:
                texte = ''
            self.grille.SetCellValue(ligne, 3, texte)
            # Durée
            if equipe.partie_existe(partie):
                texte = equipe.resultat(partie).duree
            else:
                texte = ''
            self.grille.SetCellValue(ligne, 4, texte)

            # Victoires
            self.grille.SetCellValue(ligne, 5, (equipe.total_victoires(partie_limite) + equipe.total_chapeaux(partie_limite)))
            # Points
            self.grille.SetCellValue(ligne, 6, equipe.total_points(partie_limite))
            # Statistiques
            self.grille.SetCellValue(ligne, 8, equipe.min_billon(partie_limite))
            self.grille.SetCellValue(ligne, 9, equipe.max_billon(partie_limite))
            self.grille.SetCellValue(ligne, 10, equipe.moyenne_billon(partie_limite))
            self.grille.SetCellValue(ligne, 11, equipe.min_duree(partie_limite))
            self.grille.SetCellValue(ligne, 12, equipe.max_duree(partie_limite))
            self.grille.SetCellValue(ligne, 13, equipe.moyenne_duree(partie_limite))

        self.grille.Thaw()

    def rechercher(self, event, precedent= -1):
        """
        Rechercher une chaine de caractère dans la colonne au
        préalablement selectionnée via 'chg_recherche_colonne'.
        Si la précedente ligne trouvée est spécifiée, la recherche
        débutera à partir de la ligne suivante.
        
        precedent (int)
        """
        i = 0
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

        event = self.grille.GetGridEvent(i, 0)
        self.grille.selectionner(event)
        self.ScrollChildIntoView(event)

    def rechercher_suivant(self, event):
        """
        Recherche la prochaine occurence du texte entré
        dans le champ de recherche.
        """
        if event.GetString().strip() == u"":
            precedent = -1
        else:
            precedent = self.grille.GetSelectedRows()
        self.rechercher(event, precedent)

    def chg_recherche_colonne(self, event):
        """
        Modifier la colonne de recherche.
        """
        self._colonne_recherche = event.index

    def selection(self):
        """
        Retourne le numéro d'équipe selectionné, ou à défaut, la
        première équipe non chapeau et non forfait de la grille.
        """
        if self.grille.GetSelectedRows() < 0:
            for i in range(0, self.grille.GetNumberRows()):
                etat = self.grille.GetCellValue(i, 2)
                if etat not in ['C', 'F'] :
                    return int(self.grille.GetCellValue(i, 0))
        else:
            return int(self.grille.GetCellValue(self.grille.GetSelectedRows(), 0))

    def ajout_equipe(self, equipe):
        """
        Ajouter une nouvelle équipe.
        """
        i = 0
        while i < self.grille.GetNumberRows():
            if int(self.grille.GetCellValue(i, 0)) > equipe.numero:
                break
            i += 1

        self.grille.InsertRows(i, 1, False)
        self.grille.SetCellValue(i, 0, u"%s" % equipe.numero)
        self.SetupScrolling(scrollToTop=False)

    def suppr_equipe(self, equipe):
        """
        Suprimer une équipe.
        """
        self.grille.DeleteRows(self.grille.ligne(equipe.numero), 1, False)
        self.grille._rafraichir_couleur()
        self.SetupScrolling(scrollToTop=False)

    def afficher_statistiques(self, valeur=True):
        """
        Afficher/Masquer la grille des statistiques.
        
        valeur (bool)
        """
        self.grille.afficher_statistiques(valeur)
        self.Layout()

    def effacer(self):
        """
        Effacer toutes les lignes.
        """
        if self.grille.GetNumberRows() > 0:
            self.grille.DeleteRows(0, self.grille.GetNumberRows(), False)
        self.Layout()
