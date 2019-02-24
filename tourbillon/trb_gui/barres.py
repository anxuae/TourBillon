#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import wx
from wx.lib.agw import buttonpanel as bp
from tourbillon import images
from tourbillon.trb_gui import evenements as evt
from tourbillon.trb_gui import grille as grl
from tourbillon.trb_core import constantes as cst

#--- Variables Globales --------------------------------------------------------

ID_INFO = wx.NewId()
ID_TIRAGE = wx.NewId()
ID_NOUVELLE_E = wx.NewId()
ID_MODIFIER_E = wx.NewId()
ID_SUPPRIMER_E = wx.NewId()
ID_NOUVELLE_P = wx.NewId()
ID_SUPPRIMER_P = wx.NewId()
ID_RESULTATS = wx.NewId()
ID_INSCRIPTION = wx.NewId()
ID_PARTIE = wx.NewId()
ID_CLASSEMENT = wx.NewId()

STYLES_MENU = {None:{wx.ID_SAVE:False,
                    wx.ID_SAVEAS:False,
                    wx.ID_PRINT:False,
                    wx.ID_PREVIEW_PRINT:False,
                    ID_INFO:False,
                    ID_TIRAGE:False,
                    ID_INSCRIPTION:False,
                    ID_NOUVELLE_E:False,
                    ID_MODIFIER_E:False,
                    ID_SUPPRIMER_E:False,
                    ID_PARTIE:False,
                    ID_NOUVELLE_P:False,
                    ID_RESULTATS:False,
                    ID_CLASSEMENT:False},

              '0 equipe':{wx.ID_SAVE:True,
                    wx.ID_SAVEAS:True,
                    wx.ID_PRINT:False,
                    wx.ID_PREVIEW_PRINT:False,
                    ID_INFO:True,
                    ID_TIRAGE:False,
                    ID_INSCRIPTION:True,
                    ID_NOUVELLE_E:True,
                    ID_MODIFIER_E:False,
                    ID_SUPPRIMER_E:False,
                    ID_PARTIE:False,
                    ID_NOUVELLE_P:False,
                    ID_RESULTATS:False,
                    ID_CLASSEMENT:False},

              cst.T_INSCRIPTION:{wx.ID_SAVE:True,
                    wx.ID_SAVEAS:True,
                    wx.ID_PRINT:False,
                    wx.ID_PREVIEW_PRINT:False,
                    ID_INFO:True,
                    ID_TIRAGE:False,
                    ID_INSCRIPTION:True,
                    ID_NOUVELLE_E:True,
                    ID_MODIFIER_E:True,
                    ID_SUPPRIMER_E:True,
                    ID_PARTIE:False,
                    ID_CLASSEMENT:False},

              '0 partie':{wx.ID_SAVE:True,
                    wx.ID_SAVEAS:True,
                    wx.ID_PRINT:True,
                    wx.ID_PREVIEW_PRINT:True,
                    ID_INFO:True,
                    ID_TIRAGE:False,
                    ID_INSCRIPTION:True,
                    ID_NOUVELLE_E:True,
                    ID_MODIFIER_E:True,
                    ID_SUPPRIMER_E:True,
                    ID_PARTIE:True,
                    ID_NOUVELLE_P:True,
                    ID_RESULTATS:False,
                    ID_SUPPRIMER_P:False,
                    ID_CLASSEMENT:True},

              cst.T_ATTEND_TIRAGE:{wx.ID_SAVE:True,
                    wx.ID_SAVEAS:True,
                    wx.ID_PRINT:True,
                    wx.ID_PREVIEW_PRINT:True,
                    ID_INFO:True,
                    ID_TIRAGE:True,
                    ID_INSCRIPTION:True,
                    ID_NOUVELLE_E:True,
                    ID_MODIFIER_E:True,
                    ID_SUPPRIMER_E:False,
                    ID_PARTIE:True,
                    ID_NOUVELLE_P:True,
                    ID_RESULTATS:True,
                    ID_SUPPRIMER_P:True,
                    ID_CLASSEMENT:True},

              cst.T_PARTIE_EN_COURS:{wx.ID_SAVE:True,
                    wx.ID_SAVEAS:True,
                    wx.ID_PRINT:True,
                    wx.ID_PREVIEW_PRINT:True,
                    ID_INFO:True,
                    ID_TIRAGE:True,
                    ID_INSCRIPTION:True,
                    ID_NOUVELLE_E:True,
                    ID_MODIFIER_E:True,
                    ID_SUPPRIMER_E:False,
                    ID_PARTIE:True,
                    ID_NOUVELLE_P:False,
                    ID_RESULTATS:True,
                    ID_SUPPRIMER_P:True,
                    ID_CLASSEMENT:True}}

