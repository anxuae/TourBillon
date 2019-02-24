#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import sys, os
import wx
import  wx.lib.printout as  printout

from tourbillon.trb_core import tournois
from tourbillon.trb_core import constantes as cst

from tourbillon.trb_gui import grille as grl

#--- Varibles globales ---------------------------------------------------------

TITRES = [(u"Place", 0.5),
          (u"N°", 0.5),
          (u"Noms", 4.7),
          (u"Victoires", 0.5),
          (u"Points", 0.5),
          (u"Chapeau", 0.5),
          (u"Nombre mini de billons en 1 partie", 0.8),
          (u"Nombre maxi de billons en 1 partie", 0.8),
          (u"Nombre moyen de billons / partie", 0.8),
          (u"Durée moyenne / partie", 0.8)]

#--- Dialog imprimer classement ------------------------------------------------

class DialogueImprimer(printout.PrintTable):
    def __init__(self, parent, classement):
        printout.PrintTable.__init__(self, parent)
        self.data = []

        for equipe, place in classement:
            self.data.append([place,
                              equipe.numero,
                              " / ".join([unicode(joueur) for joueur in equipe.joueurs()]),
                              equipe.total_victoires(),
                              equipe.total_points(),
                              equipe.total_chapeaux(),
                              equipe.min_billon(),
                              equipe.max_billon(),
                              equipe.moyenne_billon(),
                              grl.unicode_timedelta(equipe.moyenne_duree())])

        self.SetLandscape()
        self.SetRowLineSize(0, 2)
        self.SetRowSpacing(5, 5)
        self.text_font = { "Name": "Arial", "Size": 14, "Colour": [0, 0, 0], "Attr": [1, 0, 0] }

        self.label = []         # Titre des colonnes
        self.set_column = []    # Dimension des colonnes
        i = 0
        for titre, largeur in TITRES:
            self.label.append(titre)
            self.set_column.append(largeur)
            if i == 2:
                self.SetColAlignment(i, wx.ALIGN_LEFT)
            else:
                self.SetColAlignment(i, wx.ALIGN_CENTRE)
            i += 1

        self.SetColTextColour(0, wx.NamedColour('RED'))
        self.SetColTextColour(1, wx.NamedColour('BLUE'))
        self.SetColTextColour(2, wx.NamedColour('BLUE'))

        self.SetHeader(u"Tournoi de Billon du %s" % tournois.tournoi().debut.strftime('%d/%m/%Y'), colour = wx.NamedColour('BLACK'))

        self.SetHeader(u"Imprimé le : ", type = "Date & Time", align = wx.ALIGN_RIGHT, indent = -0.5, colour = wx.NamedColour('BLUE'))
        self.SetFooter(u"Page ", colour = wx.NamedColour('BLACK'), type = "Num")
