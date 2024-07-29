# -*- coding: UTF-8 -*-

import wx
from wx.lib.agw import buttonpanel as bp
from tourbillon import images

from tourbillon.gui import evenements as evt
from tourbillon.gui import grille as grl
from tourbillon.core import constantes as cst
from tourbillon.core import tournoi

ID_STATISTIQUES = wx.NewId()
ID_INFO = wx.NewId()
ID_TIRAGE = wx.NewId()
ID_SHELL = wx.NewId()
ID_NOUVELLE_E = wx.NewId()
ID_MODIFIER_E = wx.NewId()
ID_SUPPRIMER_E = wx.NewId()
ID_NOUVELLE_P = wx.NewId()
ID_SUPPRIMER_P = wx.NewId()
ID_RESULTATS = wx.NewId()
ID_INSCRIPTION = wx.NewId()
ID_PARTIE = wx.NewId()
ID_CLASSEMENT = wx.NewId()

STYLES_MENU = {None: {wx.ID_SAVE: False,
                      wx.ID_SAVEAS: False,
                      wx.ID_PRINT: False,
                      wx.ID_PREVIEW_PRINT: False,
                      ID_INFO: False,
                      ID_TIRAGE: False,
                      ID_INSCRIPTION: False,
                      ID_NOUVELLE_E: False,
                      ID_MODIFIER_E: False,
                      ID_SUPPRIMER_E: False,
                      ID_PARTIE: False,
                      ID_NOUVELLE_P: False,
                      ID_RESULTATS: False,
                      ID_CLASSEMENT: False},

               '0 equipe': {wx.ID_SAVE: True,
                            wx.ID_SAVEAS: True,
                            wx.ID_PRINT: False,
                            wx.ID_PREVIEW_PRINT: False,
                            ID_INFO: True,
                            ID_TIRAGE: False,
                            ID_INSCRIPTION: True,
                            ID_NOUVELLE_E: True,
                            ID_MODIFIER_E: False,
                            ID_SUPPRIMER_E: False,
                            ID_PARTIE: False,
                            ID_NOUVELLE_P: False,
                            ID_RESULTATS: False,
                            ID_CLASSEMENT: False},

               cst.T_INSCRIPTION: {wx.ID_SAVE: True,
                                   wx.ID_SAVEAS: True,
                                   wx.ID_PRINT: False,
                                   wx.ID_PREVIEW_PRINT: False,
                                   ID_INFO: True,
                                   ID_TIRAGE: False,
                                   ID_INSCRIPTION: True,
                                   ID_NOUVELLE_E: True,
                                   ID_MODIFIER_E: True,
                                   ID_SUPPRIMER_E: True,
                                   ID_PARTIE: False,
                                   ID_CLASSEMENT: False},

               '0 partie': {wx.ID_SAVE: True,
                            wx.ID_SAVEAS: True,
                            wx.ID_PRINT: True,
                            wx.ID_PREVIEW_PRINT: True,
                            ID_INFO: True,
                            ID_TIRAGE: False,
                            ID_INSCRIPTION: True,
                            ID_NOUVELLE_E: True,
                            ID_MODIFIER_E: True,
                            ID_SUPPRIMER_E: True,
                            ID_PARTIE: True,
                            ID_NOUVELLE_P: True,
                            ID_RESULTATS: False,
                            ID_SUPPRIMER_P: False,
                            ID_CLASSEMENT: True},

               cst.T_ATTEND_TIRAGE: {wx.ID_SAVE: True,
                                     wx.ID_SAVEAS: True,
                                     wx.ID_PRINT: True,
                                     wx.ID_PREVIEW_PRINT: True,
                                     ID_INFO: True,
                                     ID_TIRAGE: True,
                                     ID_INSCRIPTION: True,
                                     ID_NOUVELLE_E: True,
                                     ID_MODIFIER_E: True,
                                     ID_SUPPRIMER_E: False,
                                     ID_PARTIE: True,
                                     ID_NOUVELLE_P: True,
                                     ID_RESULTATS: True,
                                     ID_SUPPRIMER_P: True,
                                     ID_CLASSEMENT: True},

               cst.T_PARTIE_EN_COURS: {wx.ID_SAVE: True,
                                       wx.ID_SAVEAS: True,
                                       wx.ID_PRINT: True,
                                       wx.ID_PREVIEW_PRINT: True,
                                       ID_INFO: True,
                                       ID_TIRAGE: True,
                                       ID_INSCRIPTION: True,
                                       ID_NOUVELLE_E: True,
                                       ID_MODIFIER_E: True,
                                       ID_SUPPRIMER_E: False,
                                       ID_PARTIE: True,
                                       ID_NOUVELLE_P: False,
                                       ID_RESULTATS: True,
                                       ID_SUPPRIMER_P: True,
                                       ID_CLASSEMENT: True}}


