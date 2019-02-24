#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import sys, os
import time
import wx
import  wx.wizard as wiz
from wx import grid
from wx.lib.mixins import listctrl
from wx.lib.wordwrap import wordwrap

from tourbillon.trb_gui import evenements as evt

from tourbillon import images
from tourbillon.trb_core import constantes as cst
from tourbillon.trb_core import tournois
from tourbillon.trb_core.tirages import utile
from tourbillon.trb_core import tirages

#--- Function ------------------------------------------------------------------

def ajout_page_titre(wizPg, titre):
    sizer = wx.BoxSizer(wx.VERTICAL)
    wizPg.SetSizer(sizer)

    title = wx.StaticText(wizPg, wx.ID_ANY, titre)
    title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

    msg = BandeTexte(wizPg)

    sizer.Add(title, 0, wx.ALL, 5)
    sizer.Add(msg, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
    sizer.Add(wx.StaticLine(wizPg, wx.ID_ANY), 0, wx.EXPAND | wx.ALL, 0)
    return sizer, msg

#--- Fenêtre de suppression de partie ------------------------------------------

class DialogueSupprimerPartie(wx.Dialog):
    def __init__(self, parent, choix = [], numero_affiche = 1):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title = u"Supprimer une partie" , style = wx.DEFAULT_DIALOG_STYLE | wx.CENTER_ON_SCREEN, pos = wx.DefaultPosition, size = wx.DefaultSize)
        self.SetMinSize((500, 150))
        self.SetSize(wx.Size(500, 140))
        self.CenterOnParent()

        self.txt_phrase0 = wx.StaticText(self, wx.ID_ANY, u"Etes vous sûr de vouloir supprimer la partie n° ")
        self.ctl_numero = wx.Choice(self, wx.ID_ANY, choices = map(unicode, choix))
        self.txt_phrase1 = wx.StaticText(self, wx.ID_ANY, u" ?")
        self.txt_phrase2 = wx.StaticText(self, wx.ID_ANY, u"(Attention, toutes les données de la partie seront supprimées)")
        self.ctl_numero.SetSelection(self.ctl_numero.FindString(unicode(numero_affiche)))

        # Choix
        box_chx = wx.BoxSizer(wx.HORIZONTAL)
        box_chx.Add(self.txt_phrase0, 0, wx.ALIGN_CENTER_VERTICAL)
        box_chx.Add(self.ctl_numero, 0, wx.ALIGN_CENTER_VERTICAL)
        box_chx.Add(self.txt_phrase1, 0, wx.ALIGN_CENTER_VERTICAL)

        # Boutons
        self.btn_ok = wx.Button(self, id = wx.ID_OK, label = u"Supprimer", size = (100, -1))
        self.btn_annule = wx.Button(self, id = wx.ID_CANCEL, label = u"Annuler", size = (100, -1))
        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        box_btn.AddSpacer((50, 50), 1, wx.EXPAND)
        box_btn.Add(self.btn_annule, 0, wx.EAST | wx.ALIGN_CENTER_VERTICAL, 30)
        box_btn.Add(self.btn_ok, 0, wx.EAST | wx.ALIGN_CENTER_VERTICAL, 15)

        # Assembler
        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSizer(box_chx, 1, wx.LEFT, 30)
        box.Add(self.txt_phrase2, 1, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 30)
        box.AddSizer(box_btn, 0, wx.EXPAND)
        self.SetSizer(box)
        self.Layout()

    def chg_numero(self, numero):
        numero = unicode(numero)
        self.ctl_numero.SetSelection(self.ctl_numero.FindString(numero))

    def numero(self):
        return self.ctl_numero.GetString(self.ctl_numero.GetSelection())

