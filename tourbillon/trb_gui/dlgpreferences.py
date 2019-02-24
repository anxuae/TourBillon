#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import sys, os
from functools import partial

import wx
from wx.lib import intctrl
from wx.lib import masked
from wx.lib import rcsizer
from wx.lib import buttons
from wx.lib.agw import floatspin as flsp
from wx import grid
import shutil

from tourbillon.trb_gui import dlgequipe as dlgeq

import tourbillon
from tourbillon import images
from tourbillon.trb_gui.dlginformations import VARIABLES, DialogueInformations, string_en_wxFont, wxFont_en_string
from tourbillon import configuration as cfg
from tourbillon.trb_core import tirages

#--- Variables globales --------------------------------------------------------

GRILLE_EDITEURS = {bool:(grid.GridCellBoolEditor, grid.GridCellBoolRenderer, ()),
                   int:(grid.GridCellNumberEditor, grid.GridCellNumberRenderer, ()),
                   float:(grid.GridCellFloatEditor, grid.GridCellFloatRenderer, (6, 2))}

#--- Fonctions ----------------------------------------------------------------

def selectioner_variable(event, ctl_texte):
    dlg = wx.SingleChoiceDialog(ctl_texte, "Ces  variables sont  mises à jour au fure et à mesure\n"
                                "de l'avancement du tournoi.",
                                'Selectionner une variable',
                                sorted(VARIABLES.keys()), wx.CHOICEDLG_STYLE)

    if dlg.ShowModal() == wx.ID_OK:
        ctl_texte.SetValue(ctl_texte.GetValue() + '%(' + dlg.GetStringSelection() + ')s')

#--- Classes -------------------------------------------------------------------

class PoliceBouton(wx.Button):
    def __init__(self, parent, init_police=wx.NullFont, init_couleur=wx.NullColour, **kwargs):
        wx.Button.__init__(self, parent, **kwargs)
        self.police = init_police
        self.couleur = init_couleur
        self._maj()

        self.Bind(wx.EVT_BUTTON, self.select_police)

    def _maj(self):
        self.SetLabel(self.police.GetFaceName())

    def select_police(self, event):
        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour(self.couleur)
        data.SetInitialFont(self.police)

        dlg = wx.FontDialog(self, data)
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            data = dlg.GetFontData()
            self.police = data.GetChosenFont()
            self.couleur = data.GetColour()
            self._maj()
        event.Skip()

    def chg_police(self, police):
        self.police = police
        self._maj()

    def chg_police_desc(self, police_desc):
        self.police = string_en_wxFont(police_desc)
        self._maj()

    def chg_couleur(self, couleur):
        self.couleur = couleur

class TimeSlider(wx.Panel):
    def __init__(self, parent, id= -1, value=0, minValue=0, maxValue=100, increment=1,
                 pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SL_HORIZONTAL):
        wx.Panel.__init__(self, parent, id, pos, size)
        self.increment = int(increment)
        self.slider = wx.Slider(self, -1, value, minValue, maxValue, style=style)
        self.txt_valeur = wx.StaticText(self, wx.ID_ANY, u"", style=wx.ALIGN_CENTER)
        self.txt_valeur.SetMinSize((50, -1))

        #position des objets
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(self.slider, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.txt_valeur, 0, wx.EXPAND)

        self.SetSizer(sizer)
        self.Layout()

        self.Bind(wx.EVT_SCROLL, self.maj_texte, self.slider)

        self.maj_texte(None)

    def maj_texte(self, event):
        valeur = int(round(self.slider.GetValue() / float(self.increment))) * self.increment
        self.slider.SetValue(valeur)
        sec = valeur / 1000.
        if sec - int(sec) == 0:
            sec = int(sec)
        min = (int(sec) - (int(sec) % 60)) / 60
        texte = ""
        if min > 0:
            texte += "%sm" % min
            sec = sec - min * 60
        if sec > 0 or min <= 0:
            texte += "%ss" % sec
        self.txt_valeur.SetLabel(texte)

        if event is not None:
            event.Skip()

    def SetTickFreq(self, value):
        self.slider.SetTickFreq(value)

    def GetValue(self):
        return self.slider.GetValue()

    def SetValue(self, value):
        self.slider.SetValue(value)
        self.maj_texte(None)

