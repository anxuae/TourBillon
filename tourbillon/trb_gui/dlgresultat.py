#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import sys, os
import wx
from  wx.lib import scrolledpanel as scrolled

from tourbillon.trb_gui import dlgequipe as dlgeq

from tourbillon.trb_core import tournois
from tourbillon.trb_core.tirages import utile
from tourbillon.trb_core import constantes as cst

#--- Entrée score --------------------------------------------------------------

class EntrerScore(wx.Panel):
    def __init__(self, parent, choix=[]):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        if choix == []:
            self.ctl_numero = wx.StaticText(self, wx.ID_ANY, u"")
            self.ctl_numero.SetBackgroundColour(wx.Color(220, 220, 220))
            self.combo = False
        else:
            self.ctl_numero = wx.Choice(self, dlgeq.ID_NUMERO, choices=map(unicode, choix))
            self.combo = True

        self.ctl_numero.SetMinSize(wx.Size(70, 22))

        self.ctl_points = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_CENTRE, validator=dlgeq.EquipeValidateur())
        self.ctl_points.SetMinSize(wx.Size(70, 22))

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.ctl_numero, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
        box.Add(self.ctl_points, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        self.SetSizer(box)
        self.Layout()

    def chg_numero(self, numero):
        numero = unicode(int(numero))
        if self.combo == True:
            self.ctl_numero.SetSelection(self.ctl_numero.FindString(numero))
        else:
            self.ctl_numero.SetLabel(u"  " + numero)
            self.Layout()

    def numero(self):
        if self.combo == True:
            return int(self.ctl_numero.GetString(self.ctl_numero.GetSelection()))
        else:
            return int(self.ctl_numero.GetLabel().strip())

    def chg_points(self, points):
        self.ctl_points.SetValue(unicode(points))

    def points(self):
        valeur = self.ctl_points.GetValue()
        if valeur == u"":
            return None
        else:
            return int(valeur)

class DialogueResultat(wx.Dialog):
    def __init__(self, parent, numero_partie, numero_affiche=1):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title=u"Resultats" , style=wx.DEFAULT_DIALOG_STYLE | wx.CENTER_ON_SCREEN | wx.RESIZE_BORDER)
        self.SetMinSize(wx.Size(280, 170))
        self.SetMaxSize(wx.Size(280, -1))
        self.SetTitle(u"Resultats de la partie n°%s" % numero_partie)
        self.CenterOnParent()

        self.entrees = []
        self.numero_partie = numero_partie
        self.tirage = tournois.tournoi().partie(self.numero_partie).tirage()

        # Panel avec les entrées des équipes
        self.panel = scrolled.ScrolledPanel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        box_panel = wx.BoxSizer(wx.VERTICAL)
        for i in range(tournois.tournoi().equipes_par_manche):
            if i == 0:
                liste = utile.creer_liste(self.tirage)
                for chap in tournois.tournoi().partie(self.numero_partie).chapeaux():
                    liste.remove(chap)
                e = EntrerScore(self.panel, sorted(liste))
                e.chg_numero(numero_affiche)
            else:
                e = EntrerScore(self.panel)
            self.entrees.append(e)
            box_panel.Add(e, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, 15)
        self.panel.SetSizer(box_panel)
        self.panel.SetupScrolling()

        # Check box enregistrement durée de fin
        self.chx_fin = wx.CheckBox(self, wx.ID_ANY, u"Enregistrer l'heure de fin.")

        # Boutons
        self.btn_ok = wx.Button(self, id=wx.ID_OK, label=u"Valider", size=(100, -1))
        self.btn_ok.SetDefault()
        self.btn_annule = wx.Button(self, id=wx.ID_CANCEL, label="Annuler", size=(100, -1))
        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        box_btn.AddSpacer((50, 50), 1, wx.EXPAND)
        box_btn.Add(self.btn_annule, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        box_btn.Add(self.btn_ok, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        box_btn.AddSpacer((50, 50), 1, wx.EXPAND)

        # Assembler
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.panel, 1, wx.EXPAND)
        box.Add(self.chx_fin, 0, wx.EXPAND | wx.LEFT, 14)
        box.AddSizer(box_btn, 0, wx.EXPAND)

        self.SetSizer(box)
        self.Layout()
        self._selection_equipe(None)
        self.verifier(None)

        hauteur_necessaire = (self.entrees[0].GetSize()[1] + 15) * len(self.entrees) + 100
        if hauteur_necessaire < wx.GetDisplaySize()[1]:
            self.SetSize(wx.Size(280, hauteur_necessaire))
        else:
            self.SetSize(wx.Size(280, wx.GetDisplaySize()[1] - 10))

        self.Bind(wx.EVT_TEXT, self.verifier)
        self.Bind(wx.EVT_CHOICE, self._selection_equipe, id=dlgeq.ID_NUMERO)

    def _selection_equipe(self, event):
        num = self.entrees[0].numero()
        for manche in self.tirage:
            if num in manche:
                break
        i = 1
        for equipe in manche:
            points = tournois.tournoi().equipe(equipe).resultat(self.numero_partie)['points']
            if equipe == num:
                self.entrees[0].chg_points(points)
            else:
                self.entrees[i].chg_numero(equipe)
                self.entrees[i].chg_points(points)
                i += 1

        if tournois.tournoi().equipe(self.entrees[0].numero()).resultat(self.numero_partie)['duree'] is None:
            self.chx_fin.SetValue(True)
            self.chx_fin.Disable()
        else:
            self.chx_fin.SetValue(False)

    def donnees(self):
        d = {}
        for entree in self.entrees:
            d[entree.numero()] = entree.points()

        return d

    def fin(self):
        return self.chx_fin.IsChecked()

    def verifier(self, event):
        valeurs = []
        for entree in self.entrees:
            if entree.points() is None:
                self.btn_ok.Disable()
                break
            valeurs.append(entree.points())

        if len(valeurs) == len(self.entrees):
            m = max(valeurs)
            if m < tournois.tournoi().points_par_manche:
                self.btn_ok.Disable()
            else:
                self.btn_ok.Enable()

        if event is not None:
            event.Skip()