class DialogueAfficherTirage(wx.Dialog):
    def __init__(self, parent, numero_affiche = 1):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title = u"Tirages" , style = wx.DEFAULT_DIALOG_STYLE | wx.CENTER_ON_SCREEN | wx.RESIZE_BORDER | wx.STAY_ON_TOP)
        self.CenterOnParent()

        self.txt_phrase = wx.StaticText(self, wx.ID_ANY, u"Tirage de la partie n° ")
        self.ctl_numero = wx.Choice(self, wx.ID_ANY, choices = [unicode(partie.numero) for partie in tournois.tournoi().parties()])
        self.ctl_numero.SetSelection(self.ctl_numero.FindString(unicode(numero_affiche)))

        # Choix
        box_chx = wx.BoxSizer(wx.HORIZONTAL)
        box_chx.Add(self.txt_phrase, 0, wx.ALIGN_CENTER_VERTICAL)
        box_chx.Add(self.ctl_numero, 0, wx.ALIGN_CENTER_VERTICAL)

        # Grille
        self.grille = grid.Grid(self)
        self.grille.CreateGrid(0, tournois.tournoi().equipes_par_manche)
        self.grille.SetColLabelSize(0)
        self.grille.SetRowLabelSize(0)

        # Boutons
        self.btn_ok = wx.Button(self, id = wx.ID_OK, label = u"Fermer", size = (100, -1))

        # Assembler
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(box_chx, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 20)
        self.sizer.Add(self.grille, 1, wx.ALIGN_CENTER)
        self.sizer.AddSizer((10, 10), 0, wx.EXPAND)
        self.sizer.Add(self.btn_ok, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 20)
        self.SetSizer(self.sizer)
        self.Layout()

        self._maj(None)
        self.Bind(wx.EVT_CHOICE, self._maj, self.ctl_numero)

    def _maj(self, event):
        tirage = tournois.tournoi().partie(int(self.ctl_numero.GetStringSelection())).tirage()
        if self.grille.GetNumberRows() > 0:
            self.grille.DeleteRows(0, self.grille.GetNumberRows(), False)

        i = 0
        while i < len(tirage):
            self.grille.InsertRows(i, 1, False)
            j = 0
            for num in tirage[i]:
                if num == cst.CHAPEAU:
                    num = u"C"
                self.grille.SetCellValue(i, j, unicode(num))
                j += 1
            i += 1

        if self.grille.GetNumberRows() < 30:
            self.Fit()

#--- Bande info pour wizard ----------------------------------------------------

class BandeTexte(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.SetMinSize(wx.Size(50, 22))

        self._info = images.bitmap('icon_info.png')
        self._erreur = images.bitmap('icon_erreur.png')
        self._attention = images.bitmap('icon_attention.png')
        self.btm_icon = wx.StaticBitmap(self, wx.ID_ANY, self._info)
        self.btm_icon.Hide()

        self.txt_message = wx.StaticText(self, wx.ID_ANY, u"")
        self.txt_message.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.btm_icon, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.txt_message, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        self.SetSizer(sizer)

    def chg_texte(self, texte, icon = None):
        texte = wordwrap(texte, 600, wx.ClientDC(self.txt_message))
        if icon == wx.ICON_ERROR:
            self.btm_icon.Show()
            self.btm_icon.SetBitmap(self._erreur)
        elif icon == wx.ICON_WARNING:
            self.btm_icon.Show()
            self.btm_icon.SetBitmap(self._attention)
        elif icon == wx.ICON_INFORMATION:
            self.btm_icon.Show()
            self.btm_icon.SetBitmap(self._info)
        else:
            self.btm_icon.Hide()

        self.txt_message.SetLabel(texte)
        self.Layout()
        self.Refresh()

    def texte(self):
        return self.txt_message.GetLabel()

#--- Liste cochable des équipes ------------------------------------------------

class ListeEquipesCtrl(wx.ListCtrl, listctrl.CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style = wx.LC_REPORT)
        listctrl.CheckListCtrlMixin.__init__(self)

        self.InsertColumn(0, "N°", wx.LIST_FORMAT_CENTRE)
        self.InsertColumn(1, "Noms", wx.LIST_FORMAT_LEFT)
        self.InsertColumn(2, "Victoires", wx.LIST_FORMAT_CENTRE)
        self.InsertColumn(3, "Points", wx.LIST_FORMAT_CENTRE)
        self.InsertColumn(4, "Chapeaux", wx.LIST_FORMAT_CENTRE)
        self.InsertColumn(5, "Classement", wx.LIST_FORMAT_CENTRE)

    def ajout_equipes(self, liste_equipes):
        selection = [int(self.GetItemText(i)) for i in range(self.GetItemCount()) if self.IsChecked(i)]
        self.DeleteAllItems()
        classement = {}
        classement.update(tournois.tournoi().classement())

        for num in liste_equipes:
            equipe = tournois.tournoi().equipe(int(num))
            self.Append([unicode(equipe.numero),
                         u", ".join([unicode(joueur) for joueur in equipe.joueurs()]),
                         unicode(equipe.total_victoires()),
                         unicode(equipe.total_points()),
                         unicode(equipe.total_chapeaux()),
                         unicode(classement[equipe])])
            # Cocher si l'équipe étaient cochées avant effacement
            if int(num) in selection:
                self.CheckItem(self.GetItemCount() - 1)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, 70)
        self.SetColumnWidth(3, 70)
        self.SetColumnWidth(4, 70)
        self.SetColumnWidth(5, 70)

        self.Refresh()

    def OnCheckItem(self, index, checked):
        self.GetEventHandler().ProcessEvent(evt.ListItemCheckedEvent(self.GetId(), index, checked))