#--- Hack pour ButtonInfo -----------------------------------------------------


class ButtonInfo(bp.ButtonInfo):

    def __init__(self, parent, id=wx.ID_ANY, bmp=wx.NullBitmap,
                 status="Normal", text="", kind=wx.ITEM_NORMAL, shortHelp="", longHelp=""):
        bp.ButtonInfo.__init__(self, parent, id, bmp, status, text, kind, shortHelp, longHelp)

        if id == wx.ID_ANY:
            self._id = wx.NewId()
        else:
            self._id = id

    def Enable(self, enable=True):
        if enable:
            self.SetStatus('Normal')
        else:
            self.SetStatus('Disabled')

    def Check(self, checked=True):
        if self.GetKind() == wx.ITEM_CHECK:
            if checked:
                self.SetToggled(True)
                self.SetStatus('Toggled')
            else:
                self.SetToggled(False)
                self.SetStatus('Normal')


class Menu(wx.Menu):

    def ajouter(self, id, text, help="", kind=wx.ITEM_NORMAL, bpm=None):
        sous_menu = wx.MenuItem(self, id, text, help, kind)
        if bpm:
            sous_menu.SetBitmap(bpm)
        self.AppendItem(sous_menu)


def styles():
    t = tournoi.tournoi()
    if t is None:
        etat = None
    else:
        if t.statut == cst.T_INSCRIPTION and t.nb_equipes() == 0:
            etat = '0 equipe'
        elif t.statut == cst.T_ATTEND_TIRAGE and t.nb_parties() == 0:
            etat = '0 partie'
        else:
            etat = t.statut
    return STYLES_MENU[etat]


def cree_contexte_menu():
    menu = Menu()
    menu.ajouter(ID_RESULTATS, "&Entrer les résultats", "  Entrer les résultats des manches de la partie en cours",
                 bpm=images.bitmap('resultats.png', scale=0.5))
    menu.ajouter(ID_MODIFIER_E, "&Modifier", "  Modifier les données d'une équipe",
                 bpm=images.bitmap('modifier.png', scale=0.5))
    menu.ajouter(ID_NOUVELLE_E, "&Nouvelle\tCtrl+E", "  Inscrire une nouvelle équipe au tournoi",
                 bpm=images.bitmap('equipe.png', scale=0.5))
    menu.ajouter(ID_SUPPRIMER_E, "&Supprimer", "  Supprimer une équipe du tournoi",
                 bpm=images.bitmap('supprimer.png', scale=0.5))

    for st, val in styles().items():
        item = menu.FindItemById(st)
        if item:
            item.Enable(val)
    return menu


