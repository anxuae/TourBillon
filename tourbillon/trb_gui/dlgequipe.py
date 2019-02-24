#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import sys, os
import wx
import string
from  wx.lib import scrolledpanel as scrolled

from tourbillon.trb_core import joueur
from tourbillon.trb_core import tournoi
from tourbillon.trb_core import constantes as cst

#--- Varibles globales ---------------------------------------------------------

ID_PRENOM = wx.NewId()
ID_NOM = wx.NewId()
ID_NUMERO = wx.NewId()

STYLE_AJOUTER = u"Ajouter"
STYLE_MOFIFIER = u"Modifier"
STYLE_SUPPRIMER = u"Supprimer"

#--- Classes -------------------------------------------------------------------

class EntrerJoueur(wx.Panel):
    def __init__(self, parent, titres=True):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self._completion = True
        self._cmp = True

        prenom, nom, age = "", "", ""
        if titres:
            prenom, nom, age = "  Prenom:", "  Nom   :", "  Age   :"

        self.txt_prenom = wx.StaticText(self, wx.ID_ANY, prenom, size=(65, -1))
        self.ctl_prenom = wx.TextCtrl(self, ID_PRENOM, u"")
        self.ctl_prenom._selection = u""

        self.txt_nom = wx.StaticText(self, wx.ID_ANY, nom, size=(65, -1))
        self.ctl_nom = wx.TextCtrl(self, ID_NOM, u"")
        self.ctl_nom._selection = u""

        self.txt_age = wx.StaticText(self, wx.ID_ANY, age, size=(50, -1))
        self.ctl_age = wx.TextCtrl(self, wx.ID_ANY, u"", size=(40, -1))
        self.ctl_age._selection = u""

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.txt_prenom, 0, wx.EXPAND)
        box.Add(self.ctl_prenom, 1, wx.EXPAND)
        box.Add(self.txt_nom, 0, wx.EXPAND)
        box.Add(self.ctl_nom, 1, wx.EXPAND)
        box.Add(self.txt_age, 0, wx.EXPAND)
        box.Add(self.ctl_age, 0, wx.EXPAND)
        self.SetSizer(box)

        self.Layout()

        self.ctl_prenom.Bind(wx.EVT_CHAR, self.enter_prenom)
        self.ctl_nom.Bind(wx.EVT_CHAR, self.enter_nom)
        self.ctl_prenom.Bind(wx.EVT_TEXT, self.completer)
        self.ctl_nom.Bind(wx.EVT_TEXT, self.completer)

    def activer_completion(self, valeur=True):
        self._completion = valeur

    def enter_prenom(self, event):
        if self._completion:

            if event.GetKeyCode() == wx.WXK_DELETE or\
               event.GetKeyCode() == wx.WXK_BACK or\
               event.GetKeyCode() == wx.WXK_TAB or\
               event.GetKeyCode() == wx.WXK_RIGHT or\
               event.GetKeyCode() == wx.WXK_RETURN or\
               event.ControlDown() or event.CmdDown():
                self._cmp = False
            else:
                point = self.ctl_prenom.GetInsertionPoint()
                self.effacer_selection(self.ctl_nom)
                self.effacer_selection(self.ctl_age)
                self.effacer_selection(self.ctl_prenom)
                self.ctl_prenom.SetInsertionPoint(point)
                self._cmp = True

        event.Skip()

    def enter_nom(self, event):
        if self._completion:

            if event.GetKeyCode() == wx.WXK_DELETE or\
               event.GetKeyCode() == wx.WXK_BACK or\
               event.GetKeyCode() == wx.WXK_TAB or\
               event.GetKeyCode() == wx.WXK_RIGHT or\
               event.GetKeyCode() == wx.WXK_RETURN or\
               event.ControlDown() or event.CmdDown():
                self._cmp = False
            else:
                point = self.ctl_nom.GetInsertionPoint()
                self.effacer_selection(self.ctl_age)
                self.effacer_selection(self.ctl_nom)
                self.ctl_nom.SetInsertionPoint(point)
                self._cmp = True

        event.Skip()

    def completer(self, event):
        if self._completion:
            if self._cmp:
                c = joueur.NomCompleteur()
                prenom, nom, age, date = c.completer(self.ctl_prenom.GetValue(), self.ctl_nom.GetValue())

                if prenom != u"":
                    self.ajout_texte(self.ctl_prenom, prenom)
                if nom != u"":
                    self.ajout_texte(self.ctl_nom, nom)
                if age != u"":
                    self.ajout_texte(self.ctl_age, age)

        event.Skip()

    def ajout_texte(self, ctl, texte):
        debut = len(ctl.GetValue())
        ctl.ChangeValue(texte)
        ctl._selection = texte[debut:]
        ctl.SetSelection(debut, len(ctl.GetValue()))

    def effacer_selection(self, ctl):
        ctl.ChangeValue(ctl.GetValue().replace(ctl._selection, u""))
        ctl._selection = u""

    def chg_joueur(self, prenom, nom, age=''):
        self.ctl_prenom.SetValue(prenom)
        self.ctl_nom.SetValue(nom)
        self.ctl_age.SetValue(age)
        self.ctl_prenom.SetSelection(len(self.ctl_prenom.GetValue()), len(self.ctl_prenom.GetValue()))
        self.ctl_nom.SetSelection(len(self.ctl_nom.GetValue()), len(self.ctl_nom.GetValue()))
        self.ctl_age.SetSelection(len(self.ctl_age.GetValue()), len(self.ctl_age.GetValue()))

    def chg_editable(self, valeur=True):
        self.ctl_prenom.SetEditable(valeur)
        self.ctl_nom.SetEditable(valeur)
        self.ctl_age.SetEditable(valeur)

    def complet(self):
        if self.ctl_prenom.GetValue() != u"" and self.ctl_nom.GetValue() != u"":
            return True
        else:
            return False

    def donnees(self):
        return (self.ctl_prenom.GetValue(), self.ctl_nom.GetValue(), self.ctl_age.GetValue())