#--- Grille des manches --------------------------------------------------------

class GrilleManchesCtrl(grid.Grid):
    def __init__(self, parent, equipes_par_manche, manches, chapeaux = []):
        grid.Grid.__init__(self, parent, wx.ID_ANY)

        # Nombre de lignes (1 par manche + 1 pour les chapeaux)
        self.equipes_par_manche = equipes_par_manche
        self.nbr_ligne = len(manches)
        if len(chapeaux) != 0:
            self.nbr_ligne += 1

        self.CreateGrid(self.nbr_ligne, self.equipes_par_manche + 1)

        # Format cellules equipe
        attr = wx.grid.GridCellAttr()
        attr.SetBackgroundColour(wx.Colour(255, 255, 255))
        attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
        attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Format cellules info
        attr_info = wx.grid.GridCellAttr()
        attr_info.SetBackgroundColour(wx.Colour(255, 255, 255))
        attr_info.SetTextColour(wx.Colour(255, 0, 0))
        attr_info.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))

        for i in range(self.GetNumberCols()):
            if i == self.GetNumberCols() - 1:
                self.SetColAttr(i, attr_info)
            else:
                self.SetColAttr(i, attr)
            self.SetColSize(i, 50)

        # Première ligne pour afficher les chapeaux
        i = 0
        j = 0
        if len(chapeaux) != 0:
            while j < self.equipes_par_manche:
                if j < len(chapeaux):
                    self.SetCellValue(i, j, unicode(chapeaux[j]))
                else:
                    self.SetCellValue(i, j, u"C")
                    self.SetCellTextColour(i, j, images.couleur(cst.CHAPEAU))
                j += 1
            i += 1

        # Afficher les manches
        for m in manches:
            j = 0
            for e in m:
                self.SetCellValue(i, j, unicode(e))
                j += 1
            i += 1

        # cases selectionnées
        self.select1 = None
        self.select2 = None

        #self.SetGridLineColour(wx.Colour(255, 255, 255))
        self.SetColMinimalAcceptableWidth(1)

        self.SetRowLabelSize(0)
        self.SetColLabelSize(0)
        self.EnableDragColSize(False)
        self.EnableDragRowSize(False)
        self.EnableEditing(False)

        self.Bind(grid.EVT_GRID_CELL_LEFT_CLICK, self._selection_equipe)

    def _selection_equipe(self, event):
        l, c = event.GetRow(), event.GetCol()
        if self.echangeable():
            # deselectionner les deux équipes selectionnées
            l1, c1 = self.select1
            l2, c2 = self.select2
            self._deselectionner(l1, c1)
            self._deselectionner(l2, c2)
            self.select1 = None
            self.select2 = None

        if (l, c) == self.select1:
            # deselectionner select1
            self._deselectionner(l, c)
            self.select1 = None
        elif (l, c) == self.select2:
            # deselectionner select2
            self._deselectionner(l, c)
            self.select2 = None
        elif self.select1 == None:
            if self.GetCellValue(l, c) != u"C" and c < self.equipes_par_manche:
                self.select1 = (l, c)
                self._selectionner(l, c)
        elif self.select2 == None:
            if self.GetCellValue(l, c) != u"C" and c < self.equipes_par_manche:
                self.select2 = (l, c)
                self._selectionner(l, c)
        self.Refresh()
        event.Skip()

    def _selectionner(self, ligne, colonne):
        self.SetCellBackgroundColour(ligne, colonne, wx.Colour(200, 6, 6))
        self.SetCellFont(ligne, colonne, wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))

    def _deselectionner(self, ligne, colonne):
        self.SetCellBackgroundColour(ligne, colonne, wx.Colour(255, 255, 255))
        self.SetCellFont(ligne, colonne, wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))

    def Layout(self):
        grid.Grid.Layout(self)
        # Largeur dernière colonne
        largeur = self.Size[0] - 15 - self.GetColSize(0) * self.equipes_par_manche
        if largeur < 200:
            largeur = 200
        self.SetColSize(self.equipes_par_manche, largeur)

    def chg_texte(self, ligne, texte):
        self.SetCellValue(ligne, self.equipes_par_manche, unicode(texte))

    def echangeable(self):
        return self.select1 is not None and self.select2 is not None

    def echanger(self):
        if self.echangeable():
            l1, c1 = self.select1
            l2, c2 = self.select2
            val1 = self.GetCellValue(l1, c1)
            val2 = self.GetCellValue(l2, c2)
            self.SetCellValue(l1, c1, val2)
            self.SetCellValue(l2, c2, val1)
            return (l1, c1), (l2, c2)

    def manche(self, ligne):
        m = []
        for j in range(self.GetNumberCols() - 1):
            valeur = self.GetCellValue(ligne, j)
            if valeur != u"C":
                valeur = int(valeur)
            m.append(valeur)
        return m

