# -*- coding: UTF-8 -*-

import wx
import wx.wizard as wiz
from wx import grid
from wx.lib.mixins import listctrl
from wx.lib.wordwrap import wordwrap

from tourbillon.gui import evenements as evt
from tourbillon.gui.dlgimpression import DialogueImprimerTirage

from tourbillon import images
from tourbillon.core import constantes as cst
from tourbillon.core import tournoi
from tourbillon.core.tirages import utils
from tourbillon.core import tirages


ID_DLG_CLASSEMENT = wx.NewId()


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


class DialogueSupprimerPartie(wx.Dialog):

    def __init__(self, parent, choix=[], numero_affiche=1):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title="Supprimer une partie", style=wx.DEFAULT_DIALOG_STYLE | wx.CENTER_ON_SCREEN, pos=wx.DefaultPosition, size=wx.DefaultSize)
        self.SetMinSize((500, 150))
        self.SetSize(wx.Size(500, 140))
        self.CenterOnParent()

        self.txt_phrase0 = wx.StaticText(self, wx.ID_ANY, "Etes vous sûr de vouloir supprimer la partie n° ")
        self.ctl_numero = wx.Choice(self, wx.ID_ANY, choices=map(unicode, choix))
        self.txt_phrase1 = wx.StaticText(self, wx.ID_ANY, " ?")
        self.txt_phrase2 = wx.StaticText(self, wx.ID_ANY, "(Attention, toutes les données de la partie seront supprimées)")
        self.ctl_numero.SetSelection(self.ctl_numero.FindString(unicode(numero_affiche)))

        # Choix
        box_chx = wx.BoxSizer(wx.HORIZONTAL)
        box_chx.Add(self.txt_phrase0, 0, wx.ALIGN_CENTER_VERTICAL)
        box_chx.Add(self.ctl_numero, 0, wx.ALIGN_CENTER_VERTICAL)
        box_chx.Add(self.txt_phrase1, 0, wx.ALIGN_CENTER_VERTICAL)

        # Boutons
        self.btn_ok = wx.Button(self, id=wx.ID_OK, label="Supprimer", size=(100, -1))
        self.btn_annule = wx.Button(self, id=wx.ID_CANCEL, label="Annuler", size=(100, -1))
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

    def __init__(self, parent, numero_affiche=1):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title="Tirages", style=wx.DEFAULT_DIALOG_STYLE | wx.CENTER_ON_SCREEN | wx.RESIZE_BORDER | wx.STAY_ON_TOP)
        self.CenterOnParent()

        self.txt_phrase = wx.StaticText(self, wx.ID_ANY, "Tirage de la partie n° ")
        self.ctl_numero = wx.Choice(self, wx.ID_ANY, choices=[unicode(partie.numero) for partie in tournoi.tournoi().parties()])
        self.ctl_numero.SetSelection(self.ctl_numero.FindString(unicode(numero_affiche)))

        # Choix
        box_chx = wx.BoxSizer(wx.HORIZONTAL)
        box_chx.Add(self.txt_phrase, 0, wx.ALIGN_CENTER_VERTICAL)
        box_chx.Add(self.ctl_numero, 0, wx.ALIGN_CENTER_VERTICAL)

        # Grille
        self.grille = GrilleManchesCtrl(self, {}, chapeaux=[])

        # Boutons
        self.btn_ok = wx.Button(self, id=wx.ID_OK, label="Fermer", size=(100, -1))
        self.btn_imprimer = wx.Button(self, id=wx.ID_PREVIEW_PRINT, label="Imprimer...", size=(100, -1))
        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        box_btn.Add(self.btn_ok, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 20)
        box_btn.Add(self.btn_imprimer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 20)

        # Assembler
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(box_chx, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 20)
        self.sizer.Add(self.grille, 1, wx.EXPAND | wx.ALL, 5)
        self.sizer.AddSizer((10, 10), 0, wx.EXPAND)
        self.sizer.AddSizer(box_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 20)
        self.SetSizer(self.sizer)
        self.Layout()

        self._maj(None)
        self.Bind(wx.EVT_CHOICE, self._maj, self.ctl_numero)
        self.Bind(wx.EVT_BUTTON, self.imprimer, self.btn_imprimer)

    def _maj(self, event):
        partie = tournoi.tournoi().partie(int(self.ctl_numero.GetStringSelection()))
        d = {}
        for m in partie.manches():
            piquet = tournoi.tournoi().equipe(m[0]).resultat(partie.numero).piquet
            d[piquet] = m
        self.grille.maj(d, [eq.numero for eq in partie.chapeaux()], tournoi.tournoi().statistiques(partie_limite=partie.numero - 1))

        for i in range(self.grille.GetNumberRows()):
            self.grille.verifier_ligne(i)

        if self.grille.GetNumberRows() < 30:
            self.Fit()

    def imprimer(self, event):
        dlg = DialogueImprimerTirage(self.GetParent(), self.ctl_numero.GetStringSelection(), self.grille)
        self.Close()
        dlg.Print()