class BarreMenu(wx.MenuBar):

    def __init__(self, parent):
        wx.MenuBar.__init__(self)

        # Menu fichier
        self.menu_fichier = Menu()
        self.menu_fichier.ajouter(wx.ID_NEW, "&Nouveau\tCtrl+N", "  Commencer un nouveau tournoi",
                                  bpm=images.bitmap('nouveau.png', scale=0.5))
        self.menu_fichier.ajouter(wx.ID_OPEN, "&Ouvrir...\tCtrl+O", "  Ouvrir un tournoi",
                                  bpm=images.bitmap('ouvrir.png', scale=0.5))
        self.menu_fichier.AppendSeparator()
        self.menu_fichier.ajouter(wx.ID_SAVE, "&Enregistrer\tCtrl+S", "  Enregistrer le fichier ouvert",
                                  bpm=images.bitmap('enregistrer.png', scale=0.5))
        self.menu_fichier.ajouter(wx.ID_SAVEAS, "&Enregistrer sous...", "  Enregistrer le fichier ouvert",
                                  bpm=images.bitmap('enregistrer_sous.png', scale=0.5))
        self.menu_fichier.AppendSeparator()
        self.menu_fichier.ajouter(wx.ID_PREVIEW_PRINT, "&Apreçu avant impression", "  Visualiser le classement avant impression",
                                  bpm=images.bitmap('loupe.png', scale=0.5))
        self.menu_fichier.ajouter(wx.ID_PRINT, "&Imprimer...\tCtrl+I", "  Imprimer le classement des équipes",
                                  bpm=images.bitmap('imprimer.png', scale=0.5))
        self.menu_fichier.AppendSeparator()
        self.menu_fichier.ajouter(wx.ID_EXIT, "&Quitter\tCtrl+Q", "  Quitter TourBillon",
                                  bpm=images.bitmap('quitter.png', scale=0.5))

        # Menu affichage
        self.menu_affichage = wx.Menu()
        self.menu_affichage.Append(ID_STATISTIQUES, "Statistiques tournoi", "  Afficher les statistiques du tournoi", wx.ITEM_CHECK)
        self.menu_affichage.Append(ID_INFO, "&Infos Equipes", "  Afficher les informations des joueurs", wx.ITEM_CHECK)
        self.menu_affichage.Append(ID_TIRAGE, "&Tirages", "  Afficher les tirages")
        self.menu_affichage.AppendSeparator()
        self.menu_affichage.Append(ID_SHELL, "Shell Python", "  Afficher un shell Python pour le débogage", wx.ITEM_CHECK)

        # Menu Tournoi
        self.sous_menu_inscription = Menu()
        self.sous_menu_inscription.ajouter(ID_NOUVELLE_E, "&Nouvelle\tCtrl+E", "  Inscrire une nouvelle équipe au tournoi",
                                           bpm=images.bitmap('equipe.png', scale=0.5))
        self.sous_menu_inscription.ajouter(ID_MODIFIER_E, "&Modifier", "  Modifier les données d'une équipe",
                                           bpm=images.bitmap('modifier.png', scale=0.5))
        self.sous_menu_inscription.ajouter(ID_SUPPRIMER_E, "&Supprimer", "  Supprimer une équipe du tournoi",
                                           bpm=images.bitmap('supprimer.png', scale=0.5))

        self.sous_menu_partie = Menu()
        self.sous_menu_partie.ajouter(ID_NOUVELLE_P, "&Nouvelle\tCtrl+P", "  Lancer une nouvelle partie",
                                      bpm=images.bitmap('partie.png', scale=0.5))
        self.sous_menu_partie.ajouter(ID_RESULTATS, "&Entrer les résultats", "  Entrer les résultats des manches de la partie en cours",
                                      bpm=images.bitmap('resultats.png', scale=0.5))
        self.sous_menu_partie.ajouter(ID_SUPPRIMER_P, "&Supprimer", "  Supprimer une partie",
                                      bpm=images.bitmap('supprimer.png', scale=0.5))

        self.menu_tournoi = Menu()
        self.menu_tournoi.AppendMenu(ID_INSCRIPTION, "&Equipes", self.sous_menu_inscription)
        self.menu_tournoi.AppendMenu(ID_PARTIE, "&Parties", self.sous_menu_partie)
        self.menu_tournoi.Append(ID_CLASSEMENT, "&Classement", "  Afficher le classement")
        self.menu_tournoi.AppendSeparator()
        self.menu_tournoi.ajouter(wx.ID_PREFERENCES, "&Préférences\tCtrl+,", " Configuration de l'application",
                                  bpm=images.bitmap('preferences.png', scale=0.5))

        # Menu Aide
        self.menu_aide = Menu()
        self.menu_aide.ajouter(wx.ID_PROPERTIES, "Information Système", " Configuration du système hôte de TourBillon...",
                               bpm=images.bitmap('systeme.png', scale=0.5))
        self.menu_aide.ajouter(wx.ID_ABOUT, "&A propos de TourBillon", " Pour en savoir plus...",
                               bpm=images.bitmap('icon.png', scale=0.6))

        self.Append(self.menu_fichier, "&Fichier")
        self.Append(self.menu_affichage, "&Affichage")
        self.Append(self.menu_tournoi, "&Tournoi")
        self.Append(self.menu_aide, "&Aide")

    def _rafraichir(self):
        """
        NE PAS UTILISER !!!!! (Manipulé par la fenêtre principale)
        """
        for st, val in styles().items():
            item = self.FindItemById(st)
            item.Enable(val)

        self.Update()