#--- Pages du Wizard -----------------------------------------------------------

class SelectionEquipesPage(wiz.PyWizardPage):
    def __init__(self, parent, title):
        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.sizer, self.txt_msg = ajout_page_titre(self, u"Selection des équipes")

        self.liste = ListeEquipesCtrl(self)
        self.liste.ajout_equipes(tournois.tournoi().equipes())
        self.liste.SetSize(wx.Size(600, 300))
        self._cocher_tout(None)

        self.btn_cocher_tout = wx.BitmapButton(self, wx.ID_ANY, images.bitmap('check_on.png'))
        self.btn_cocher_tout.SetToolTipString(u"Sélectionner toutes les équipes")
        self.btn_decocher_tout = wx.BitmapButton(self, wx.ID_ANY, images.bitmap('check_off.png'))
        self.btn_decocher_tout.SetToolTipString(u"Dessélectionner toutes les équipes")

        self.sizer.Add(self.liste, 1, wx.ALL, 5)

        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        box_btn.Add(self.btn_cocher_tout)
        box_btn.Add(self.btn_decocher_tout)

        self.sizer.AddSizer(box_btn, 0, wx.LEFT, 5)

        # Décocher les équipes forfait de la partie précédente
        if tournois.tournoi().partie_courante() is not None:
            forfaits = tournois.tournoi().partie_courante().forfaits()
        else:
            forfaits = []
        i = 0
        while i < self.liste.GetItemCount():
            if int(self.liste.GetItemText(i)) in forfaits:
                self.liste.CheckItem(i, False)
            i = i + 1

        self.Bind(wx.EVT_BUTTON, self._cocher_tout, self.btn_cocher_tout)
        self.Bind(wx.EVT_BUTTON, self._decocher_tout, self.btn_decocher_tout)
        self.Bind(evt.EVT_LIST_ITEM_CHECKED, self.verifier, self.liste)

    def _cocher_tout(self, event):
        i = 0
        while i < self.liste.GetItemCount():
            self.liste.CheckItem(i, True)
            i = i + 1

    def _decocher_tout(self, event):
        i = 0
        while i < self.liste.GetItemCount():
            self.liste.CheckItem(i, False)
            i = i + 1

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        if utile.nb_chapeaux_necessaires(len(self.equipes()), tournois.tournoi().equipes_par_manche) == 0:
            # Page tirage
            self.next.GetNext().SetPrev(self)
            return self.next.GetNext()
        else:
            # Page chapeaux
            self.next.GetNext().SetPrev(self.next)
            return self.next

    def GetPrev(self):
        return self.prev

    def equipes(self):
        liste = []
        i = 0
        while i < self.liste.GetItemCount():
            if self.liste.IsChecked(i) == True:
                liste.append(int(self.liste.GetItemText(i)))
            i = i + 1
        return liste

    def forfaits(self):
        liste = []
        i = 0
        while i < self.liste.GetItemCount():
            if self.liste.IsChecked(i) == False:
                liste.append(int(self.liste.GetItemText(i)))
            i = i + 1
        return liste

    def verifier(self, event):
        nextButton = self.GetParent().FindWindowById(wx.ID_FORWARD)
        if len(self.equipes()) < 3:
            self.txt_msg.chg_texte("Au minimum, 3 équipes doivent être séléctionnées.", wx.ICON_ERROR)
            nextButton.Disable()
        else:
            self.txt_msg.chg_texte("")
            nextButton.Enable()

        if event is not None:
            event.Skip()

