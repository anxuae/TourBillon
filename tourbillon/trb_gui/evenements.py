#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import wx

#--- Evenements ----------------------------------------------------------------

class RafraichirEvent(wx.PyCommandEvent):
    TYPE = wx.NewEventType()

    def __init__(self, id, quoi='tout'):
        wx.PyCommandEvent.__init__(self, RafraichirEvent.TYPE, id)
        self.quoi = quoi

EVT_RAFRAICHIR = wx.PyEventBinder(RafraichirEvent.TYPE, expectedIDs=1)

class ListItemCheckedEvent(wx.PyCommandEvent):
    TYPE = wx.NewEventType()

    def __init__(self, id, index, checked):
        wx.PyCommandEvent.__init__(self, ListItemCheckedEvent.TYPE, id)
        self.index = index
        self.checked = checked

EVT_LIST_ITEM_CHECKED = wx.PyEventBinder(ListItemCheckedEvent.TYPE, expectedIDs=1)

class PreferencesEvent(wx.PyCommandEvent):
    TYPE = wx.NewEventType()

    def __init__(self, id, page=1):
        wx.PyCommandEvent.__init__(self, PreferencesEvent.TYPE, id)
        self.page = page

EVT_PREFERENCES = wx.PyEventBinder(PreferencesEvent.TYPE, expectedIDs=1)

class ProgressionTirageEvent(wx.PyCommandEvent):
    TYPE = wx.NewEventType()

    def __init__(self, id, valeur= -1, message=None, resultat={'tirage':[], 'chapeaux':[]}, erreur=None):
        wx.PyCommandEvent.__init__(self, ProgressionTirageEvent.TYPE, id)
        self.valeur = valeur
        self.message = message
        self.resultat = resultat
        self.erreur = erreur

EVT_PROGRESSION_TIRAGE = wx.PyEventBinder(ProgressionTirageEvent.TYPE, expectedIDs=1)

class MenuRechercheEvent(wx.PyCommandEvent):
    TYPE = wx.NewEventType()

    def __init__(self, id, index, texte):
        wx.PyCommandEvent.__init__(self, MenuRechercheEvent.TYPE, id)
        self.index = index
        self.texte = texte

EVT_MENU_RECHERCHE = wx.PyEventBinder(MenuRechercheEvent.TYPE, expectedIDs=1)