class EquipeValidateur(wx.PyValidator):
    def __init__(self, pyVar=None):
        wx.PyValidator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return EquipeValidateur()

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in string.digits:
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()
        return

class EntrerNumero(wx.Panel):
    def __init__(self, parent, choix=[]):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.SetMinSize((-1, 40))

        self.txt_numero = wx.StaticText(self, wx.ID_ANY, u"Equipe n° ")
        if choix == []:
            self.ctl_numero = wx.TextCtrl(self, wx.ID_ANY, u"", validator=EquipeValidateur())
            self.combo = False
        else:
            self.ctl_numero = wx.Choice(self, ID_NUMERO, choices=map(unicode, choix))
            self.combo = True

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.txt_numero, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
        box.Add(self.ctl_numero, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(box)
        self.Layout()

    def chg_numero(self, numero):
        numero = unicode(numero)
        if self.combo == True:
            self.ctl_numero.SetSelection(self.ctl_numero.FindString(numero))
        else:
            self.ctl_numero.SetValue(numero)

    def complet(self):
        if self.combo == True:
            return True
        else:
            if self.ctl_numero.GetValue() != u"":
                try:
                    tournoi.tournoi().equipe(int(self.ctl_numero.GetValue()))
                    return False
                except:
                    return True
            else:
                return False

    def numero(self):
        if self.combo == True:
            return self.ctl_numero.GetString(self.ctl_numero.GetSelection())
        else:
            return self.ctl_numero.GetValue()

class DialogueEquipe(wx.Dialog):
    def __init__(self, parent, style=STYLE_AJOUTER, choix=[], numero_affiche=1, completion=True):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title=style + u" une équipe" , style=wx.DEFAULT_DIALOG_STYLE | wx.CENTER_ON_SCREEN | wx.RESIZE_BORDER)
        self.SetMinSize((500, 220))
        self.CenterOnParent()

        self.entrees = []
        self.choix = choix

        # Panel avec les entrées des joueurs
        self.panel = scrolled.ScrolledPanel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        box_panel = wx.BoxSizer(wx.VERTICAL)
        for i in range(tournoi.tournoi().joueurs_par_equipe):
            e = EntrerJoueur(self.panel)
            e.activer_completion(completion)
            self.entrees.append(e)
            box_panel.Add(e, 0, wx.EXPAND | wx.ALL, 15)
        self.panel.SetSizer(box_panel)
        self.panel.SetupScrolling()

        if style == STYLE_SUPPRIMER:
            for entree in self.entrees:
                entree.chg_editable(False)

        # Boutons
        self.btn_ok = wx.Button(self, id=wx.ID_OK, label=style, size=(100, -1))
        self.btn_ok.SetDefault()
        self.btn_annule = wx.Button(self, id=wx.ID_CANCEL, label="Annuler", size=(100, -1))
        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        box_btn.AddSpacer((50, 50), 1, wx.EXPAND)
        box_btn.Add(self.btn_annule, 0, wx.EAST | wx.ALIGN_CENTER_VERTICAL, 30)
        box_btn.Add(self.btn_ok, 0, wx.EAST | wx.ALIGN_CENTER_VERTICAL, 15)

        # Numero
        if style == STYLE_AJOUTER:
            self.txt_numero = EntrerNumero(self)
            self.txt_numero.chg_numero(numero_affiche)
        else:
            self.txt_numero = EntrerNumero(self, self.choix)
            self.txt_numero.chg_numero(numero_affiche)
            self._maj(None)

        self._btn_satut(None)

        # Assembler
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.txt_numero, 0, wx.ALIGN_CENTER_HORIZONTAL)
        box.Add(self.panel, 1, wx.EXPAND)
        box.AddSizer(box_btn, 0, wx.EXPAND)

        self.SetSizer(box)
        self.Layout()

        hauteur_necessaire = (self.entrees[0].GetSize()[1] + 30) * len(self.entrees) + 125
        if hauteur_necessaire < wx.GetDisplaySize()[1]:
            self.SetSize(wx.Size(500, hauteur_necessaire))
        else:
            self.SetSize(wx.Size(500, wx.GetDisplaySize()[1] - 10))

        self.Bind(wx.EVT_CHOICE, self._maj, id=ID_NUMERO)
        self.Bind(wx.EVT_TEXT, self._btn_satut)

    def _maj(self, event):
        num = int(self.txt_numero.numero())
        i = 0
        for joueur in tournoi.tournoi().equipe(num).joueurs():
            self.entrees[i].chg_joueur(joueur.prenom, joueur.nom, joueur.age)
            i += 1
        if event:
            event.Skip()

    def _btn_satut(self, event):
        if not self.txt_numero.complet():
            self.btn_ok.Enable(False)
            return
        else:
            for entree in self.entrees:
                if not entree.complet():
                    self.btn_ok.Enable(False)
                    return
        self.btn_ok.Enable(True)

    def donnees(self):
        d = {'numero':int(self.txt_numero.numero()), 'joueurs':[]}
        for entree in self.entrees:
            d['joueurs'].append(entree.donnees())
        return d