class DialogueAfficherClassement(wx.Dialog):

    single = None

    def __init__(self, parent, numero_affiche=1):
        wx.Dialog.__init__(self, parent, ID_DLG_CLASSEMENT, title="Tirages", style=wx.DEFAULT_DIALOG_STYLE | wx.CENTER_ON_SCREEN | wx.RESIZE_BORDER | wx.STAY_ON_TOP)
        DialogueAfficherClassement.single = self
        self.CenterOnParent()
        self.SetSize((300, 600))

        txt_phrase = wx.StaticText(self, wx.ID_ANY, "Classement des équipes")

        # Grille
        self.grille = grid.Grid(self, wx.ID_ANY)
        self.grille.CreateGrid(0, 2)
        self.grille.SetColLabelValue(0, "Place")
        self.grille.SetColLabelValue(1, "N°")
        self.grille.SetRowLabelSize(0)
        self.grille.EnableDragColSize(False)
        self.grille.EnableDragRowSize(False)

        # Boutons
        self.btn_ok = wx.Button(self, id=wx.ID_OK, label="Fermer", size=(100, -1))

        # Assembler
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(txt_phrase, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 20)
        self.sizer.Add(self.grille, 1, wx.EXPAND | wx.ALL, 5)
        self.sizer.AddSizer((10, 10), 0, wx.EXPAND)
        self.sizer.Add(self.btn_ok, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 20)
        self.SetSizer(self.sizer)
        self.Layout()

        self._maj(None)
        self.Bind(wx.EVT_ACTIVATE, self._maj)
        self.Bind(wx.EVT_CLOSE, self._clear)

    def _clear(self, event):
        DialogueAfficherClassement.single = None
        event.Skip()

    def _maj(self, event):
        avec_victoires = self.GetParent().config.get_typed('TOURNOI', 'CLASSEMENT_VICTOIRES')
        avec_joker = self.GetParent().config.get_typed('TOURNOI', 'CLASSEMENT_JOKER')
        avec_duree = self.GetParent().config.get_typed('TOURNOI', 'CLASSEMENT_DUREE')
        classement = tournoi.tournoi().classement(avec_victoires, avec_joker, avec_duree)

        # Effacer la grille
        if self.grille.GetNumberRows() > 0:
            self.grille.DeleteRows(1, self.grille.GetNumberRows(), False)

        i = 0
        for equipe, place in classement:
            self.grille.InsertRows(i, 1, False)
            self.grille.SetCellValue(i, 0, "%s" % place)
            self.grille.SetCellValue(i, 1, "%s" % equipe.numero)
            i += 1

        self.Layout()