#--- Hack pour ButtonInfo ------------------------------------------------------

class ButtonInfo(bp.ButtonInfo):

    def __init__(self, parent, id = wx.ID_ANY, bmp = wx.NullBitmap,
                 status = "Normal", text = "", kind = wx.ITEM_NORMAL, shortHelp = "", longHelp = ""):
        bp.ButtonInfo.__init__(self, parent, id , bmp , status , text , kind, shortHelp , longHelp)

        if id == wx.ID_ANY:
            self._id = wx.NewId()
        else:
            self._id = id

    def Enable(self, enable = True):
        if enable:
            self.SetStatus('Normal')
        else:
            self.SetStatus('Disabled')

    def Check(self, checked = True):
        if self.GetKind() == wx.ITEM_CHECK:
            if checked:
                self.SetToggled(True)
                self.SetStatus('Toggled')
            else:
                self.SetToggled(False)
                self.SetStatus('Normal')

#--- Classes -------------------------------------------------------------------

class BarreMenu(wx.MenuBar):
    def __init__(self, parent):
        wx.MenuBar.__init__(self)

        # Menu fichier
        self.menu_fichier = wx.Menu()
        self.menu_fichier.Append(wx.ID_NEW, u"&Nouveau\tCtrl+N", u"  Commencer un nouveau tournoi")
        self.menu_fichier.Append(wx.ID_OPEN, u"&Charger\tCtrl+C", u"  Ouvrir un tournoi")
        self.menu_fichier.AppendSeparator()
        self.menu_fichier.Append(wx.ID_SAVE, u"&Enregistrer\tCtrl+S", u"  Enregistrer le fichier ouvert")
        self.menu_fichier.Append(wx.ID_SAVEAS, u"&Enregistrer sous...", u"  Enregistrer le fichier ouvert")
        self.menu_fichier.AppendSeparator()
        self.menu_fichier.Append(wx.ID_PREVIEW_PRINT, u"&Apreçu avant impression", u"  Visualiser le classement avant impression")
        self.menu_fichier.Append(wx.ID_PRINT, u"&Imprimer...\tCtrl+I", u"  Imprimer le classement des équipes")
        self.menu_fichier.AppendSeparator()
        self.menu_fichier.Append(wx.ID_EXIT, u"&Quitter\tCtrl+Q", u"  Quitter TourBillon")

        # Menu affichage
        self.menu_affichage = wx.Menu()
        self.menu_affichage.Append(ID_INFO, u"&Infos Equipes", u"  Afficher les informations des joueurs", wx.ITEM_CHECK)
        self.menu_affichage.Append(ID_TIRAGE, u"&Tirages", u"  Afficher les tirages")

        # Menu Tournoi
        self.sous_menu_inscription = wx.Menu()
        self.sous_menu_inscription.Append(ID_NOUVELLE_E, u"&Nouvelle\tCtrl+E", u"  Inscrire une nouvelle équipe au tournoi")
        self.sous_menu_inscription.Append(ID_MODIFIER_E, u"&Modifier", u"  Modifier les données d'une équipe")
        self.sous_menu_inscription.Append(ID_SUPPRIMER_E, u"&Supprimer", u"  Supprimer une équipe du tournoi")

        self.sous_menu_partie = wx.Menu()
        self.sous_menu_partie.Append(ID_NOUVELLE_P, u"&Nouvelle\tCtrl+P", u"  Lancer une nouvelle partie")
        self.sous_menu_partie.Append(ID_SUPPRIMER_P, u"&Supprimer", u"  Supprimer une partie")
        self.sous_menu_partie.Append(ID_RESULTATS, u"&Entrer les résultats", u"  Entrer les résultats des manches de la partie en cours")

        self.menu_tournoi = wx.Menu()
        self.menu_tournoi.AppendMenu(ID_INSCRIPTION, u"&Equipes", self.sous_menu_inscription)
        self.menu_tournoi.AppendMenu(ID_PARTIE, u"&Parties", self.sous_menu_partie)
        self.menu_tournoi.Append(ID_CLASSEMENT, u"&Classement", u"  Afficher le classement")
        self.menu_tournoi.AppendSeparator()
        self.menu_tournoi.Append(wx.ID_PREFERENCES, u"&Préférences", u" Configuration de l'application")

        # Menu Aide
        self.menu_aide = wx.Menu()
        self.menu_aide.Append(wx.ID_ABOUT, u"&A propos de TourBillon", u" Pour en savoir plus...")

        self.Append(self.menu_fichier, "&Fichier")
        self.Append(self.menu_affichage, "&Affichage")
        self.Append(self.menu_tournoi, "&Tournoi")
        self.Append(self.menu_aide, "&Aide")

    def _rafraichir(self, etat = None):
        """
        NE PAS UTILISER !!!!! (Manipulé par la fenêtre principale)
        """
        styles = STYLES_MENU[etat]
        for st in styles:
            self.Enable(st, styles[st])
        self.Layout()