class SelectionChapeauPage(wiz.PyWizardPage):
    def __init__(self, parent, title):
        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.sizer, self.txt_msg = ajout_page_titre(self, u"Selection des chapeaux")

        self.liste = ListeEquipesCtrl(self)
        self.liste.SetSize(wx.Size(600, 300))

        self.btn_cocher_tout = wx.BitmapButton(self, -1, images.bitmap('check_on.png'))
        self.btn_cocher_tout.SetToolTipString(u"Sélectionner toutes les équipes")
        self.btn_decocher_tout = wx.BitmapButton(self, -1, images.bitmap('check_off.png'))
        self.btn_decocher_tout.SetToolTipString(u"Dessélectionner toutes les équipes")

        self.sizer.Add(self.liste, 1, wx.ALL, 5)

        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        box_btn.Add(self.btn_cocher_tout)
        box_btn.Add(self.btn_decocher_tout)

        self.sizer.AddSizer(box_btn, 0, wx.LEFT, 5)

        self.Bind(wx.EVT_BUTTON, self._cocher_tout, self.btn_cocher_tout)
        self.Bind(wx.EVT_BUTTON, self._decocher_tout, self.btn_decocher_tout)
        self.Bind(evt.EVT_LIST_ITEM_CHECKED, self.verifier, self.liste)

    def _cocher_tout(self, event):
        i = 0
        while i < self.liste.GetItemCount():
            self.liste.CheckItem(i, True)
            i = i + 1

    def _decocher_tout(self, event):
        i = 0
        while i < self.liste.GetItemCount():
            self.liste.CheckItem(i, False)
            i = i + 1

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev

    def pre_chapeaux(self):
        liste = []
        i = 0
        while i < self.liste.GetItemCount():
            if self.liste.IsChecked(i) == True:
                liste.append(int(self.liste.GetItemText(i)))
            i = i + 1
        return liste

    def verifier(self, event):
        nextButton = self.GetParent().FindWindowById(wx.ID_FORWARD)
        nb_max = utile.nb_chapeaux_necessaires(self.liste.GetItemCount(), tournois.tournoi().equipes_par_manche)

        if nb_max < len(self.pre_chapeaux()):
            self.txt_msg.chg_texte("Il ne peut pas y avoir plus de %s chapeau(x)." % nb_max, wx.ICON_ERROR)
            nextButton.Disable()
        elif nb_max > len(self.pre_chapeaux()):
            self.txt_msg.chg_texte("Si nécessaire, le reste de la séléction se fera par tirage. (maximum %s chapeau(x))..." % nb_max, wx.ICON_INFORMATION)
            nextButton.Enable()
        else:
            self.txt_msg.chg_texte("")
            nextButton.Enable()

        if event is not None:
            event.Skip()