class BandeTexte(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.SetMinSize(wx.Size(50, 22))

        self._info = images.bitmap('icon_info.png')
        self._erreur = images.bitmap('icon_erreur.png')
        self._attention = images.bitmap('icon_attention.png')
        self.btm_icon = wx.StaticBitmap(self, wx.ID_ANY, self._info)
        self.btm_icon.Hide()

        self.txt_message = wx.StaticText(self, wx.ID_ANY, "")
        self.txt_message.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.btm_icon, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.txt_message, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        self.SetSizer(sizer)

    def chg_texte(self, texte, icon=None):
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


class ListeEquipesCtrl(wx.ListCtrl, listctrl.CheckListCtrlMixin):

    def __init__(self, parent, config):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT)
        listctrl.CheckListCtrlMixin.__init__(self)
        self.config = config

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
        avec_victoires = self.config.get_typed('TOURNOI', 'CLASSEMENT_VICTOIRES')
        avec_joker = self.config.get_typed('TOURNOI', 'CLASSEMENT_JOKER')
        avec_duree = self.config.get_typed('TOURNOI', 'CLASSEMENT_DUREE')
        classement.update(tournoi.tournoi().classement(avec_victoires, avec_joker, avec_duree))

        for num in liste_equipes:
            equipe = tournoi.tournoi().equipe(int(num))
            self.Append([unicode(equipe.numero),
                         ", ".join([unicode(joueur) for joueur in equipe.joueurs()]),
                         unicode(equipe.victoires()),
                         unicode(equipe.points()),
                         unicode(equipe.chapeaux()),
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


class GrilleManchesCtrl(grid.Grid):

    def __init__(self, parent, manches, chapeaux=[]):
        grid.Grid.__init__(self, parent, wx.ID_ANY)
        self.equipes_par_manche = tournoi.tournoi().equipes_par_manche
        self.CreateGrid(0, self.equipes_par_manche + 2)
        self.SetColAttr(0, self.attribut('piquet'))
        self.SetColAttr(self.GetNumberCols() - 1, self.attribut('info'))

        for i in range(self.GetNumberCols()):
            if 0 < i < self.GetNumberCols() - 1:
                self.SetColAttr(i, self.attribut('equipe'))
            self.SetColSize(i, 50)

        # cases selectionnées
        self.select1 = None
        self.select2 = None

        # self.SetGridLineColour(wx.Colour(255, 255, 255))
        self.SetColMinimalAcceptableWidth(1)

        self.SetRowLabelSize(0)
        for i in range(self.GetNumberCols()):
            if i == 0:
                self.SetColLabelValue(i, "Piquet")
            elif i == self.GetNumberCols() - 1:
                self.SetColLabelValue(self.GetNumberCols() - 1, "Information")
            else:
                self.SetColLabelValue(i, "")
        self.EnableDragColSize(False)
        self.EnableDragRowSize(False)

        # Mise à jour
        self.maj(manches, chapeaux, tournoi.tournoi().statistiques())

        self.Bind(grid.EVT_GRID_CELL_LEFT_CLICK, self._selection_equipe)
        self.Bind(wx.EVT_SIZE, self.Layout, self)

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
        elif self.select1 is None:
            if self.GetCellValue(l, c) != "C" and 0 < c < self.equipes_par_manche + 1:
                self.select1 = (l, c)
                self._selectionner(l, c)
        elif self.select2 is None:
            if self.GetCellValue(l, c) != "C" and 0 < c < self.equipes_par_manche + 1:
                self.select2 = (l, c)
                self._selectionner(l, c)
        self.Refresh()
        event.Skip()

    def _selectionner(self, ligne, colonne):
        self.SetCellBackgroundColour(ligne, colonne, wx.Colour(6, 200, 6))
        self.SetCellFont(ligne, colonne, wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))

    def _deselectionner(self, ligne, colonne):
        self.SetCellBackgroundColour(ligne, colonne, wx.Colour(255, 255, 255))
        self.SetCellFont(ligne, colonne, wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))

    def attribut(self, ref):
        attr = grid.GridCellAttr()
        if ref == 'equipe':
            attr.SetBackgroundColour(wx.Colour(255, 255, 255))
            attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetTextColour(wx.Colour(0, 0, 200))
            attr.SetReadOnly(True)
        elif ref == 'piquet':
            attr.SetBackgroundColour(images.couleur('piquet'))
            attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
            attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            attr.SetTextColour(wx.Colour(0, 0, 0))
            attr.SetReadOnly(False)
        elif ref == 'info':
            attr.SetBackgroundColour(wx.Colour(255, 255, 255))
            attr.SetTextColour(wx.Colour(255, 0, 0))
            attr.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
            attr.SetReadOnly(True)
        return attr

    def Layout(self, event=None):
        grid.Grid.Layout(self)
        # Largeur dernière colonne
        largeur = self.Size[0] - 30 - self.GetColSize(0) * (self.equipes_par_manche + 1)
        if largeur < 200:
            largeur = 200
        self.SetColSize(self.equipes_par_manche + 1, largeur)
        if event is not None:
            event.Skip()

    def maj(self, manches, chapeaux=[], statistiques={}):
        self.statistiques = statistiques

        # Suppression des lignes
        if self.GetNumberRows() > 0:
            self.DeleteRows(0, self.GetNumberRows())

        # Nombre de lignes (1 par manche + 1 pour les chapeaux)
        self.nbr_ligne = len(manches)
        if len(chapeaux) != 0:
            self.nbr_ligne += 1
        self.InsertRows(0, self.nbr_ligne)

        # Première ligne pour afficher les chapeaux
        i = 0
        j = 0
        if len(chapeaux) != 0:
            self.SetCellValue(i, 0, "-")
            while j < self.equipes_par_manche:
                if j < len(chapeaux):
                    self.SetCellValue(i, j + 1, unicode(chapeaux[j]))
                else:
                    self.SetCellValue(i, j + 1, "C")
                    self.SetCellTextColour(i, j + 1, images.couleur(cst.CHAPEAU))
                j += 1
            i += 1

        # Afficher les manches
        for piquet, m in manches.items():
            self.SetCellValue(i, 0, unicode(piquet))
            j = 1
            for e in m:
                self.SetCellValue(i, j, unicode(e))
                j += 1
            i += 1

    def chg_texte(self, ligne, texte):
        self.SetCellValue(ligne, self.equipes_par_manche + 1, unicode(texte))

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
        for j in range(1, self.GetNumberCols() - 1):
            valeur = self.GetCellValue(ligne, j)
            if valeur != "C":
                valeur = int(valeur)
            m.append(valeur)

        p = self.GetCellValue(ligne, 0)
        try:
            p = int(p)
        except:
            pass

        return p, m

    def verifier_ligne(self, ligne):
        attention = False
        _piquet, manche = self.manche(ligne)

        if "C" in manche:
            manche = [equipe for equipe in manche if equipe != "C"]
            # Compter parmis les chapeaux les équipes qui ont déjà été chapeau
            deja_ete_chapeau = []
            for num in manche:
                if self.statistiques[num]['chapeaux'] != 0:
                    deja_ete_chapeau.append(num)

            # Afficher le message si des équipes ont déjà été chapeau
            if len(deja_ete_chapeau) == 1:
                attention = True
                self.chg_texte(ligne, "!!! L'équipe n°%s a déjà été chapeau." % deja_ete_chapeau[0])
            elif len(deja_ete_chapeau) > 1:
                attention = True
                self.chg_texte(ligne, "!!! Les équipes n°%s ont déjà été chapeaux." % ", ".join(map(unicode, deja_ete_chapeau)))
            else:
                self.chg_texte(ligne, "")
        else:
            # Pour chaque ligne, afficher si des équipes se sont déjà rencontrées.
            rencontre_faite = False
            rencontres = []
            manche.sort()

            for num in manche:
                for manche_prec in self.statistiques[num]['manches']:
                    manche_prec = sorted(manche_prec)
                    if manche == manche_prec:
                        rencontres.append(manche)
                        rencontre_faite = True
                        break

                    m = []
                    for adv in manche_prec:
                        if adv in manche:
                            m.append(adv)
                    if m and m not in rencontres and len(m) > 1:
                        rencontres.append(m)

            if rencontres != []:
                attention = True
                if rencontre_faite:
                    texte = "!!! Cette manche a déjà eu lie"
                else:
                    texte = "!!! Les rencontres suivantes ont déjà eu lieu: %s" % ", ".join(map(unicode, rencontres))
                self.chg_texte(ligne, texte)
            else:
                self.chg_texte(ligne, "")

        return attention