class BarreBouton(bp.ButtonPanel):
    def __init__(self, parent):
        bp.ButtonPanel.__init__(self, parent, wx.ID_ANY, text = "",
                                agwStyle = bp.BP_USE_GRADIENT, alignment = bp.BP_ALIGN_LEFT)

        self.controls = []

        self.Freeze()
        # Bouton partie précédente
        self.btn_precedente = ButtonInfo(self, id = wx.ID_ANY,
                                        bmp = images.bitmap('precedent.png'), kind = wx.ITEM_NORMAL,
                                        shortHelp = "Précédente", longHelp = "Afficher les données de la partie précédente.")

        self.btn_precedente.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(self.btn_precedente)
        self.controls.append(self.btn_precedente)

        # Partie affichée
        self.txt_partie = wx.StaticText(self, id = wx.ID_ANY, label = "0",
                             size = (30, 40), style = wx.ALIGN_CENTER)
        self.txt_partie.SetToolTipString("Partie affichée")
        font = wx.Font(40, wx.SWISS, wx.NORMAL, wx.BOLD, False, "Mistral")

        self.txt_partie.SetFont(font)
        self.txt_partie.SetForegroundColour(wx.Color(62, 33, 17))
        self.AddControl(self.txt_partie)

        # Bouton partie suivante
        self.btn_suivante = ButtonInfo(self, id = wx.ID_ANY,
                        bmp = images.bitmap('suivant.png'), kind = wx.ITEM_NORMAL,
                        shortHelp = "Suivante", longHelp = "Afficher les données de la partie suivante.")

        self.btn_suivante.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(self.btn_suivante)
        self.controls.append(self.btn_suivante)

        # Ajouter un espace
        self.AddSpacer((100, 0), 0, wx.ALIGN_RIGHT)

        # Bouton inscription
        self.btn_equipe = ButtonInfo(self, id = ID_NOUVELLE_E,
                        bmp = images.bitmap('equipe.png'), kind = wx.ITEM_NORMAL,
                        shortHelp = "Inscription", longHelp = "Inscrire des équipes au tournoi.")

        self.btn_equipe.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(self.btn_equipe)
        self.controls.append(self.btn_equipe)

        # Bouton ajouter partie
        self.btn_partie = ButtonInfo(self, id = ID_NOUVELLE_P,
                        bmp = images.bitmap('partie.png'), kind = wx.ITEM_NORMAL,
                        shortHelp = "Nouvelle partie", longHelp = "Démarrer une nouvelle partie.")

        self.btn_partie.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(self.btn_partie)
        self.controls.append(self.btn_partie)

        # Bouton resultats
        self.btn_resultats = ButtonInfo(self, id = ID_RESULTATS,
                        bmp = images.bitmap('resultats.png'), kind = wx.ITEM_NORMAL,
                        shortHelp = "Résultats", longHelp = "Enregistrer le résultat d'une manche.")

        self.btn_resultats.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(self.btn_resultats)
        self.controls.append(self.btn_resultats)

        # Ajouter un espace
        self.AddSpacer((50, 0), 1, wx.ALL)

        # Bouton afficher informations
        self.btn_info = ButtonInfo(self, id = ID_INFO,
                        bmp = images.bitmap('info.png'), kind = wx.ITEM_CHECK,
                        shortHelp = "Informations", longHelp = "Afficher les informations relatives au tournoi en fonction de son statut.")

        self.btn_info.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(self.btn_info)
        self.controls.append(self.btn_info)

        # Chercher
        self.box_chercher = wx.SearchCtrl(self, wx.ID_FIND, size = (200, -1), style = wx.TE_PROCESS_ENTER)

        menu = wx.Menu()
        titres = [t[0] for t in grl.TITRES if t[0] != u""]
        for texte in titres:
            menu.Append(wx.ID_ANY, texte, "" , wx.ITEM_RADIO)
        self.box_chercher.SetMenu(menu)
        self.box_chercher.ShowCancelButton(True)

        self.AddControl(self.box_chercher, 0, wx.ALIGN_CENTER_VERTICAL)
        self.controls.append(self.box_chercher)

        # Ajouter un separateur
        self.AddSeparator()

        # Bouton Enregistrer
        btn = ButtonInfo(self, id = wx.ID_SAVE,
                        bmp = images.bitmap('enregistrer.png'), kind = wx.ITEM_NORMAL,
                        shortHelp = "Enregistrer", longHelp = "Enregistrer le tournoi en cours.")

        btn.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(btn)
        self.controls.append(btn)

        # Propiétés
        bpArt = self.GetBPArt()
        self.SetAlignment(bp.BP_ALIGN_RIGHT)

        bpArt.SetMetric(bp.BP_SEPARATOR_SIZE, 10)
        bpArt.SetMetric(bp.BP_MARGINS_SIZE, wx.Size(10, 3))
        bpArt.SetMetric(bp.BP_PADDING_SIZE, wx.Size(3, 0))
        bpArt.SetMetric(bp.BP_BORDER_SIZE, 2)

        bpArt.SetColour(bp.BP_TEXT_COLOUR, images.couleur('texte'))
        bpArt.SetColour(bp.BP_BORDER_COLOUR, images.couleur('bordure'))
        bpArt.SetColour(bp.BP_GRADIENT_COLOUR_FROM, images.couleur('gradient1'))
        bpArt.SetColour(bp.BP_GRADIENT_COLOUR_TO, images.couleur('gradient2'))
        bpArt.SetColour(bp.BP_BUTTONTEXT_COLOUR, images.couleur('texte_bouton'))
        bpArt.SetColour(bp.BP_SEPARATOR_COLOUR, bp.BrightenColour(images.couleur('separateur'), 0.85))
        bpArt.SetColour(bp.BP_SELECTION_BRUSH_COLOUR, images.couleur('selection'))
        bpArt.SetColour(bp.BP_SELECTION_PEN_COLOUR, wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVECAPTION))

        self.Thaw()
        self.DoLayout()

        self.box_chercher.Bind(wx.EVT_MENU, self._menu_recherche)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self._effacer_recherche)

    def _menu_recherche(self, event):
        menu = self.box_chercher.GetMenu()
        for i in range(menu.GetMenuItemCount()):
            item = menu.FindItemByPosition(i)
            if item.IsChecked():
                texte = item.GetLabel()
                index = i

        wx.PostEvent(self, evt.MenuRechercheEvent(self.GetId(), index, texte))

    def _effacer_recherche(self, event):
        self.box_chercher.Clear()

    def _rafraichir(self, etat, texte = ''):
        """
        NE PAS UTILISER !!!!! (Manipulé par la fenêtre principale)
        """
        styles = STYLES_MENU[etat]
        for st in styles:
            control = self.FindItemById(st)
            if control is not None:
                control.Enable(styles[st])
        self.SetBarText(texte)
        self.DoLayout()

    def partie(self):
        return int(float(self.txt_partie.GetLabelText()))

    def chg_partie(self, valeur = 0):
        self.txt_partie.SetLabel(unicode(valeur))

    def FindItemById(self, id):
        for control in self.controls:
            if control.GetId() == id:
                return control
        return None