class LancerTiragePage(wiz.PyWizardPage):
    def __init__(self, parent, title):
        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.sizer, self.txt_msg = ajout_page_titre(self, u"Tirage")

        self._tirage = None

        # Tirage manuel / automatique
        self.rdb_type_tirage = wx.RadioBox(self, wx.ID_ANY, u"", choices = [u"Tirage Automatique", u"Tirage Manuel"],
                                           majorDimension = 2, style = wx.RA_SPECIFY_COLS)

        # Choix de l'algorithme
        self.chx_algorithme = wx.Choice(self, wx.ID_ANY, choices = tirages.__modules__.keys())
        self.txt_algorithme = wx.StaticText(self, wx.ID_ANY, u"Choix de l'algorithme utilisé: ")
        self.btn_options = wx.Button(self, id = wx.ID_PREFERENCES, label = u"Options", size = (100, -1))

        # Progression
        self.bar_progression = wx.Gauge(self, wx.ID_ANY, 100, style = wx.GA_HORIZONTAL)
        self.txt_progression = wx.TextCtrl(self, wx.ID_ANY, u"", style = wx.TE_MULTILINE)
        self.txt_progression.SetEditable(False)

        # Start / Stop
        self.btn_tirage = wx.Button(self, id = wx.ID_APPLY, label = u"Démarrer", size = (100, -1))

        self.sizer.Add(self.rdb_type_tirage, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add((10, 10), 0, wx.EXPAND | wx.ALL, 5)

        chx_box = wx.BoxSizer(wx.HORIZONTAL)
        chx_box.Add(self.txt_algorithme, 0, wx.ALIGN_CENTER_VERTICAL)
        chx_box.Add(self.chx_algorithme, 1, wx.LEFT, 10)
        chx_box.Add((40, 10), 0)
        chx_box.Add(self.btn_options, 0)
        self.sizer.AddSizer(chx_box, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add((10, 10), 0, wx.EXPAND | wx.ALL, 5)

        prg_box = wx.BoxSizer(wx.HORIZONTAL)
        prg_box.Add(self.bar_progression, 1, wx.ALIGN_CENTER_VERTICAL)
        prg_box.Add((40, 10), 0)
        prg_box.Add(self.btn_tirage, 0)
        self.sizer.AddSizer(prg_box, 0, wx.EXPAND | wx.ALL, 5)

        self.sizer.AddSizer(self.txt_progression, 1, wx.EXPAND | wx.ALL, 5)

        self.Bind(wx.EVT_RADIOBOX, self.verifier, self.rdb_type_tirage)
        self.Bind(wx.EVT_BUTTON, self._modifier_options, self.btn_options)
        self.Bind(wx.EVT_BUTTON, self.demarrer_arreter_tirage, self.btn_tirage)
        self.Bind(evt.EVT_PROGRESSION_TIRAGE, self.progression)

    def _modifier_options(self, event):
        wx.PostEvent(self, evt.PreferencesEvent(self.btn_options.GetId(), 2))

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev

    def pre_tirage(self):
        if self.rdb_type_tirage.GetSelection() == 1:
            # Tirage manuel: créer un tirage ordonné
            equipes = self.GetParent().page1.equipes()
            pre_chapeaux = self.GetParent().page2.pre_chapeaux()
            for chapeau in pre_chapeaux:
                equipes.remove(chapeau)

            tirage = utile.creer_manches(equipes, tournois.tournoi().equipes_par_manche)

            if len(tirage[-1]) < tournois.tournoi().equipes_par_manche:
                pre_chapeaux += tirage.pop(-1)

            return (tirage, pre_chapeaux)
        else:
            # tirage automatique
            return (self._tirage.tirage, self._tirage.chapeaux)

    def progression_event(self, *args, **kwrds):
        """
        Méthode appelée par le thread à chaque nouvelle progression de l'algorithme.
        """
        event = evt.ProgressionTirageEvent(-1, *args, **kwrds)
        wx.PostEvent(self, event)
        time.sleep(0.001)

    def progression(self, event):
        """
        Méthode appelée par le thread principal lors d'un nouveau événement de 
        progression.
        """
        self.bar_progression.SetValue(event.valeur)
        if event.message is not None:
            self.txt_progression.WriteText(event.message + u'\n')

        if event.erreur or event.valeur == 100:
            self._tirage.isAlive = lambda : False
            self.verifier(event)

    def demarrer_arreter_tirage(self, event):
        if self._tirage is not None:
            if self._tirage.isAlive():
               self._tirage.stop()
               self._tirage.join()
               self.txt_msg.chg_texte(u"")
            else:
                self._tirage = None

        if self._tirage is None:
            self.txt_msg.chg_texte(u"")
            self.txt_progression.Clear()
            self.txt_progression.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD, False, "Courier New"))
            # Statistiques des équipes (hors FORFAITS)
            statistiques = tournois.tournoi().statistiques(self.GetParent().forfaits())

            # Pre chapeaux
            pre_chapeaux = self.GetParent().page2.pre_chapeaux()

            # Créeation du thread tirage
            self._tirage = tirages.tirage(self.chx_algorithme.GetStringSelection(),
                                          tournois.tournoi().equipes_par_manche,
                                          statistiques,
                                          pre_chapeaux,
                                          self.progression_event)

            # Configuration du tirage
            config = self.GetParent().config.get_options(u"TIRAGE_" + self.chx_algorithme.GetStringSelection().upper())
            self._tirage.configurer(**config)

            # Démarrer le tirage
            self._tirage.start()
            self.verifier(None)

    def verifier(self, event):
        nextButton = self.GetParent().FindWindowById(wx.ID_FORWARD)
        prevButton = self.GetParent().FindWindowById(wx.ID_BACKWARD)
        cancButton = self.GetParent().FindWindowById(wx.ID_CANCEL)

        if self.rdb_type_tirage.GetSelection() == 1:
            # Tirage manuel
            self.chx_algorithme.Disable()
            self.bar_progression.Disable()
            self.btn_tirage.Disable()
            self.btn_options.Disable()
            nextButton.Enable()
            self.txt_msg.chg_texte(u"Passez à l'étape suivante.", wx.ICON_INFORMATION)
        else:
            self.txt_msg.chg_texte(u"")
            if self._tirage is None:
                # Pas de tirage effectué
                self.chx_algorithme.Enable()
                self.bar_progression.Enable()
                self.btn_options.Enable()
                self.rdb_type_tirage.Enable()
                self.btn_tirage.Enable()
                self.btn_tirage.SetLabel("Démarrer")
                nextButton.Disable()
            else:
                if self._tirage.isAlive():
                    # Algorithme en cours
                    self.rdb_type_tirage.Disable()
                    self.chx_algorithme.Disable()
                    self.bar_progression.Enable()
                    self.btn_options.Disable()
                    self.btn_tirage.Enable()
                    self.btn_tirage.SetLabel("Arrêter")
                    nextButton.Disable()
                    prevButton.Disable()
                    cancButton.Disable()
                else:
                    # Algorithme terminé
                    self.rdb_type_tirage.Enable()
                    self.chx_algorithme.Enable()
                    self.bar_progression.Enable()
                    self.btn_options.Enable()
                    self.btn_tirage.Enable()
                    self.btn_tirage.SetLabel("Démarrer")
                    prevButton.Enable()
                    cancButton.Enable()

                    # Passer à la confirmation du tirage
                    if self._tirage.erreur is None:
                        self.txt_msg.chg_texte(u"Le tirage est terminé. Passez à l'étape suivante.", wx.ICON_INFORMATION)
                        nextButton.Enable()
                    else:
                        self.txt_msg.chg_texte(unicode(self._tirage.erreur), wx.ICON_ERROR)
                        nextButton.Disable()

        if event is not None:
            event.Skip()

