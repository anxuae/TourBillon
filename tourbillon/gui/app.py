# -*- coding: UTF-8 -*-

import sys
import wx

from wx.lib.agw import advancedsplash as aspl
from wx.lib.agw import toasterbox as toast

import tourbillon
from tourbillon.core import player
from tourbillon.gui import fenetre
from tourbillon import images, logger


class GuiLoggerHandler(logger.LoggerHandler):

    def __init__(self, parent):
        logger.LoggerHandler.__init__(self)
        self.parent = parent

    def afficher(self, record):
        if self.parent.IsShown():
            texte = self.format(record)
            tb = toast.ToasterBox(self.parent, toast.TB_SIMPLE, toast.TB_DEFAULT_STYLE, toast.TB_ONTIME | toast.TB_ONCLICK)

            w = 200
            h = 125
            tb.SetPopupSize((w, h))

            rect = self.parent.GetRect()
            x = rect[0] + rect[2] - w
            y = rect[1] + rect[3] - h
            tb.SetPopupPosition((x, y))

            tb.SetPopupPauseTime(3000)
            tb.SetPopupScrollSpeed(1)

            tb.SetPopupBackgroundColour(images.couleur('selection'))
            tb.SetPopupTextColour(images.couleur('texte_bouton'))

            tb.SetPopupText(texte)
            tb.SetPopupTextFont(wx.Font(12, wx.SWISS, wx.ITALIC, wx.NORMAL))

            tb.Play()


class FentetreSplash(aspl.AdvancedSplash):

    def __init__(self, parent=None, id=wx.ID_ANY, temps=10000):
        # Créer l'image
        bmap_unconvertedAplha = images.splash.GetBitmap()
        image = bmap_unconvertedAplha.ConvertToImage()
        image.ConvertAlphaToMask(threshold=128)
        bmap_convertedAlpha = image.ConvertToBitmap()

        # Créer la fenêtre
        aspl.AdvancedSplash.__init__(self, parent, id, bitmap=bmap_convertedAlpha, timeout=temps,
                                     agwStyle=aspl.AS_TIMEOUT | aspl.AS_CENTER_ON_SCREEN)

        # Afficher la version
        try:
            self.SetText("version %s.%s.%s" % tourbillon.__version__)
            self.SetTextFont(wx.Font(16, wx.ROMAN, wx.NORMAL, wx.NORMAL))
            self.SetTextPosition((385, 245))
        except:
            pass


class TourBillonGUI(wx.App):

    def __init__(self, config):
        self.config = config
        self.fenetre = None
        self.splash = None
        wx.App.__init__(self, False)
        self.SetAppName(tourbillon.__nom__)
        self.SetAppDisplayName(tourbillon.__nom__)

        # This catches events when the app is asked to activate by some other process
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

    def OnInit(self):
        """
        Afficher la fenetre splash et la fenêtre principale.
        """
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnShow, self._timer)

        player.charger_historique(self.config.get_typed('TOURNOI', 'historique'))

        def splash():
            self.splash = FentetreSplash(None, wx.ID_ANY)
            self.splash.Update()

        if sys.platform == 'darwin':
            # Bug dans AdvancedSplash: appeler la Splash lorsque la EventLoop est démarrée
            wx.CallAfter(splash)
        else:
            splash()

        self.fenetre = fenetre.FenetrePrincipale(self.config)
        if self.config.get_typed('INTERFACE', 'BAVARDE'):
            level = logger.INFO
        else:
            level = logger.CRITICAL
        logger.ajouter_handler(GuiLoggerHandler(self.fenetre), level, "%(message)s")

        # Laisser le temps du chargement avant affichage
        self._timer.Start(3000)
        return True

    def OnShow(self, event):
        """
        Changer la geometrie après initilisation de la fenetre
        (évite les problèmes de rafraichissement)
        """
        geo = self.config.get_typed('INTERFACE', 'geometrie')
        self.fenetre.SetPosition(geo[:2])
        self.fenetre.SetSize(geo[2:])
        self.fenetre.Show()

        if self.splash in list(wx.GetTopLevelWindows()):
            self.splash.Raise()  # Afficher au dessus de la fentre principale

        if self.config.get_typed('INTERFACE', 'maximiser') or self.config.get_typed('INTERFACE', 'plein_ecran'):
            self.fenetre.Maximize()
        self._timer.Stop()

    def MacOpenFile(self, fichier):
        """
        Appelé quand un fichier est déposé sur l'icon située dans le
        dock ou ouvert via le menu contextuel du Finder.
        """
        self.ouvrir(fichier)

    def BringWindowToFront(self):
        try:  # it's possible for this event to come when the frame is closed
            self.GetTopWindow().Raise()
        except:
            pass

    def OnActivate(self, event):
        # if this is an activate event, rather than something else, like iconize.
        if event.GetActive():
            self.BringWindowToFront()
        event.Skip()

    def MacReopenApp(self):
        """Called when the doc icon is clicked, and ???"""
        self.BringWindowToFront()

    def run(self):
        self.MainLoop()

    def ouvrir(self, fichier):
        self.fenetre.ouvrir(fichier)