class DialogueMessageEquipe(wx.Dialog):
    def __init__(self, parent, equipe):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title=u"Tournoi en cours" , style=wx.DEFAULT_DIALOG_STYLE | wx.CENTER_ON_SCREEN, pos=wx.DefaultPosition, size=wx.DefaultSize)
        self.SetMinSize((500, 220))
        self.SetSize(wx.Size(500, 200))
        self.CenterOnParent()

        texte = u"La partie n° %s est en cours, pour toutes les parties précédentes l'équipe\n\
sera considérée comme forfait, choisissez l'état de l'équipe n° %s pour la\n\
partie en cours:" % (tournoi.tournoi().partie_courante().numero, equipe)
        self.txt_info = wx.StaticText(self, wx.ID_ANY, texte, size=wx.Size(-1, 200))
        self.chx_etat = wx.Choice(self, ID_NUMERO, choices=[cst.FORFAIT, cst.CHAPEAU])
        self.chk_cree_manche = wx.CheckBox(self, wx.ID_ANY, "Créer une manche avec les équipes chapeaux si possible.")

        # Boutons
        self.btn_ok = wx.Button(self, id=wx.ID_OK, label=u"Valider", size=(100, -1))
        self.btn_ok.SetDefault()
        self.btn_annule = wx.Button(self, id=wx.ID_CANCEL, label=u"Annuler", size=(100, -1))

        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        box_btn.AddSpacer((50, 50), 1, wx.EXPAND)
        box_btn.Add(self.btn_annule, 0, wx.EAST | wx.ALIGN_CENTER_VERTICAL, 30)
        box_btn.Add(self.btn_ok, 0, wx.EAST | wx.ALIGN_CENTER_VERTICAL, 15)

        # Assembler
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.txt_info, 1, wx.ALL , 20)
        box.Add(self.chx_etat, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
        box.Add(self.chk_cree_manche, 1, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        box.AddSizer(box_btn, 0, wx.EXPAND)

        self.SetSizer(box)
        self.Layout()

        self.Bind(wx.EVT_CHOICE, self.modif_etat, self.chx_etat)
        self.Bind(wx.EVT_CHECKBOX, self.modif_option, self.chk_cree_manche)

    def modif_etat(self, event):
        if event.GetString() == cst.FORFAIT:
            self.chk_cree_manche.SetValue(False)

    def modif_option(self, event):
        if event.IsChecked():
            self.chx_etat.SetSelection(self.chx_etat.FindString(cst.CHAPEAU))

    def etat(self):
        return self.chx_etat.GetString(self.chx_etat.GetSelection())

    def creer_manche(self):
        return self.chk_cree_manche.IsChecked()
