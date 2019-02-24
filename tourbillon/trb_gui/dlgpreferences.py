#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import sys, os

import wx
from wx.lib import intctrl
from wx.lib import masked
from wx.lib import rcsizer
from wx.lib.agw import floatspin as flsp
from wx import grid

from tourbillon.trb_gui import dlgequipe as dlgeq

import tourbillon
from tourbillon import images
from tourbillon import configuration as cfg
from tourbillon.trb_core import tirages

#--- Variables globales --------------------------------------------------------

DEFAUT = cfg.TypedConfigParser()
_chemin_defaut = os.path.join(os.path.dirname(os.path.abspath(tourbillon.__file__)), 'defaut.cfg')
DEFAUT.read(_chemin_defaut)

#--- Fonctions -----------------------------------------------------------------

GRILLE_EDITEURS = {bool:(grid.GridCellBoolEditor, grid.GridCellBoolRenderer, ()),
                   int:(grid.GridCellNumberEditor, grid.GridCellNumberRenderer, ()),
                   float:(grid.GridCellFloatEditor, grid.GridCellFloatRenderer, (6, 2))}

#--- Classes -------------------------------------------------------------------

class GeneralPage(wx.Panel):
    def __init__(self, parent, config):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.section = "INTERFACE"

        # Boite encadrée
        box2 = wx.StaticBox(self, wx.ID_ANY, u"Enregistrement")
        box3 = wx.StaticBox(self, wx.ID_ANY, u"Affichage")

        # Chemin enregistrements
        txt_chemin_enregistrement = wx.StaticText(self, wx.ID_ANY, u"Chemin de sauvegarde par défaut : ")
        self.ctl_chemin_enregistrement = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.ctl_chemin_enregistrement.SetValue(os.path.expanduser(config.get(self.section, 'enregistrement')))
        btn_parcourir = wx.Button(self, wx.ID_ANY, u"Parcourir...")

        # Enregistrement automatique
        self.cbx_enregistrement_auto = wx.CheckBox(self, wx.ID_ANY, u"Enregistrement automatique")
        self.cbx_enregistrement_auto.SetValue(config.get_typed(self.section, 'enregistrement_auto'))

        # Demarrer en plein écran
        self.cbx_plein_ecran = wx.CheckBox(self, wx.ID_ANY, u"Démarrer TourBillon en plein écran")
        self.cbx_plein_ecran.SetValue(config.get_typed(self.section, 'plein_ecran'))

        # Afficher la fenêtre de preférences lors d'un nouveau tournoi
        self.cbx_nouveau_affiche_preferences = wx.CheckBox(self, wx.ID_ANY, u"Afficher les préférences lors d'un nouveau tournoi")
        self.cbx_nouveau_affiche_preferences.SetValue(config.get_typed(self.section, 'nouveau_affiche_preferences'))

        #position des objets
        sizer = wx.BoxSizer(wx.VERTICAL)

        boit1 = wx.BoxSizer(wx.HORIZONTAL)
        boit1.Add(txt_chemin_enregistrement, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        boit1.Add(self.ctl_chemin_enregistrement, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        boit1.Add(btn_parcourir, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)

        boit2 = wx.StaticBoxSizer(box2, wx.VERTICAL)
        boit2.AddSizer(boit1, 0, wx.EXPAND | wx.ALL, 5)
        boit2.Add(self.cbx_enregistrement_auto, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(boit2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        boit3 = wx.StaticBoxSizer(box3, wx.VERTICAL)
        boit3.Add(self.cbx_plein_ecran, 0, wx.ALL, 5)
        boit3.Add(self.cbx_nouveau_affiche_preferences, 0, wx.ALL, 5)
        sizer.Add(boit3, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.SetSizer(sizer)
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.parcourir, btn_parcourir)

    def parcourir(self, event):
        """
        Bouton Parcourir...
        """
        dlg = wx.DirDialog(self, u"Choisir le dossier d'enregistrement :", self.ctl_chemin_enregistrement.GetValue(), style = wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            self.ctl_chemin_enregistrement.SetValue(dlg.GetPath())
        dlg.Destroy()

    def donnees(self):
        """
        Récupérer les valeurs choisies par l'utilisateur.
        """
        return {'enregistrement':self.ctl_chemin_enregistrement.GetValue(),
                'enregistrement_auto':self.cbx_enregistrement_auto.GetValue(),
                'plein_ecran':self.cbx_plein_ecran.GetValue(),
                'nouveau_affiche_preferences':self.cbx_nouveau_affiche_preferences.GetValue()}

    def defaut(self):
        """
        Réinialiser les valeurs par défaut.
        """
        self.ctl_chemin_enregistrement.SetValue(os.path.expanduser(DEFAUT.get(self.section, 'enregistrement')))
        self.cbx_enregistrement_auto.SetValue(DEFAUT.get_typed(self.section, 'enregistrement_auto'))
        self.cbx_plein_ecran.SetValue(DEFAUT.get_typed(self.section, 'plein_ecran'))
        self.cbx_nouveau_affiche_preferences.SetValue(DEFAUT.get_typed(self.section, 'nouveau_affiche_preferences'))

class TournoiPage(wx.Panel):
    def __init__(self, parent, config):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.section = "TOURNOI"

        # Boite encadrée
        box1 = wx.StaticBox(self, wx.ID_ANY, u"Joueurs")
        box2 = wx.StaticBox(self, wx.ID_ANY, u"Equipes")
        box3 = wx.StaticBox(self, wx.ID_ANY, u"Manches")

        # Chemin historique joueurs
        txt_historique_joueurs = wx.StaticText(self, wx.ID_ANY, u"Fichier historique des joueurs : ")
        self.ctl_historique_joueurs = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.ctl_historique_joueurs.SetValue(os.path.expanduser(config.get(self.section, 'historique')))
        btn_parcourir = wx.Button(self, wx.ID_ANY, u"Parcourir...")

        # Completion des noms de joueurs
        self.cbx_joueur_completion = wx.CheckBox(self, wx.ID_ANY, u"Auto complétion des prénoms et noms des joueurs")
        self.cbx_joueur_completion.SetValue(config.get_typed(self.section, 'joueur_completion'))

        # Joueurs par équipes
        txt_joueurs_par_equipe = wx.StaticText(self, wx.ID_ANY, u"Nombre de joueurs par équipe : ")
        self.spn_joueurs_par_equipe = flsp.FloatSpin(self, wx.ID_ANY, min_val = 1, increment = 1, agwStyle = flsp.FS_CENTRE)
        self.spn_joueurs_par_equipe.SetFormat("%f")
        self.spn_joueurs_par_equipe.SetDigits(0)
        self.spn_joueurs_par_equipe.SetValue(config.get_typed(self.section, 'joueurs_par_equipe'))

        # Type de classement
        self.cbx_classement_duree = wx.CheckBox(self, wx.ID_ANY, u"Les équipes sont classées sen fonction de la durée moyenne d'une partie")
        self.cbx_classement_duree.SetValue(config.get_typed(self.section, 'classement_duree'))

        # Points par manche
        txt_points_par_manche = wx.StaticText(self, wx.ID_ANY, u"Nombre de points par manche : ")
        self.spn_points_par_manche = flsp.FloatSpin(self, wx.ID_ANY, min_val = 1, increment = 1, agwStyle = flsp.FS_CENTRE)
        self.spn_points_par_manche.SetFormat("%f")
        self.spn_points_par_manche.SetDigits(0)
        self.spn_points_par_manche.SetValue(config.get_typed(self.section, 'points_par_manche'))

        # Equipes par manche
        txt_equipes_par_manche = wx.StaticText(self, wx.ID_ANY, u"Nombre de d'équipes par manche : ")
        self.spn_equipes_par_manche = flsp.FloatSpin(self, wx.ID_ANY, min_val = 2, increment = 1, agwStyle = flsp.FS_CENTRE)
        self.spn_equipes_par_manche.SetFormat("%f")
        self.spn_equipes_par_manche.SetDigits(0)
        self.spn_equipes_par_manche.SetValue(config.get_typed(self.section, 'equipes_par_manche'))

        #position des objets
        sizer = wx.BoxSizer(wx.VERTICAL)

        boit1 = wx.BoxSizer(wx.HORIZONTAL)
        boit1.Add(txt_historique_joueurs, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        boit1.Add(self.ctl_historique_joueurs, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        boit1.Add(btn_parcourir, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)

        boit2 = wx.StaticBoxSizer(box1, wx.VERTICAL)
        boit2.AddSizer(boit1, 0, wx.EXPAND, 5)
        boit2.Add(self.cbx_joueur_completion, 0, wx.EXPAND | wx.TOP, 10)
        sizer.Add(boit2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        boit3 = wx.BoxSizer(wx.HORIZONTAL)
        boit3.Add(txt_joueurs_par_equipe, 1, wx.ALIGN_CENTER_VERTICAL)
        boit3.Add(self.spn_joueurs_par_equipe, 1)

        boit4 = wx.StaticBoxSizer(box2, wx.VERTICAL)
        boit4.AddSizer(boit3, 0, wx.EXPAND)
        boit4.Add(self.cbx_classement_duree, 0, wx.EXPAND | wx.TOP, 10)
        sizer.Add(boit4, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        boit5 = wx.BoxSizer(wx.HORIZONTAL)
        boit5.Add(txt_points_par_manche, 1, wx.ALIGN_CENTER_VERTICAL)
        boit5.Add(self.spn_points_par_manche, 1)

        boit6 = wx.BoxSizer(wx.HORIZONTAL)
        boit6.Add(txt_equipes_par_manche, 1, wx.ALIGN_CENTER_VERTICAL)
        boit6.Add(self.spn_equipes_par_manche, 1)

        boit7 = wx.StaticBoxSizer(box3, wx.VERTICAL)
        boit7.AddSizer(boit5, 0, wx.EXPAND)
        boit7.AddSizer(boit6, 0, wx.EXPAND)
        sizer.Add(boit7, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.SetSizer(sizer)
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.parcourir, btn_parcourir)

    def parcourir(self, event):
        """
        Bouton Parcourir...
        """
        dlg = wx.FileDialog(self, u"Choisir le fichier :", self.ctl_historique_joueurs.GetValue(), style = wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            self.ctl_historique_joueurs.SetValue(dlg.GetPath())
        dlg.Destroy()

    def donnees(self):
        """
        Récupérer les valeurs choisies par l'utilisateur.
        """
        return {'historique_joueurs':self.ctl_historique_joueurs.GetValue(),
                'points_par_manche':int(self.spn_points_par_manche.GetValue()),
                'joueurs_par_equipe':int(self.spn_joueurs_par_equipe.GetValue()),
                'equipes_par_manche':int(self.spn_equipes_par_manche.GetValue()),
                'classement_duree':self.cbx_classement_duree.GetValue(),
                'joueur_completion':self.cbx_joueur_completion.GetValue()}

    def defaut(self):
        """
        Réinialiser les valeurs par défaut.
        """
        self.ctl_historique_joueurs.SetValue(os.path.expanduser(DEFAUT.get(self.section, 'historique')))
        self.spn_points_par_manche.SetValue(DEFAUT.get_typed(self.section, 'points_par_manche'))
        self.spn_joueurs_par_equipe.SetValue(DEFAUT.get_typed(self.section, 'joueurs_par_equipe'))
        self.spn_equipes_par_manche.SetValue(DEFAUT.get_typed(self.section, 'equipes_par_manche'))
        self.cbx_classement_duree.SetValue(DEFAUT.get_typed(self.section, 'classement_duree'))
        self.cbx_joueur_completion.SetValue(DEFAUT.get_typed(self.section, 'joueur_completion'))

class GrilleOptionsTirages(wx.Panel):
    def __init__(self, parent, config, section):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.section = section

        self.grille = grid.Grid(self, wx.ID_ANY)
        self.grille.SetRowLabelSize(0)
        self.grille.SetDefaultCellBackgroundColour(images.couleur('grille'))
        nb_lignes = len(config.get_options(self.section))
        self.grille.CreateGrid(nb_lignes, 2)

        # Entête
        self.grille.SetColLabelValue(0, u"Paramètre")
        self.grille.SetColSize(0, 370)
        self.grille.SetColLabelValue(1, u"Valeur")
        self.grille.SetColSize(1, 170)

        i = 0
        config = config.get_options(self.section)
        parametres = config.keys()
        parametres.sort()
        for nom in parametres:
            valeur = config[nom]
            # Nom de le variable
            self.grille.SetCellValue(i, 0, nom)
            attr = grid.GridCellAttr()
            attr.SetReadOnly(True)
            self.grille.SetColAttr(0, attr)

            # Valeur de la variable
            EditorClass, RendererClass, args = GRILLE_EDITEURS[type(valeur)]
            RendererClass.type = type(valeur)
            self.grille.SetCellEditor(i, 1, EditorClass())
            self.grille.SetCellRenderer(i, 1, RendererClass(*args))

            if RendererClass.type == bool:
                if valeur == True:
                    valeur = 1
                else:
                    valeur = ''
                attr = grid.GridCellAttr()
                attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
                self.grille.SetColAttr(1, attr)

            self.grille.SetCellValue(i, 1, unicode(valeur))
            i += 1

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.grille, 1, wx.EXPAND | wx.LEFT, 15)
        self.SetSizer(box)

    def type(self, ligne):
        return self.grille.GetCellRenderer(ligne, 1).type

    def donnees(self):
        """
        Récupérer les valeurs choisies par l'utilisateur.
        """
        d = {}
        i = 0
        while i < self.grille.GetNumberRows():
            valeur = self.grille.GetCellValue(i, 1)
            d[self.grille.GetCellValue(i, 0)] = unicode(self.type(i)(valeur))
            i += 1
        return d

    def defaut(self):
        """
        Réinialiser les valeurs par défaut.
        """
        i = 0
        while i < self.grille.GetNumberRows():
            valeur = DEFAUT.get_typed(self.section, self.grille.GetCellValue(i, 0))
            if type(valeur) == bool:
                if valeur == True:
                    valeur = 1
                else:
                    valeur = ''
            self.grille.SetCellValue(i, 1, unicode(valeur))
            i += 1

class TiragePage(wx.Panel):
    def __init__(self, parent, config):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.section = "TIRAGE"
        self.pages = []

        self.choicebook = wx.Choicebook(self, wx.ID_ANY)

        modules = tirages.__modules__.keys()
        modules.sort()
        for tirage in modules:
            page = GrilleOptionsTirages(self.choicebook, config, self.section + "_" + tirage.upper())
            self.pages.append(page)
            self.choicebook.AddPage(page, tirage)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.choicebook, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(box)

    def donnees(self):
        """
        Récupérer les valeurs choisies par l'utilisateur.
        """
        d = {}
        for page in self.pages:
            d[page.section] = page.donnees()
        return d

    def defaut(self):
        """
        Réinialiser les valeurs par défaut.
        """
        page = self.choicebook.GetCurrentPage()
        page.defaut()

class AffichagePage(wx.Panel):
    def __init__(self, parent, config):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.section = "INFO_EQUIPE"
        texte1 = wx.StaticText(self, -1, u"          En cours de construction...")

    def donnees(self):
        """
        Récupérer les valeurs choisies par l'utilisateur.
        """
        return {}

    def defaut(self):
        """
        Réinialiser les valeurs par défaut.
        """
        pass

class DialoguePreferences(wx.Dialog):
    def __init__(self, parent, config, page = 0):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, u"Préférences TourBillon", size = (600, 460))
        self.SetBackgroundColour(wx.Colour(226, 226, 226))
        self.CenterOnParent(wx.BOTH)
        self.config = config

        self.notebook = wx.Listbook(self, wx.ID_ANY, style = wx.LB_TOP)

        # Liste des images
        il = wx.ImageList(32, 32)
        il.Add(images.bitmap('opt_general.png'))
        il.Add(images.bitmap('opt_tournoi.png'))
        il.Add(images.bitmap('opt_tirage.png'))
        il.Add(images.bitmap('opt_affichage.png'))
        self.notebook.AssignImageList(il)

        # Création des pages
        self.page0 = GeneralPage(self.notebook, self.config)
        self.notebook.AddPage(self.page0, u"   Général   ", imageId = 0)
        self.page1 = TournoiPage(self.notebook, self.config)
        self.notebook.AddPage(self.page1, u"   Tournoi   ", imageId = 1)
        self.page2 = TiragePage(self.notebook, self.config)
        self.notebook.AddPage(self.page2, u"   Tirages   ", imageId = 2)
        self.page3 = AffichagePage(self.notebook, self.config)
        self.notebook.AddPage(self.page3, u"Infos équipes", imageId = 3)

        # Bouttons
        self.btn_defaut = wx.Button(self, wx.ID_DEFAULT, u"Défaut", size = (100, 25))
        self.btn_enregistrer = wx.Button(self, wx.ID_OK, u"Enregistrer", size = (100, 25))
        self.btn_enregistrer.SetDefault()
        self.btn_annuler = wx.Button(self, wx.ID_CANCEL, u"Annuler", size = (100, 25))

        # Position des objets
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.notebook, 1, wx.EXPAND)

        boit1 = wx.BoxSizer(wx.HORIZONTAL)
        boit1.Add(self.btn_defaut, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        boit1.Add((10, 10), 1)
        boit1.Add(self.btn_annuler, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        boit1.Add(self.btn_enregistrer, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        sizer.Add(boit1, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)
        self.Layout()
        self.notebook.SetSelection(page)

        self.Bind(wx.EVT_BUTTON, self.defaut, self.btn_defaut)

    def donnees(self):
        d = {self.page0.section:self.page0.donnees(),
             self.page1.section:self.page1.donnees()}

        d.update(self.page2.donnees())

        return d

    def defaut(self, event):
        page = self.notebook.GetCurrentPage()
        page.defaut()