class ConfirmerTiragePage(wiz.PyWizardPage):
    def __init__(self, parent, title):
        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.sizer, self.txt_msg = ajout_page_titre(self, u"Confirmation du tirage")

        self.grille = None
        self.btn_echanger = wx.Button(self, wx.ID_ANY, label = u"Echanger", size = (100, -1))

        self.sizer.AddSizer(self.btn_echanger, 0, wx.LEFT | wx.BOTTOM, 5)
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.echanger, self.btn_echanger)

        self.statistiques = tournois.tournoi().statistiques()

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev

    def echanger(self, event):
        if self.grille is not None:
            cell1, cell2 = self.grille.echanger()
            self.verifier_ligne(cell1[0])
            self.verifier_ligne(cell2[0])
            self.verifier(event)

    def chg_tirage(self, tirage, chapeaux = []):
        if self.grille is not None:
            self.sizer.Remove(self.grille)
        self.grille = GrilleManchesCtrl(self, tournois.tournoi().equipes_par_manche, tirage, chapeaux)
        self.Bind(grid.EVT_GRID_CELL_LEFT_CLICK, self.verifier)
        self.sizer.Insert(3, self.grille, 1, wx.EXPAND | wx.ALL, 5)
        self.Layout()
        self.grille.Layout()

    def tirage(self):
        l = []
        i = 0
        while i < self.grille.GetNumberRows():
            manche = self.grille.manche(i)
            if u"C" not in manche:
                l.append(manche)
            i += 1

        return l

    def chapeaux(self):
        manche = self.grille.manche(0)
        if u"C" in manche:
            return [equipe for equipe in manche if equipe != u"C"]
        else:
            return []

    def verifier_ligne(self, ligne):
        attention = False
        manche = self.grille.manche(ligne)
        if u"C" in manche:
            manche = [equipe for equipe in manche if equipe != u"C"]
            # Compter parmis les chapeaux les équipes qui ont été déjà chapeau
            deja_ete_chapeau = []
            for num in manche:
                if tournois.tournoi().equipe(num).total_chapeaux() != 0:
                    deja_ete_chapeau.append(num)
                i = 1

            # Afficher le message si des équipes ont déjà été chapeau
            if len(deja_ete_chapeau) == 1:
                attention = True
                self.grille.chg_texte(ligne, u"!!! L'équipe n°%s a déjà été chapeau." % deja_ete_chapeau[0])
            elif len(deja_ete_chapeau) > 1:
                attention = True
                self.grille.chg_texte(ligne, u"!!! Les équipes n°%s ont déjà été chapeaux." % ", ".join(map(unicode, deja_ete_chapeau)))
            else:
                self.grille.chg_texte(ligne, u"")
        else:
            # Pour chaque ligne, afficher si des équipes se sont déjà rencontrées.
            renc = []
            for num in manche:
                c = []
                adversaires = self.statistiques[num]['adversaires']
                for adv in adversaires:
                    if adv in manche:
                        c.append(adv)
                if c != []:
                    c = [num] + c
                    c.sort()
                    if c not in renc:
                        renc.append(c)

            if renc != []:
                attention = True
                self.grille.chg_texte(ligne, u"!!! Les rencontres suivantes ont déjà eu lieu: %s" % ", ".join(map(unicode, renc)))
            else:
                self.grille.chg_texte(ligne, u"")

        return attention

    def verifier(self, event):
        if self.grille is not None:
            if self.grille.echangeable():
                self.btn_echanger.Enable()
            else:
                self.btn_echanger.Disable()

            if event is None:
                for i in range(self.grille.GetNumberRows()):
                    self.verifier_ligne(i)

            attention = False
            for i in range(self.grille.GetNumberRows()):
                if self.grille.GetCellValue(i, self.grille.GetNumberCols() - 1):
                    attention = True
                    break
            if attention:
                self.txt_msg.chg_texte(u"Ce tirage contient des redondances.", wx.ICON_WARNING)
            else:
                self.txt_msg.chg_texte(u"")

        if event is not None:
            event.Skip()