class BarreBouton(bp.ButtonPanel):

    def __init__(self, parent):
        bp.ButtonPanel.__init__(self, parent, wx.ID_ANY, text="",
                                agwStyle=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)
        self.controls = []

        self.Freeze()
        # Bouton partie précédente
        self.btn_precedente = ButtonInfo(self, id=wx.ID_ANY,
                                         bmp=images.bitmap('precedent.png'), kind=wx.ITEM_NORMAL,
                                         shortHelp="Précédente", longHelp="Afficher les données de la partie précédente.")

        self.btn_precedente.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(self.btn_precedente)
        self.controls.append(self.btn_precedente)

        # Partie affichée
        self.txt_partie = wx.StaticText(self, id=wx.ID_ANY, label="0",
                                        size=(50, -1), style=wx.ALIGN_CENTER)
        self.txt_partie.SetToolTipString("Partie affichée")
        font = wx.Font(35, wx.SWISS, wx.NORMAL, wx.BOLD, False, "Impact")

        self.txt_partie.SetFont(font)
        self.txt_partie.SetForegroundColour(wx.Colour(144, 65, 21))
        self.AddControl(self.txt_partie)

        # Bouton partie suivante
        self.btn_suivante = ButtonInfo(self, id=wx.ID_ANY,
                                       bmp=images.bitmap('suivant.png'), kind=wx.ITEM_NORMAL,
                                       shortHelp="Suivante", longHelp="Afficher les données de la partie suivante.")

        self.btn_suivante.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(self.btn_suivante)
        self.controls.append(self.btn_suivante)

        # Ajouter un espace
        self.AddSpacer((100, 0), 0, wx.ALIGN_RIGHT)

        # Bouton inscription
        self.btn_equipe = ButtonInfo(self, id=ID_NOUVELLE_E,
                                     bmp=images.bitmap('equipe.png'), kind=wx.ITEM_NORMAL,
                                     shortHelp="Inscription", longHelp="Inscrire des équipes au tournoi.")

        self.btn_equipe.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(self.btn_equipe)
        self.controls.append(self.btn_equipe)

        # Bouton ajouter partie
        self.btn_partie = ButtonInfo(self, id=ID_NOUVELLE_P,
                                     bmp=images.bitmap('partie.png'), kind=wx.ITEM_NORMAL,
                                     shortHelp="Nouvelle partie", longHelp="Démarrer une nouvelle partie.")

        self.btn_partie.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(self.btn_partie)
        self.controls.append(self.btn_partie)

        # Bouton resultats
        self.btn_resultats = ButtonInfo(self, id=ID_RESULTATS,
                                        bmp=images.bitmap('resultats.png'), kind=wx.ITEM_NORMAL,
                                        shortHelp="Résultats", longHelp="Enregistrer le résultat d'une manche.")

        self.btn_resultats.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(self.btn_resultats)
        self.controls.append(self.btn_resultats)

        # Ajouter un espace
        self.AddSpacer((50, 0), 1, wx.ALL)

        # Bouton afficher informations
        self.btn_info = ButtonInfo(self, id=ID_INFO,
                                   bmp=images.bitmap('info.png'), kind=wx.ITEM_CHECK,
                                   shortHelp="Informations", longHelp="Afficher les informations relatives au tournoi en fonction de son statut.")

        self.btn_info.SetTextAlignment(bp.BP_BUTTONTEXT_ALIGN_RIGHT)
        self.AddButton(self.btn_info)
        self.controls.append(self.btn_info)

        # Chercher
        self.box_chercher = wx.SearchCtrl(self, wx.ID_FIND, size=(200, -1), style=wx.TE_PROCESS_ENTER)

        menu = wx.Menu()
        titres = [t[0] for t in grl.TITRES['partie'] if t[0] != ""] + [t[0] for t in grl.TITRES['statistiques'] if t[0] != ""]
        for texte in titres:
            menu.Append(wx.ID_ANY, texte, "", wx.ITEM_RADIO)
        self.box_chercher.SetMenu(menu)
        self.box_chercher.ShowCancelButton(True)

        self.AddControl(self.box_chercher, 0, wx.ALIGN_CENTER_VERTICAL)
        self.controls.append(self.box_chercher)

        # Ajouter un separateur
        self.AddSeparator()

        # Bouton Enregistrer
        btn = ButtonInfo(self, id=wx.ID_SAVE,
                         bmp=images.bitmap('enregistrer.png'), kind=wx.ITEM_NORMAL,
                         shortHelp="Enregistrer", longHelp="Enregistrer le tournoi en cours.")

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
        self.Bind(wx.EVT_SIZE, self._force_layout)

    def _force_layout(self, event):
        """
        Fix un bug sous win32: le widget de recherche n'est pas correctement
        positionné lors d'un redimensionnement de la fenêtre si la mise en
        page n'est pas forcée.
        """
        self.Layout()
        self.Refresh()
        event.Skip()

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
        self.Refresh()

    def _rafraichir(self, texte=''):
        """
        NE PAS UTILISER !!!!! (Manipulé par la fenêtre principale)
        """
        for st in styles():
            control = self.FindItemById(st)
            if control is not None:
                control.Enable(styles()[st])
        self.SetBarText(texte)
        self.DoLayout()
        self.txt_partie.Refresh()
        self.Refresh()

    def numero(self):
        return int(float(self.txt_partie.GetLabelText()))

    def chg_partie(self, valeur=0):
        self.txt_partie.SetLabel(str(valeur))
        self.Refresh()

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
        if valeur is None:
            self.valeur = not self.valeur
        else:
            self.valeur = valeur

        if self.valeur is True:
            self._image.SetBitmap(self._rouge)
        else:
            self._image.SetBitmap(self._vert)

        self.Layout()

    def Layout(self):
        rect = self.parent.GetFieldRect(5)
        self._image.SetPosition((rect.x + 5, rect.y + 1))
        self.parent.Refresh()


class BarreEtat(wx.StatusBar):

    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent)
        self.SetFieldsCount(6)
        self.SetStatusWidths([-1, 180, 100, 100, 200, 35])
        self.SetStatusText("", 5)

        self._voyant_modif = Voyant(self)
        self.Bind(wx.EVT_SIZE, self.reDim, self)

    def _rafraichir(self, debut, parties, equipes, manches_incompletes, modifie):
        """
        NE PAS UTILISER !!!!! (Manipulé par la fenêtre principale)
        """
        self.SetStatusText("  Manches incompletes : %s" % manches_incompletes, 4)
        self.SetStatusText("  Equipes : %s" % equipes, 3)
        self.SetStatusText("  Parties : %s" % parties, 2)
        self.SetStatusText("  Début du tournoi : %s" % debut, 1)
        self._voyant_modif.change(modifie)

    def reDim(self, event):
        self._voyant_modif.Layout()
        event.Skip()