class SelectionEquipesPage(wiz.PyWizardPage):

    def __init__(self, parent, title):
        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.sizer, self.txt_msg = ajout_page_titre(self, "Selection des équipes")

        self.liste = ListeEquipesCtrl(self, self.GetParent().config)
        self.liste.ajout_equipes(tournoi.tournoi().equipes())
        self.liste.SetSize(wx.Size(600, 300))
        self._cocher_tout(None)

        self.btn_cocher_tout = wx.BitmapButton(self, wx.ID_ANY, images.bitmap('check_on.png'))
        self.btn_cocher_tout.SetToolTipString("Sélectionner toutes les équipes")
        self.btn_decocher_tout = wx.BitmapButton(self, wx.ID_ANY, images.bitmap('check_off.png'))
        self.btn_decocher_tout.SetToolTipString("Dessélectionner toutes les équipes")

        self.sizer.Add(self.liste, 1, wx.EXPAND | wx.ALL, 5)

        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        box_btn.Add(self.btn_cocher_tout)
        box_btn.Add(self.btn_decocher_tout)

        self.sizer.AddSizer(box_btn, 0, wx.LEFT, 5)

        # Décocher les équipes forfait de la partie précédente
        if tournoi.tournoi().partie_courante() is not None:
            forfaits = tournoi.tournoi().partie_courante().forfaits()
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

    def SetNext(self, nnext):
        self.next = nnext

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        if utils.nb_chapeaux_necessaires(len(self.equipes()), tournoi.tournoi().equipes_par_manche) != 0:
            # Page chapeaux
            self.next.GetNext().SetPrev(self.next)
            return self.next
        else:
            # Page tirage
            self.next.GetNext().SetPrev(self)
            return self.next.GetNext()

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
        self.sizer, self.txt_msg = ajout_page_titre(self, "Selection des chapeaux")

        self.liste = ListeEquipesCtrl(self, self.GetParent().config)
        self.liste.SetSize(wx.Size(600, 300))

        self.btn_cocher_tout = wx.BitmapButton(self, -1, images.bitmap('check_on.png'))
        self.btn_cocher_tout.SetToolTipString("Sélectionner toutes les équipes")
        self.btn_decocher_tout = wx.BitmapButton(self, -1, images.bitmap('check_off.png'))
        self.btn_decocher_tout.SetToolTipString("Dessélectionner toutes les équipes")

        self.sizer.Add(self.liste, 1, wx.EXPAND | wx.ALL, 5)

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

    def SetNext(self, nnext):
        self.next = nnext

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev

    def chapeaux(self):
        liste = []
        i = 0
        while i < self.liste.GetItemCount():
            if self.liste.IsChecked(i) == True:
                liste.append(int(self.liste.GetItemText(i)))
            i = i + 1
        return liste

    def verifier(self, event):
        nextButton = self.GetParent().FindWindowById(wx.ID_FORWARD)
        nb_max = utils.nb_chapeaux_necessaires(self.liste.GetItemCount(), tournoi.tournoi().equipes_par_manche)

        if nb_max < len(self.chapeaux()):
            self.txt_msg.chg_texte("Il ne peut pas y avoir plus de %s chapeau(x)." % nb_max, wx.ICON_ERROR)
            nextButton.Disable()
        elif nb_max > len(self.chapeaux()):
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
        self.sizer, self.txt_msg = ajout_page_titre(self, "Tirage")

        self._generateur = None

        # Choix de l'algorithme
        liste_tirages = [generateur.DESCRIPTION for _nom, generateur in tirages.TIRAGES.items()]
        self.chx_algorithme = wx.Choice(self, wx.ID_ANY, choices=liste_tirages)
        algorithme = self.GetParent().config.get('TOURNOI', 'ALGORITHME_DEFAUT')
        self.chx_algorithme.SetSelection(tirages.TIRAGES.keys().index(algorithme))
        self.txt_algorithme = wx.StaticText(self, wx.ID_ANY, "Choix de l'algorithme utilisé: ")
        self.btn_options = wx.Button(self, id=wx.ID_PREFERENCES, label="Options", size=(100, -1))

        # Progression
        self.bar_progression = wx.Gauge(self, wx.ID_ANY, 100, size=(-1, 15), style=wx.GA_HORIZONTAL)
        self.txt_tps_restant = wx.StaticText(self, wx.ID_ANY, "", size=(40, -1), style=wx.ALIGN_RIGHT)
        self.txt_progression = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.txt_progression.SetEditable(False)

        # Start / Stop
        self.btn_tirage = wx.Button(self, id=wx.ID_APPLY, label="Démarrer", size=(100, -1))

        chx_box = wx.BoxSizer(wx.HORIZONTAL)
        chx_box.Add(self.txt_algorithme, 0, wx.ALIGN_CENTER_VERTICAL)
        chx_box.Add(self.chx_algorithme, 1, wx.LEFT, 10)
        chx_box.Add((40, 10), 0)
        chx_box.Add(self.btn_options, 0)
        self.sizer.AddSizer(chx_box, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Add((10, 10), 0, wx.EXPAND | wx.ALL, 5)

        prg_box = wx.BoxSizer(wx.HORIZONTAL)
        prg_box.Add(self.bar_progression, 1, wx.ALIGN_CENTER_VERTICAL)
        prg_box.AddSpacer((10, -1))
        prg_box.Add(self.txt_tps_restant, 0, wx.ALIGN_CENTER_VERTICAL)
        prg_box.Add((40, 10), 0)
        prg_box.Add(self.btn_tirage, 0)
        self.sizer.AddSizer(prg_box, 0, wx.EXPAND | wx.ALL, 5)

        self.sizer.AddSizer(self.txt_progression, 1, wx.EXPAND | wx.ALL, 5)

        self.Bind(wx.EVT_BUTTON, self._modifier_options, self.btn_options)
        self.Bind(wx.EVT_BUTTON, self.demarrer_arreter_tirage, self.btn_tirage)
        self.Bind(evt.EVT_PROGRESSION_TIRAGE, self.progression)

    def _modifier_options(self, event):
        wx.PostEvent(self, evt.PreferencesEvent(self.btn_options.GetId(), 2, self.chx_algorithme.GetCurrentSelection()))

    def SetNext(self, nnext):
        self.next = nnext

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev

    def tirage(self):
        if self._generateur is None:
            self.demarrer_arreter_tirage(None)
        return self._generateur.tirage

    def chapeaux(self):
        if self._generateur is None:
            self.demarrer_arreter_tirage(None)
        return self._generateur.chapeaux

    def progression_event(self, *args, **kwrds):
        """
        Méthode appelée par le thread du tirage à chaque nouvelle progression de l'algorithme.
        """
        event = evt.ProgressionTirageEvent(-1, *args, **kwrds)
        wx.PostEvent(self, event)

    def progression(self, event):
        """
        Méthode appelée par le thread principal lors d'un nouveau événement
        de progression.
        """
        if event.valeur >= 0:
            self.bar_progression.SetValue(event.valeur)
        if event.message is not None:
            self.txt_progression.WriteText(event.message + u'\n')
        if event.tps_restant is not None:
            self.txt_tps_restant.SetLabel(tirages.utils.temps_texte(event.tps_restant))

        if self._generateur.erreur or event.valeur == 100:
            self._generateur.isAlive = lambda: False
            self.verifier(event)

    def demarrer_arreter_tirage(self, event):
        if self._generateur is not None:
            if self._generateur.isAlive():
                self._generateur.stop()
                self._generateur.join()
                self.txt_msg.chg_texte("")
            else:
                self._generateur = None

        if self._generateur is None:
            self.txt_msg.chg_texte("")
            self.txt_progression.Clear()
            self.bar_progression.SetValue(0)
            font = self.txt_progression.GetFont()
            font.SetFaceName("Courier")
            self.txt_progression.SetFont(font)
            # Statistiques des équipes (hors FORFAITS)
            statistiques = tournoi.tournoi().statistiques(self.GetParent().forfaits())

            # Pre chapeaux
            chapeaux = self.GetParent().page2.chapeaux()

            # Création du thread tirage
            self._generateur = tirages.creer_generateur(tirages.TIRAGES.items()[self.chx_algorithme.GetCurrentSelection()][0],
                                                        tournoi.tournoi().equipes_par_manche,
                                                        statistiques,
                                                        chapeaux,
                                                        self.progression_event)

            # Configuration du tirage
            config = self.GetParent().config.get_options(tirages.TIRAGES.items()[self.chx_algorithme.GetCurrentSelection()][0])
            self._generateur.configurer(**config)

            # Démarrer le tirage
            self._generateur.start()
            self.verifier(None)

    def verifier(self, event):
        nextButton = self.GetParent().FindWindowById(wx.ID_FORWARD)
        prevButton = self.GetParent().FindWindowById(wx.ID_BACKWARD)
        cancButton = self.GetParent().FindWindowById(wx.ID_CANCEL)

        self.txt_msg.chg_texte("")
        if self._generateur is None:
            # Pas de tirage effectué
            self.chx_algorithme.Enable()
            self.bar_progression.Enable()
            self.btn_options.Enable()
            self.btn_tirage.Enable()
            self.btn_tirage.SetLabel("Démarrer")
            nextButton.Disable()
        else:
            if self._generateur.isAlive():
                # Algorithme en cours
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
                self.chx_algorithme.Enable()
                self.bar_progression.Enable()
                self.btn_options.Enable()
                self.btn_tirage.Enable()
                self.btn_tirage.SetLabel("Démarrer")
                prevButton.Enable()
                cancButton.Enable()

                # Passer à la confirmation du tirage
                if self._generateur.erreur is None:
                    self.txt_msg.chg_texte("Le tirage est terminé. Passez à l'étape suivante.", wx.ICON_INFORMATION)
                    nextButton.Enable()
                else:
                    self.txt_msg.chg_texte(unicode(self._generateur.erreur), wx.ICON_ERROR)
                    nextButton.Disable()

        if event is not None:
            event.Skip()


class ConfirmerTiragePage(wiz.PyWizardPage):

    def __init__(self, parent, title):
        wiz.PyWizardPage.__init__(self, parent)
        self.next = self.prev = None
        self.sizer, self.txt_msg = ajout_page_titre(self, "Confirmation du tirage")

        self.grille = None

        self.btn_echanger = wx.Button(self, wx.ID_ANY, label="Echanger", size=(100, -1))
        self.btn_imprimer = wx.Button(self, id=wx.ID_PREVIEW_PRINT, label="Imprimer...", size=(100, -1))
        self.btn_classement = wx.Button(self, id=wx.ID_ANY, label="Classement...", size=(100, -1))
        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        box_btn.Add(self.btn_echanger, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 20)
        box_btn.Add(self.btn_imprimer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 20)
        box_btn.Add(self.btn_classement, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 20)

        self.sizer.AddSizer(box_btn, 0, wx.LEFT | wx.BOTTOM, 5)
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.echanger, self.btn_echanger)
        self.Bind(wx.EVT_BUTTON, self.imprimer, self.btn_imprimer)
        self.Bind(wx.EVT_BUTTON, self.classement, self.btn_classement)

    def SetNext(self, nnext):
        self.next = nnext

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev

    def echanger(self, event):
        if self.grille is not None:
            cell1, cell2 = self.grille.echanger()
            self.grille.verifier_ligne(cell1[0])
            self.grille.verifier_ligne(cell2[0])
            self.verifier(event)

    def chg_tirage(self, tirage, chapeaux=[]):
        if self.grille is not None:
            self.sizer.Remove(self.grille)

        d = {}
        piquets = tournoi.tournoi().piquets()
        for m in tirage:
            d[piquets.pop(0)] = m
        self.grille = GrilleManchesCtrl(self, d, chapeaux)
        self.Bind(grid.EVT_GRID_CELL_LEFT_CLICK, self.verifier)
        self.sizer.Insert(3, self.grille, 1, wx.EXPAND | wx.ALL, 5)
        self.Layout()
        self.grille.Layout()

    def tirage(self):
        l = {}
        i = 0
        while i < self.grille.GetNumberRows():
            piquet, manche = self.grille.manche(i)
            if "C" not in manche:
                l[piquet] = manche
            i += 1

        return l

    def chapeaux(self):
        _piquet, manche = self.grille.manche(0)
        if "C" in manche:
            return [equipe for equipe in manche if equipe != "C"]
        else:
            return []

    def imprimer(self, event):
        partie = tournoi.tournoi().partie_courante()
        if partie:
            num = partie.numero + 1
        else:
            num = 1
        dlg = DialogueImprimerTirage(self.GetParent(), num, self.grille)
        dlg.Print()

    def classement(self, event):
        if not DialogueAfficherClassement.single:
            DialogueAfficherClassement(self.GetParent())
            DialogueAfficherClassement.single.Show()
        DialogueAfficherClassement.single.Raise()

    def verifier(self, event):
        piquets = []
        if self.grille is not None:
            if self.grille.echangeable():
                self.btn_echanger.Enable()
            else:
                self.btn_echanger.Disable()

            if event is None:
                for i in range(self.grille.GetNumberRows()):
                    self.grille.verifier_ligne(i)

            # Message d'avertissement
            attention = False
            for i in range(self.grille.GetNumberRows()):
                p, _ = self.grille.manche(i)
                piquets.append(p)
                if self.grille.GetCellValue(i, self.grille.GetNumberCols() - 1):
                    attention = True

            if attention:
                self.txt_msg.chg_texte("Ce tirage contient des redondances.", wx.ICON_WARNING)
            else:
                self.txt_msg.chg_texte("")

        # Verifier unicité des numéro de piquets
        for i in range(len(piquets)):
            p = piquets[i]
            nb = piquets.count(p)
            if nb == 1 and type(p) == int:
                self.grille.SetCellBackgroundColour(i, 0, wx.Colour(200, 200, 200))
            else:
                self.grille.SetCellBackgroundColour(i, 0, wx.Colour(210, 0, 0))

        if event is not None:
            event.Skip()