class Voyant(object):
    def __init__(self, parent):
        self.parent = parent
        self.valeur = True

        self._vert = images.bitmap('vert.png')
        self._rouge = images.bitmap('rouge.png')
        self._image = wx.StaticBitmap(self.parent, wx.ID_ANY, self._vert)

    def change(self, valeur):
        if valeur == None:
            self.valeur = not self.valeur
        else:
            self.valeur = valeur

        if self.valeur == True:
            self._image.SetBitmap(self._rouge)
        else:
            self._image.SetBitmap(self._vert)

        self.Layout()

    def Layout(self):
        rect = self.parent.GetFieldRect(4)
        self._image.SetPosition((rect.x + 4, rect.y + 1))
        self.parent.Refresh()

class BarreEtat(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent)
        self.SetFieldsCount(5)
        self.SetStatusWidths([-1, 180, 140, 140, 35])
        self.SetStatusText(u"", 4)

        self._voyant_modif = Voyant(self)
        self.Bind(wx.EVT_SIZE, self.reDim, self)

    def _rafraichir(self, debut, equipes, parties , modifie):
        """
        NE PAS UTILISER !!!!! (Manipulé par la fenêtre principale)
        """
        self.SetStatusText(u"  Nombre de parties : %s" % parties, 3)
        self.SetStatusText(u"  Nombre d'équipes : %s" % equipes, 2)
        self.SetStatusText(u"  Début du tournoi : %s" % debut, 1)
        self._voyant_modif.change(modifie)

    def reDim(self, event):
        self._voyant_modif.Layout()
        event.Skip()