#--- Fenêtre de tirage + d'ajout de partie (Wizard)-----------------------------

class DialogueAjouterPartie(wiz.Wizard):
    def __init__(self, parent, config):
        wiz.Wizard.__init__(self, parent, wx.ID_ANY, title = u"Nouvelle partie", pos = wx.DefaultPosition)
        self.CenterOnParent()
        self.config = config

        self.page1 = SelectionEquipesPage(self, u"Page 1")
        self.page2 = SelectionChapeauPage(self, u"Page 2")
        self.page3 = LancerTiragePage(self, u"Page 3")
        self.page4 = ConfirmerTiragePage(self, u"Page 4")

        # Ordre initial des pages
        self.page1.SetNext(self.page2)
        self.page2.SetPrev(self.page1)
        self.page2.SetNext(self.page3)
        self.page3.SetPrev(self.page2)
        self.page3.SetNext(self.page4)
        self.page4.SetPrev(self.page3)

        self.FitToPage(self.page1)
        self.GetPageAreaSizer().Add(self.page1)

        self.Bind(wiz.EVT_WIZARD_PAGE_CHANGED, self.chg_page)
        self.Bind(wx.EVT_CLOSE, self.annuler)

    def ShowModal(self):
        return self.RunWizard(self.page1)

    def chg_page(self, event):
        page = event.GetPage()
        if page == self.page2:
            page.liste.ajout_equipes(self.page1.equipes())
        elif page == self.page4:
            page.chg_tirage(*self.page3.pre_tirage())
        page.verifier(None)

    def equipes(self):
        return self.page1.equipes()

    def forfaits(self):
        return self.page1.forfaits()

    def chapeaux(self):
        return self.page4.chapeaux()

    def tirage(self):
        return self.page4.tirage()

    def annuler(self, event):
        if self.page3._tirage is not None:
            if self.page3._tirage.isAlive():
                self.page3.txt_msg.chg_texte(u"Arrêtez le tirage avant de fermer.", wx.ICON_WARNING)
                return
        event.Skip()