class GeneralPage(wx.Panel):
    def __init__(self, parent, section, config):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.section = section

        # Boite encadrée
        box2 = wx.StaticBox(self, wx.ID_ANY, u"Enregistrement")
        box3 = wx.StaticBox(self, wx.ID_ANY, u"Affichage")

        # Chemin enregistrements
        txt_chemin_enregistrement = wx.StaticText(self, wx.ID_ANY, u"Chemin de sauvegarde par défaut : ")
        self.ctl_chemin_enregistrement = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.ctl_chemin_enregistrement.SetValue(os.path.expanduser(config.get(self.section, 'ENREGISTREMENT')))
        btn_parcourir = wx.Button(self, wx.ID_ANY, u"Parcourir...")

        # Enregistrement automatique
        self.cbx_enregistrement_auto = wx.CheckBox(self, wx.ID_ANY, u"Enregistrement automatique")
        self.cbx_enregistrement_auto.SetValue(config.get_typed(self.section, 'ENREGISTREMENT_AUTO'))

        # Demarrer en plein écran
        self.cbx_plein_ecran = wx.CheckBox(self, wx.ID_ANY, u"Démarrer TourBillon en plein écran")
        self.cbx_plein_ecran.SetValue(config.get_typed(self.section, 'PLEIN_ECRAN'))

        # Afficher la fenêtre de preférences lors d'un nouveau tournoi
        self.cbx_nouveau_affiche_preferences = wx.CheckBox(self, wx.ID_ANY, u"Afficher les préférences lors d'un nouveau tournoi")
        self.cbx_nouveau_affiche_preferences.SetValue(config.get_typed(self.section, 'NOUVEAU_AFFICHE_PREFERENCES'))

        # Interface bavarde
        self.cbx_bavarde = wx.CheckBox(self, wx.ID_ANY, u"Interface bavarde")
        self.cbx_bavarde.SetValue(config.get_typed(self.section, 'BAVARDE'))

        # image de fond
        txt_chemin_fond = wx.StaticText(self, wx.ID_ANY, u"Image de fond : ")
        self.ctl_chemin_fond = wx.TextCtrl(self, wx.ID_ANY, u"")
        nom = config.get_typed(self.section, 'IMAGE')
        if not nom:
            nom = u""
        self.ctl_chemin_fond.SetValue(nom)
        btn_parcourir_fond = wx.Button(self, wx.ID_ANY, u"Parcourir...")

        #position des objets
        sizer = wx.BoxSizer(wx.VERTICAL)

        boit1 = wx.BoxSizer(wx.HORIZONTAL)
        boit1.Add(txt_chemin_enregistrement, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        boit1.Add(self.ctl_chemin_enregistrement, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        boit1.Add(btn_parcourir, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)

        boit2 = wx.StaticBoxSizer(box2, wx.VERTICAL)
        boit2.AddSizer(boit1, 0, wx.EXPAND | wx.ALL, 5)
        boit2.Add(self.cbx_enregistrement_auto, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(boit2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        boit3 = wx.BoxSizer(wx.HORIZONTAL)
        boit3.Add(txt_chemin_fond, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        boit3.Add(self.ctl_chemin_fond, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        boit3.Add(btn_parcourir_fond, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)

        boit4 = wx.StaticBoxSizer(box3, wx.VERTICAL)
        boit4.AddSizer(boit3, 0, wx.EXPAND | wx.ALL, 5)
        boit4.Add(self.cbx_plein_ecran, 0, wx.ALL, 5)
        boit4.Add(self.cbx_bavarde, 0, wx.ALL, 5)
        boit4.Add(self.cbx_nouveau_affiche_preferences, 0, wx.ALL, 5)
        sizer.Add(boit4, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.SetSizer(sizer)
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.parcourir, btn_parcourir)
        self.Bind(wx.EVT_BUTTON, self.parcourir_fond, btn_parcourir_fond)

    def parcourir(self, event):
        """
        Bouton Parcourir...
        """
        dlg = wx.DirDialog(self, u"Choisir le dossier d'enregistrement :", self.ctl_chemin_enregistrement.GetValue(), style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            self.ctl_chemin_enregistrement.SetValue(dlg.GetPath())
        dlg.Destroy()

    def parcourir_fond(self, event):
        """
        Bouton Parcourir fond de l'écran...
        """
        dlg = wx.FileDialog(self, u"Choisir Une image de fond :", self.ctl_chemin_fond.GetValue(), style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            self.ctl_chemin_fond.SetValue(dlg.GetPath())
        dlg.Destroy()

    def donnees(self):
        """
        Récupérer les valeurs choisies par l'utilisateur.
        """
        chemin_image = self.ctl_chemin_fond.GetValue()
        if chemin_image != "":
            _, ext = os.path.splitext(chemin_image)
            destination = os.path.join(cfg.USERPATH, 'fond_perso' + ext)
            if destination != chemin_image:
                shutil.copy2(chemin_image, destination)
        else:
            destination = u""

        return {'ENREGISTREMENT':self.ctl_chemin_enregistrement.GetValue(),
                'ENREGISTREMENT_AUTO':self.cbx_enregistrement_auto.GetValue(),
                'PLEIN_ECRAN':self.cbx_plein_ecran.GetValue(),
                'BAVARDE':self.cbx_bavarde.GetValue(),
                'NOUVEAU_AFFICHE_PREFERENCES':self.cbx_nouveau_affiche_preferences.GetValue(),
                'IMAGE':destination}

    def defaut(self):
        """
        Réinialiser les valeurs par défaut.
        """
        self.ctl_chemin_enregistrement.SetValue(os.path.expanduser(cfg.DEFAUT[self.section]['ENREGISTREMENT']))
        self.cbx_enregistrement_auto.SetValue(cfg.DEFAUT[self.section]['ENREGISTREMENT_AUTO'])
        self.cbx_plein_ecran.SetValue(cfg.DEFAUT[self.section]['PLEIN_ECRAN'])
        self.cbx_bavarde.SetValue(cfg.DEFAUT[self.section]['BAVARDE'])
        self.cbx_nouveau_affiche_preferences.SetValue(cfg.DEFAUT[self.section]['NOUVEAU_AFFICHE_PREFERENCES'])
        self.ctl_chemin_fond.SetValue(cfg.DEFAUT[self.section]['IMAGE'])

class TournoiPage(wx.Panel):
    def __init__(self, parent, section, config):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.section = section

        # Boite encadrée
        box1 = wx.StaticBox(self, wx.ID_ANY, u"Joueurs")
        box2 = wx.StaticBox(self, wx.ID_ANY, u"Equipes")
        box3 = wx.StaticBox(self, wx.ID_ANY, u"Manches")

        # Chemin historique joueurs
        txt_historique_joueurs = wx.StaticText(self, wx.ID_ANY, u"Fichier historique des joueurs : ")
        self.ctl_historique_joueurs = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.ctl_historique_joueurs.SetValue(os.path.expanduser(config.get(self.section, 'HISTORIQUE')))
        btn_parcourir = wx.Button(self, wx.ID_ANY, u"Parcourir...")

        # Completion des noms de joueurs
        self.cbx_joueur_completion = wx.CheckBox(self, wx.ID_ANY, u"Auto complétion des prénoms et noms des joueurs")
        self.cbx_joueur_completion.SetValue(config.get_typed(self.section, 'JOUEUR_COMPLETION'))

        # Joueurs par équipes
        txt_joueurs_par_equipe = wx.StaticText(self, wx.ID_ANY, u"Nombre de joueurs par équipe : ")
        self.spn_joueurs_par_equipe = flsp.FloatSpin(self, wx.ID_ANY, min_val=1, increment=1, agwStyle=flsp.FS_CENTRE)
        self.spn_joueurs_par_equipe.SetFormat("%f")
        self.spn_joueurs_par_equipe.SetDigits(0)
        self.spn_joueurs_par_equipe.SetValue(config.get_typed(self.section, 'JOUEURS_PAR_EQUIPE'))

        # Type de classement
        txt_classement = wx.StaticText(self, wx.ID_ANY, u"Le classement se fait par ordre de priorité en fonction : ")
        self.cbx_classement_victoires = wx.CheckBox(self, wx.ID_ANY, u"1. des victoires")
        self.cbx_classement_victoires.SetValue(config.get_typed(self.section, 'CLASSEMENT_VICTOIRES'))
        txt_classement_points = wx.StaticText(self, wx.ID_ANY, u"2. des points")
        self.cbx_classement_duree = wx.CheckBox(self, wx.ID_ANY, u"3. de la durée moyenne d'une partie")
        self.cbx_classement_duree.SetValue(config.get_typed(self.section, 'CLASSEMENT_DUREE'))

        # Points par manche
        txt_points_par_manche = wx.StaticText(self, wx.ID_ANY, u"Nombre de points par manche : ")
        self.spn_points_par_manche = flsp.FloatSpin(self, wx.ID_ANY, min_val=1, increment=1, agwStyle=flsp.FS_CENTRE)
        self.spn_points_par_manche.SetFormat("%f")
        self.spn_points_par_manche.SetDigits(0)
        self.spn_points_par_manche.SetValue(config.get_typed(self.section, 'POINTS_PAR_MANCHE'))

        # Equipes par manche
        txt_equipes_par_manche = wx.StaticText(self, wx.ID_ANY, u"Nombre de d'équipes par manche : ")
        self.spn_equipes_par_manche = flsp.FloatSpin(self, wx.ID_ANY, min_val=2, increment=1, agwStyle=flsp.FS_CENTRE)
        self.spn_equipes_par_manche.SetFormat("%f")
        self.spn_equipes_par_manche.SetDigits(0)
        self.spn_equipes_par_manche.SetValue(config.get_typed(self.section, 'EQUIPES_PAR_MANCHE'))

        #position des objets
        sizer = wx.BoxSizer(wx.VERTICAL)

        boit1 = wx.BoxSizer(wx.HORIZONTAL)
        boit1.Add(txt_historique_joueurs, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        boit1.Add(self.ctl_historique_joueurs, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        boit1.Add(btn_parcourir, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)

        boit2 = wx.StaticBoxSizer(box1, wx.VERTICAL)
        boit2.AddSizer(boit1, 0, wx.EXPAND, 5)
        boit2.Add(self.cbx_joueur_completion, 0, wx.EXPAND | wx.TOP, 10)
        sizer.Add(boit2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        boit3 = wx.BoxSizer(wx.HORIZONTAL)
        boit3.Add(txt_joueurs_par_equipe, 1, wx.ALIGN_CENTER_VERTICAL)
        boit3.Add(self.spn_joueurs_par_equipe, 1)

        boit4 = wx.BoxSizer(wx.HORIZONTAL)
        boit4.AddSpacer((20, 10))
        boit4.Add(self.cbx_classement_victoires, 0, wx.TOP | wx.LEFT, 10)
        boit4.AddSpacer((20, 10))
        boit4.Add(txt_classement_points, 0, wx.TOP | wx.LEFT, 10)
        boit4.AddSpacer((20, 10))
        boit4.Add(self.cbx_classement_duree, 0, wx.TOP | wx.LEFT, 10)

        boit5 = wx.StaticBoxSizer(box2, wx.VERTICAL)
        boit5.AddSizer(boit3, 0, wx.EXPAND)
        boit5.Add(txt_classement, 0, wx.EXPAND | wx.TOP, 5)
        boit5.AddSizer(boit4, 0, wx.EXPAND)
        sizer.Add(boit5, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        boit6 = wx.BoxSizer(wx.HORIZONTAL)
        boit6.Add(txt_points_par_manche, 1, wx.ALIGN_CENTER_VERTICAL)
        boit6.Add(self.spn_points_par_manche, 1)

        boit7 = wx.BoxSizer(wx.HORIZONTAL)
        boit7.Add(txt_equipes_par_manche, 1, wx.ALIGN_CENTER_VERTICAL)
        boit7.Add(self.spn_equipes_par_manche, 1)

        boit8 = wx.StaticBoxSizer(box3, wx.VERTICAL)
        boit8.AddSizer(boit6, 0, wx.EXPAND)
        boit8.AddSizer(boit7, 0, wx.EXPAND)
        sizer.Add(boit8, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.SetSizer(sizer)
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.parcourir, btn_parcourir)

    def parcourir(self, event):
        """
        Bouton Parcourir...
        """
        dlg = wx.FileDialog(self, u"Choisir le fichier :", self.ctl_historique_joueurs.GetValue(), style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            self.ctl_historique_joueurs.SetValue(dlg.GetPath())
        dlg.Destroy()

    def donnees(self):
        """
        Récupérer les valeurs choisies par l'utilisateur.
        """
        return {'HISTORIQUE':self.ctl_historique_joueurs.GetValue(),
                'POINTS_PAR_MANCHE':int(self.spn_points_par_manche.GetValue()),
                'JOUEURS_PAR_EQUIPE':int(self.spn_joueurs_par_equipe.GetValue()),
                'EQUIPES_PAR_MANCHE':int(self.spn_equipes_par_manche.GetValue()),
                'CLASSEMENT_VICTOIRES':self.cbx_classement_victoires.GetValue(),
                'CLASSEMENT_DUREE':self.cbx_classement_duree.GetValue(),
                'JOUEUR_COMPLETION':self.cbx_joueur_completion.GetValue()}

    def defaut(self):
        """
        Réinialiser les valeurs par défaut.
        """
        self.ctl_historique_joueurs.SetValue(os.path.expanduser(cfg.DEFAUT[self.section]['HISTORIQUE']))
        self.spn_points_par_manche.SetValue(cfg.DEFAUT[self.section]['POINTS_PAR_MANCHE'])
        self.spn_joueurs_par_equipe.SetValue(cfg.DEFAUT[self.section]['JOUEURS_PAR_EQUIPE'])
        self.spn_equipes_par_manche.SetValue(cfg.DEFAUT[self.section]['EQUIPES_PAR_MANCHE'])
        self.cbx_classement_victoires.SetValue(cfg.DEFAUT[self.section]['CLASSEMENT_VICTOIRES'])
        self.cbx_classement_duree.SetValue(cfg.DEFAUT[self.section]['CLASSEMENT_DUREE'])
        self.cbx_joueur_completion.SetValue(cfg.DEFAUT[self.section]['JOUEUR_COMPLETION'])

class TiragePage(wx.Panel):
    def __init__(self, parent, section, config):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.section = section
        self.pages = []

        self.choicebook = wx.Choicebook(self, wx.ID_ANY)

        for type_tirage, module in tirages.TIRAGES.items():
            page = TirageSousPageParametre(self.choicebook, config, type_tirage)
            self.pages.append(page)
            self.choicebook.AddPage(page, tirages.TIRAGES[type_tirage].NOM)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.choicebook, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)
        self.Layout()

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

class TirageSousPageParametre(wx.Panel):
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

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grille, 0, wx.EXPAND | wx.LEFT, 15)

        self.SetSizer(sizer)
        self.Layout()

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
            valeur = tirages.TIRAGES[self.section].DEFAUT[self.grille.GetCellValue(i, 0).upper()]
            if type(valeur) == bool:
                if valeur == True:
                    valeur = 1
                else:
                    valeur = ''
            self.grille.SetCellValue(i, 1, unicode(valeur))
            i += 1

class AffichagePage(wx.Panel):
    def __init__(self, parent, section, config):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.section = section

        self.notebook = wx.Notebook(self, wx.ID_ANY, style=wx.LB_TOP)
        self._dlg_test = DialogueInformations(self, config)

        # Création des pages
        page0 = AffichageSousPageMessage(self.notebook, self.section, config, self.test)
        self.notebook.AddPage(page0, u"   Message     ")
        page1 = AffichageSousPageInterlude(self.notebook, self.section, config, self.test)
        self.notebook.AddPage(page1, u"   Interlude     ")
        page2 = AffichageSousPageGrille(self.notebook, self.section, config, self.test)
        self.notebook.AddPage(page2, u"Tirages / Résultats")

        self.cbx_dimension_auto = wx.CheckBox(self, wx.ID_ANY, u"Dimensionner la taille des polices automatiquement")
        self.cbx_dimension_auto.SetValue(config.get_typed(self.section, 'DIMENSION_AUTO'))

        self.btn_test = wx.Button(self, -1, "Test")

        #position des objets
        sizer = wx.BoxSizer(wx.VERTICAL)

        boit1 = wx.BoxSizer(wx.HORIZONTAL)
        boit1.Add(self.cbx_dimension_auto, 0, wx.EXPAND)
        boit1.AddSpacer((10, 10), 1)
        boit1.Add(self.btn_test, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self.notebook, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        sizer.AddSpacer((10, 20), 0, wx.EXPAND)
        sizer.AddSizer(boit1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self.SetSizer(sizer)
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.test, self.btn_test)

    def test(self, event):
        self._dlg_test.configurer(self.donnees())
        if event.GetId() == self.btn_test.GetId():
            self.btn_test.SetLabel(">>>")
            if self._dlg_test.IsShown():
                self._dlg_test.test(True)
            else:
                self._dlg_test.Show()
                self._dlg_test.test()
        else:
            self._dlg_test.test()

    def donnees(self):
        """
        Récupérer les valeurs choisies par l'utilisateur.
        """
        d = {'DIMENSION_AUTO':self.cbx_dimension_auto.GetValue() }

        for page in range(self.notebook.GetPageCount()):
            d.update(self.notebook.GetPage(page).donnees())

        return d

    def defaut(self):
        """
        Réinialiser les valeurs par défaut.
        """
        self.cbx_dimension_auto.SetValue(cfg.DEFAUT[self.section]['DIMENSION_AUTO'])
        page = self.notebook.GetCurrentPage()
        page.defaut()

class AffichageSousPageMessage(wx.Panel):
    def __init__(self, parent, section, config, maj):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.section = section
        self._maj = maj

        # Message
        self.cbx_message_visible = wx.CheckBox(self, wx.ID_ANY, u"Afficher un message personnalisé:")
        self.cbx_message_visible.SetValue(config.get_typed(self.section, 'MESSAGE_VISIBLE'))

        self.ctl_message = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.ctl_message.SetValue(config.get(self.section, 'MESSAGE', raw=True))

        police1 = string_en_wxFont(config.get(self.section, 'MESSAGE_POLICE'))
        couleur1 = wx.Colour(*config.get_typed(self.section, 'MESSAGE_COULEUR'))

        self.btn_message_police = PoliceBouton(self, police1, couleur1)
        self.btn_message_police.SetMinSize((250, -1))
        self.btn_message_couleur = wx.ColourPickerCtrl(self)
        self.btn_message_couleur.SetColour(couleur1)

        self.sld_message_vitesse = wx.Slider(self, value=config.get_typed(self.section, 'MESSAGE_VITESSE'), minValue=1, maxValue=100,
                        style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.sld_message_vitesse.SetTickFreq(5)

        self.btn_variables = wx.Button(self, -1, "Variables...")

        #position des objets
        sizer = wx.BoxSizer(wx.VERTICAL)

        boit1 = wx.BoxSizer(wx.HORIZONTAL)
        boit1.Add(wx.StaticText(self, -1, u"Police de caractères:", size=(230, -1)), 0, wx.ALIGN_CENTER_VERTICAL)
        boit1.Add(self.btn_message_police, 0, wx.ALIGN_CENTER_VERTICAL)
        boit1.Add(self.btn_message_couleur, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 20)

        boit2 = wx.BoxSizer(wx.HORIZONTAL)
        boit2.Add(wx.StaticText(self, -1, u"Vitesse de défilement (en fps):", size=(230, -1)), 0, wx.ALIGN_CENTER_VERTICAL)
        boit2.Add(self.sld_message_vitesse, 1, wx.ALIGN_CENTER_VERTICAL)

        boit3 = wx.BoxSizer(wx.HORIZONTAL)
        boit3.Add(self.ctl_message, 1, wx.RIGHT, 10)
        boit3.Add(self.btn_variables, 0)

        sizer.Add(self.cbx_message_visible, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        sizer.AddSpacer((20, 20), 0, wx.EXPAND)
        sizer.Add(boit3, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        sizer.AddSpacer((20, 20), 0, wx.EXPAND)
        sizer.AddSizer(boit1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        sizer.AddSpacer((20, 20), 0, wx.EXPAND)
        sizer.AddSizer(boit2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetSizer(sizer)
        self.Layout()

        self.Bind(wx.EVT_CHECKBOX, self._maj, self.cbx_message_visible)
        self.Bind(wx.EVT_TEXT, self._maj, self.ctl_message)
        self.Bind(wx.EVT_BUTTON, self.maj_couleur, self.btn_message_police)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.maj_couleur, self.btn_message_couleur)
        self.Bind(wx.EVT_SCROLL, self._maj, self.sld_message_vitesse)
        self.Bind(wx.EVT_BUTTON, partial(selectioner_variable, ctl_texte=self.ctl_message), self.btn_variables)

    def maj_couleur(self, event):
        if event.GetId() == self.btn_message_couleur.GetId():
            self.btn_message_police.couleur = self.btn_message_couleur.GetColour()
        else:
            self.btn_message_couleur.SetColour(self.btn_message_police.couleur)
        self._maj(event)

    def donnees(self):
        """
        Récupérer les valeurs choisies par l'utilisateur.
        """
        return {'MESSAGE_VISIBLE':self.cbx_message_visible.GetValue(),
                'MESSAGE':self.ctl_message.GetValue(),
                'MESSAGE_POLICE':wxFont_en_string(self.btn_message_police.police),
                'MESSAGE_COULEUR':self.btn_message_couleur.GetColour(),
                'MESSAGE_VITESSE':self.sld_message_vitesse.GetValue()}

    def defaut(self):
        """
        Réinialiser les valeurs par défaut.
        """
        self.cbx_message_visible.SetValue(cfg.DEFAUT[self.section]['MESSAGE_VISIBLE'])
        self.ctl_message.SetValue(cfg.DEFAUT[self.section]['MESSAGE'])
        self.btn_message_police.chg_police_desc(cfg.DEFAUT[self.section]['MESSAGE_POLICE'])
        self.btn_message_couleur.SetColour(wx.Colour(*cfg.DEFAUT[self.section]['MESSAGE_COULEUR']))
        self.sld_message_vitesse.SetValue(cfg.DEFAUT[self.section]['MESSAGE_VITESSE'])

class AffichageSousPageInterlude(wx.Panel):
    def __init__(self, parent, section, config, maj):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.section = section
        self._maj = maj

        self.ctl_texte_inscription = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.ctl_texte_inscription.SetValue(config.get(self.section, 'TEXTE_INSCRIPTION', raw=True))

        self.ctl_texte_tirage = wx.TextCtrl(self, wx.ID_ANY, u"")
        self.ctl_texte_tirage.SetValue(config.get(self.section, 'TEXTE_TIRAGE', raw=True))

        police2 = string_en_wxFont(config.get(self.section, 'TEXTE_POLICE'))
        couleur2 = wx.Colour(*config.get_typed(self.section, 'TEXTE_COULEUR'))

        self.btn_texte_police = PoliceBouton(self, police2, couleur2)
        self.btn_texte_police.SetMinSize((250, -1))
        self.btn_texte_couleur = wx.ColourPickerCtrl(self)
        self.btn_texte_couleur.SetColour(couleur2)

        self.btn_variables_inscription = wx.Button(self, -1, "Variables...")
        self.btn_variables_tirage = wx.Button(self, -1, "Variables...")

        #position des objets
        sizer = wx.BoxSizer(wx.VERTICAL)

        boit1 = wx.BoxSizer(wx.HORIZONTAL)
        boit1.Add(wx.StaticText(self, -1, u"Interlude inscription:", size=(150, -1)), 0, wx.ALIGN_CENTER_VERTICAL)
        boit1.Add(self.ctl_texte_inscription, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        boit1.Add(self.btn_variables_inscription)

        boit2 = wx.BoxSizer(wx.HORIZONTAL)
        boit2.Add(wx.StaticText(self, -1, u"Interlude tirage:", size=(150, -1)), 0, wx.ALIGN_CENTER_VERTICAL)
        boit2.Add(self.ctl_texte_tirage, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        boit2.Add(self.btn_variables_tirage)

        boit3 = wx.BoxSizer(wx.HORIZONTAL)
        boit3.Add(wx.StaticText(self, -1, u"Police de caractères:", size=(150, -1)), 0, wx.ALIGN_CENTER_VERTICAL)
        boit3.Add(self.btn_texte_police, 1, wx.ALIGN_CENTER_VERTICAL)
        boit3.Add(self.btn_texte_couleur, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 20)

        sizer.AddSizer(boit1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        sizer.AddSpacer((20, 20), 0, wx.EXPAND)
        sizer.AddSizer(boit2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        sizer.AddSpacer((20, 20), 0, wx.EXPAND)
        sizer.AddSizer(boit3, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetSizer(sizer)
        self.Layout()

        self.Bind(wx.EVT_TEXT, self._maj, self.ctl_texte_inscription)
        self.Bind(wx.EVT_TEXT, self._maj, self.ctl_texte_tirage)
        self.Bind(wx.EVT_BUTTON, self.maj_couleur, self.btn_texte_police)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.maj_couleur, self.btn_texte_couleur)
        self.Bind(wx.EVT_BUTTON, partial(selectioner_variable, ctl_texte=self.ctl_texte_inscription), self.btn_variables_inscription)
        self.Bind(wx.EVT_BUTTON, partial(selectioner_variable, ctl_texte=self.ctl_texte_tirage), self.btn_variables_tirage)

    def maj_couleur(self, event):
        if event.GetId() == self.btn_texte_couleur.GetId():
            self.btn_texte_police.couleur = self.btn_texte_couleur.GetColour()
        else:
            self.btn_texte_couleur.SetColour(self.btn_texte_police.couleur)
        self._maj(event)

    def donnees(self):
        """
        Récupérer les valeurs choisies par l'utilisateur.
        """
        return {'TEXTE_INSCRIPTION':self.ctl_texte_inscription.GetValue(),
                'TEXTE_TIRAGE':self.ctl_texte_tirage.GetValue(),
                'TEXTE_POLICE':wxFont_en_string(self.btn_texte_police.police),
                'TEXTE_COULEUR':self.btn_texte_couleur.GetColour()}

    def defaut(self):
        """
        Réinialiser les valeurs par défaut.
        """
        self.ctl_texte_inscription.SetValue(cfg.DEFAUT[self.section]['TEXTE_INSCRIPTION'])
        self.ctl_texte_tirage.SetValue(cfg.DEFAUT[self.section]['TEXTE_TIRAGE'])
        self.btn_texte_police.chg_police_desc(cfg.DEFAUT[self.section]['TEXTE_POLICE'])
        self.btn_texte_couleur.SetColour(wx.Colour(*cfg.DEFAUT[self.section]['TEXTE_COULEUR']))

class AffichageSousPageGrille(wx.Panel):
    def __init__(self, parent, section, config, maj):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.section = section
        self._maj = maj

        # Titre
        police3 = string_en_wxFont(config.get(self.section, 'TITRE_POLICE'))
        couleur3 = wx.Colour(*config.get_typed(self.section, 'TITRE_COULEUR'))

        self.btn_titre_police = PoliceBouton(self, police3, couleur3)
        self.btn_titre_police.SetMinSize((250, -1))
        self.btn_titre_couleur = wx.ColourPickerCtrl(self)
        self.btn_titre_couleur.SetColour(couleur3)

        # Grille
        police4 = string_en_wxFont(config.get(self.section, 'GRILLE_POLICE'))

        self.btn_grille_police = PoliceBouton(self, police4, wx.Colour(0, 0, 0))
        self.btn_grille_police.SetMinSize((250, -1))

        self.spn_grille_lignes = flsp.FloatSpin(self, wx.ID_ANY, min_val=1, increment=1, agwStyle=flsp.FS_CENTRE)
        self.spn_grille_lignes.SetFormat("%f")
        self.spn_grille_lignes.SetDigits(0)
        self.spn_grille_lignes.SetValue(config.get_typed(self.section, 'GRILLE_LIGNES'))

        self.sld_grille_duree_affichage = TimeSlider(self, value=config.get_typed(self.section, 'GRILLE_DUREE_AFFICHAGE'), minValue=5000, maxValue=600000,
                        increment=1000, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        self.sld_grille_duree_affichage.SetTickFreq(30000)

        self.sld_grille_temps_defilement = TimeSlider(self, value=config.get_typed(self.section, 'GRILLE_TEMPS_DEFILEMENT'), minValue=0, maxValue=5000,
                        increment=100, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        self.sld_grille_temps_defilement.SetTickFreq(500)

        # Sens de défilement
        self.btn_sens_horizontal = buttons.GenBitmapToggleButton(self, -1, None, size=(40, 40))
        self.btn_sens_horizontal.SetBitmapLabel(images.bitmap('defilement_h.png'))
        self.btn_sens_horizontal.SetToggle(not config.get_typed(self.section, 'GRILLE_DEFILEMENT_VERTICAL'))
        self.btn_sens_vertical = buttons.GenBitmapToggleButton(self, -1, None, size=(40, 40))
        self.btn_sens_vertical.SetBitmapLabel(images.bitmap('defilement_v.png'))
        self.btn_sens_vertical.SetToggle(config.get_typed(self.section, 'GRILLE_DEFILEMENT_VERTICAL'))

        #position des objets
        sizer = wx.BoxSizer(wx.VERTICAL)

        boit1 = wx.BoxSizer(wx.HORIZONTAL)
        boit1.Add(wx.StaticText(self, -1, u"Police de caractères du titre:", size=(230, -1)), 0, wx.ALIGN_CENTER_VERTICAL)
        boit1.Add(self.btn_titre_police, 0, wx.ALIGN_CENTER_VERTICAL)
        boit1.Add(self.btn_titre_couleur, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 20)

        boit2 = wx.BoxSizer(wx.HORIZONTAL)
        boit2.Add(wx.StaticText(self, -1, u"Nombre de lignes affichées:", size=(230, -1)), 0, wx.ALIGN_CENTER_VERTICAL)
        boit2.Add(self.spn_grille_lignes, 1, wx.ALIGN_CENTER_VERTICAL)

        boit3 = wx.BoxSizer(wx.HORIZONTAL)
        boit3.Add(wx.StaticText(self, -1, u"Police de caractères de la grille:", size=(230, -1)), 0, wx.ALIGN_CENTER_VERTICAL)
        boit3.Add(self.btn_grille_police, 0, wx.ALIGN_CENTER_VERTICAL)

        boit4 = wx.BoxSizer(wx.HORIZONTAL)
        boit4.Add(wx.StaticText(self, -1, u"Temps avant changement:", size=(230, -1)), 0, wx.ALIGN_CENTER_VERTICAL)
        boit4.Add(self.sld_grille_duree_affichage, 1, wx.ALIGN_CENTER_VERTICAL)

        boit5 = wx.BoxSizer(wx.HORIZONTAL)
        boit5.Add(wx.StaticText(self, -1, u"Vitesse de défilement:", size=(230, -1)), 0, wx.ALIGN_CENTER_VERTICAL)
        boit5.Add(self.sld_grille_temps_defilement, 1, wx.ALIGN_CENTER_VERTICAL)

        boit6 = wx.BoxSizer(wx.HORIZONTAL)
        boit6.Add(wx.StaticText(self, -1, u"Sens de défilement des tirages:\n(Cas ou il y a deux grilles)", size=(230, -1)), 0, wx.ALIGN_CENTER_VERTICAL)
        boit6.Add(self.btn_sens_horizontal, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 40)
        boit6.Add(self.btn_sens_vertical, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 40)

        sizer.AddSizer(boit1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        sizer.AddSpacer((20, 20), 0, wx.EXPAND)
        sizer.AddSizer(boit2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        sizer.AddSpacer((20, 20), 0, wx.EXPAND)
        sizer.AddSizer(boit3, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        sizer.AddSpacer((20, 20), 0, wx.EXPAND)
        sizer.AddSizer(boit4, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        sizer.AddSpacer((20, 20), 0, wx.EXPAND)
        sizer.AddSizer(boit5, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        sizer.AddSpacer((20, 10), 0, wx.EXPAND)
        sizer.AddSizer(boit6, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetSizer(sizer)
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.maj_couleur, self.btn_titre_police)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.maj_couleur, self.btn_titre_couleur)
        self.Bind(flsp.EVT_FLOATSPIN, self._maj, self.spn_grille_lignes)
        self.Bind(wx.EVT_BUTTON, self._maj, self.btn_grille_police)
        self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self._maj, self.sld_grille_duree_affichage.slider)
        self.Bind(wx.EVT_SCROLL_THUMBRELEASE, self._maj, self.sld_grille_temps_defilement.slider)
        self.Bind(wx.EVT_BUTTON, partial(self.selection_sens_defilement, btn=self.btn_sens_horizontal), self.btn_sens_horizontal)
        self.Bind(wx.EVT_BUTTON, partial(self.selection_sens_defilement, btn=self.btn_sens_vertical), self.btn_sens_vertical)

    def maj_couleur(self, event):
        if event.GetId() == self.btn_titre_couleur.GetId():
            self.btn_titre_police.couleur = self.btn_titre_couleur.GetColour()
        else:
            self.btn_titre_couleur.SetColour(self.btn_titre_police.couleur)
        self._maj(event)

    def selection_sens_defilement(self, event, btn):
        if btn == self.btn_sens_horizontal:
            nobtn = self.btn_sens_vertical
        else:
            nobtn = self.btn_sens_horizontal
        nobtn.SetToggle(not btn.GetToggle())

    def donnees(self):
        """
        Récupérer les valeurs choisies par l'utilisateur.
        """
        return {'TITRE_POLICE':wxFont_en_string(self.btn_titre_police.police),
                'TITRE_COULEUR':self.btn_titre_couleur.GetColour(),
                'GRILLE_LIGNES': int(self.spn_grille_lignes.GetValue()),
                'GRILLE_POLICE': wxFont_en_string(self.btn_grille_police.police),
                'GRILLE_DUREE_AFFICHAGE': self.sld_grille_duree_affichage.GetValue(),
                'GRILLE_TEMPS_DEFILEMENT': self.sld_grille_temps_defilement.GetValue(),
                'GRILLE_DEFILEMENT_VERTICAL': self.btn_sens_vertical.GetToggle()}

    def defaut(self):
        """
        Réinialiser les valeurs par défaut.
        """
        self.btn_titre_police.chg_police_desc(cfg.DEFAUT[self.section]['TITRE_POLICE'])
        self.btn_titre_couleur.SetColour(wx.Colour(*cfg.DEFAUT[self.section]['TITRE_COULEUR']))
        self.spn_grille_lignes.SetValue(cfg.DEFAUT[self.section]['GRILLE_LIGNES'])
        self.btn_grille_police.chg_police_desc(cfg.DEFAUT[self.section]['GRILLE_POLICE'])
        self.sld_grille_duree_affichage.SetValue(cfg.DEFAUT[self.section]['GRILLE_DUREE_AFFICHAGE'])
        self.sld_grille_temps_defilement.SetValue(cfg.DEFAUT[self.section]['GRILLE_TEMPS_DEFILEMENT'])
        self.btn_sens_vertical.SetToggle(cfg.DEFAUT[self.section]['GRILLE_DEFILEMENT_VERTICAL'])
        self.btn_sens_horizontal.SetToggle(not cfg.DEFAUT[self.section]['GRILLE_DEFILEMENT_VERTICAL'])

class DialoguePreferences(wx.Dialog):
    def __init__(self, parent, config, page=0):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, u"Préférences TourBillon")
        self.SetBackgroundColour(wx.Colour(226, 226, 226))
        self.SetMinSize((600, 500))
        self.CenterOnParent(wx.BOTH)
        self.config = config

        self.notebook = wx.Listbook(self, wx.ID_ANY, style=wx.LB_TOP)

        # Liste des images
        il = wx.ImageList(32, 32)
        il.Add(images.bitmap('opt_general.png'))
        il.Add(images.bitmap('opt_tournoi.png'))
        il.Add(images.bitmap('opt_tirage.png'))
        il.Add(images.bitmap('opt_affichage.png'))
        self.notebook.AssignImageList(il)

        # Création des pages
        self.page0 = GeneralPage(self.notebook, "INTERFACE", self.config)
        self.notebook.AddPage(self.page0, u"   Général   ", imageId=0)
        self.page1 = TournoiPage(self.notebook, "TOURNOI", self.config)
        self.notebook.AddPage(self.page1, u"   Tournoi   ", imageId=1)
        self.page2 = TiragePage(self.notebook, "", self.config)
        self.notebook.AddPage(self.page2, u"   Tirages   ", imageId=2)
        self.page3 = AffichagePage(self.notebook, "AFFICHAGE", self.config)
        self.notebook.AddPage(self.page3, u"Affichage", imageId=3)

        # Bouttons
        self.btn_defaut = wx.Button(self, wx.ID_DEFAULT, u"Défaut", size=(100, 25))
        self.btn_enregistrer = wx.Button(self, wx.ID_OK, u"Enregistrer", size=(100, 25))
        self.btn_enregistrer.SetDefault()
        self.btn_annuler = wx.Button(self, wx.ID_CANCEL, u"Annuler", size=(100, 25))

        # Position des objets
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.notebook, 0, wx.EXPAND)

        boit1 = wx.BoxSizer(wx.HORIZONTAL)
        boit1.Add(self.btn_defaut, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        boit1.Add((10, 10), 1, wx.EXPAND)
        boit1.Add(self.btn_annuler, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        boit1.Add(self.btn_enregistrer, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        sizer.Add(boit1, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)
        self.Layout()
        self.notebook.SetSelection(page)
        self.Fit()

        self.Bind(wx.EVT_BUTTON, self.defaut, self.btn_defaut)

    def donnees(self):
        d = {self.page0.section:self.page0.donnees(),
             self.page1.section:self.page1.donnees(),
             self.page3.section:self.page3.donnees()}

        d.update(self.page2.donnees())

        return d

    def defaut(self, event):
        page = self.notebook.GetCurrentPage()
        page.defaut()