class DialogueAjouterPartie(wiz.Wizard):

    def __init__(self, parent, config):
        wiz.Wizard.__init__(self, parent, wx.ID_ANY, title="Nouvelle partie",
                            style=wx.DEFAULT_FRAME_STYLE, pos=wx.DefaultPosition)
        self.CenterOnParent()
        self.config = config

        self.page1 = SelectionEquipesPage(self, "Page 1")
        self.page2 = SelectionChapeauPage(self, "Page 2")
        self.page3 = LancerTiragePage(self, "Page 3")
        self.page4 = ConfirmerTiragePage(self, "Page 4")

        # Ordre initial des pages
        self.page1.SetNext(self.page2)
        self.page2.SetPrev(self.page1)
        self.page2.SetNext(self.page3)
        self.page3.SetPrev(self.page2)
        self.page3.SetNext(self.page4)
        self.page4.SetPrev(self.page3)

        self.FitToPage(self.page1)

        self.Bind(wiz.EVT_WIZARD_PAGE_CHANGED, self.chg_page)
        self.Bind(wx.EVT_CLOSE, self.annuler)

    def ShowModal(self):
        return self.RunWizard(self.page1)

    def chg_page(self, event):
        page = event.GetPage()
        if page == self.page2:
            page.liste.ajout_equipes(self.page1.equipes())
        elif page == self.page4:
            page.chg_tirage(self.page3.tirage(), self.page3.chapeaux())
        page.verifier(None)
        page.Fit()

    def equipes(self):
        return self.page1.equipes()

    def forfaits(self):
        return self.page1.forfaits()

    def chapeaux(self):
        return self.page4.chapeaux()

    def tirage(self):
        return self.page4.tirage()

    def annuler(self, event):
        if self.page3._generateur is not None:
            if self.page3._generateur.isAlive():
                self.page3.txt_msg.chg_texte("Arrêtez le tirage avant de fermer.", wx.ICON_WARNING)
                return
        event.Skip()
