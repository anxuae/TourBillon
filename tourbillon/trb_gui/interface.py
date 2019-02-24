#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import sys
import os
from datetime import datetime
import wx
from wx.lib.agw import advancedsplash as aspl
import wx.lib.scrolledpanel as scrolled
from wx.lib.wordwrap import wordwrap

import tourbillon
from tourbillon.trb_core import constantes as cst
from tourbillon.trb_core import tournois, joueurs
from tourbillon.trb_core import exceptions as expt

from tourbillon import images
from tourbillon.trb_gui import barres
from tourbillon.trb_gui import evenements as evt
from tourbillon.trb_gui import grille as grl
from tourbillon.trb_gui import dlgequipe as dlgeq
from tourbillon.trb_gui import dlgpartie as dlgpa
from tourbillon.trb_gui import dlgresultat as dlgre
from tourbillon.trb_gui import dlgimpression as dlgim
from tourbillon.trb_gui import dlgpreferences as dlgpref

#--- Variables Globales --------------------------------------------------------

FILTRE_FICHIER = u"Fichier Tourbillon (*.trb)|*.trb|"\
    "All files (*.*)|*.*"

#--- Classes -------------------------------------------------------------------


class FentetreSplash(aspl.AdvancedSplash):

    def __init__(self, parent=None, id=wx.ID_ANY, temps=5000):
        # Créer l'image
        bmap_unconvertedAplha = images.splash.GetBitmap()
        image = bmap_unconvertedAplha.ConvertToImage()
        image.ConvertAlphaToMask(threshold=128)
        bmap_convertedAlpha = image.ConvertToBitmap()

        # Créer la fenêtre
        aspl.AdvancedSplash.__init__(self, parent, id, bitmap=bmap_convertedAlpha, timeout=temps,
                                     agwStyle=aspl.AS_TIMEOUT | aspl.AS_CENTER_ON_SCREEN)


class TourBillonGUI(wx.Frame):

    def __init__(self, nom, config):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=nom,
                          size=(640, 400), style = wx.DEFAULT_FRAME_STYLE)

        # Initialiser
        self.config = config
        self.config.get_typed('INTERFACE', 'plein_ecran')
        if self.config.get_typed('INTERFACE', 'maximiser') or self.config.get_typed('INTERFACE', 'plein_ecran'):
            self.Maximize()
        else:
            geo = self.config.get_typed('INTERFACE', 'geometrie')
            self.SetPosition(geo[:2])
            self.SetSize(geo[2:])
        joueurs.charger_historique(config.get_typed('TOURNOI', 'historique'))

        # Fenêtre informations montrée
        self.fenetre_info = False

        # Icon
        self.SetIcon(images.TourBillon_icon())

        # Créer la barre de menu
        self.barre_menu = barres.BarreMenu(self)
        self.SetMenuBar(self.barre_menu)

        self.Bind(wx.EVT_MENU, self.nouveau, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.charger, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.enregistrer, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.enregistrer_sous, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.apercu_avant_impression, id=wx.ID_PREVIEW_PRINT)
        self.Bind(wx.EVT_MENU, self.imprimer, id=wx.ID_PRINT)
        self.Bind(wx.EVT_MENU, self.quitter, id=wx.ID_EXIT)

        self.Bind(wx.EVT_MENU, self.afficher_info, id=barres.ID_INFO)
        self.Bind(wx.EVT_MENU, self.afficher_tirage, id=barres.ID_TIRAGE)

        self.Bind(wx.EVT_MENU, self.nouvelle_equipe, id=barres.ID_NOUVELLE_E)
        self.Bind(wx.EVT_MENU, self.modifier_equipe, id=barres.ID_MODIFIER_E)
        self.Bind(wx.EVT_MENU, self.supprimer_equipe, id=barres.ID_SUPPRIMER_E)
        self.Bind(wx.EVT_MENU, self.nouvelle_partie, id=barres.ID_NOUVELLE_P)
        self.Bind(wx.EVT_MENU, self.supprimer_partie, id=barres.ID_SUPPRIMER_P)
        self.Bind(wx.EVT_MENU, self.entrer_resultats, id=barres.ID_RESULTATS)
        self.Bind(wx.EVT_MENU, self.classement, id=barres.ID_CLASSEMENT)
        self.Bind(wx.EVT_MENU, self.preferences, id=wx.ID_PREFERENCES)

        self.Bind(wx.EVT_MENU, self.a_propos_de, id=wx.ID_ABOUT)

        # Créer la barre de statut
        self.barre_etat = barres.BarreEtat(self)
        self.SetStatusBar(self.barre_etat)

        # Créer la grille
        self.grille = grl.GrillePanel(self)

        # Créer la barre des boutons (pas la guerre)
        self.barre_bouton = barres.BarreBouton(self)

        self.Bind(wx.EVT_BUTTON, self.afficher_partie_prec, self.barre_bouton.btn_precedente)
        self.Bind(wx.EVT_BUTTON, self.afficher_partie_suiv, self.barre_bouton.btn_suivante)

        self.Bind(wx.EVT_BUTTON, self.enregistrer, id=wx.ID_SAVE)
        self.Bind(wx.EVT_BUTTON, self.afficher_info, id=barres.ID_INFO)
        self.Bind(wx.EVT_BUTTON, self.afficher_tirage, id=barres.ID_TIRAGE)
        self.Bind(wx.EVT_BUTTON, self.nouvelle_equipe, id=barres.ID_NOUVELLE_E)
        self.Bind(wx.EVT_BUTTON, self.nouvelle_partie, id=barres.ID_NOUVELLE_P)
        self.Bind(wx.EVT_BUTTON, self.entrer_resultats, id=barres.ID_RESULTATS)
        self.Bind(wx.EVT_BUTTON, self.entrer_resultats, id=barres.ID_RESULTATS)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.grille.rechercher_suivant, id=wx.ID_FIND)
        self.Bind(wx.EVT_TEXT_ENTER, self.grille.rechercher_suivant, id=wx.ID_FIND)
        self.Bind(wx.EVT_TEXT, self.grille.rechercher, id=wx.ID_FIND)
        self.Bind(evt.EVT_MENU_RECHERCHE, self.grille.chg_recherche_colonne, self.barre_bouton)

        # Position des widgets
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.barre_bouton, 0, wx.EXPAND)
        box.Add((20, 20))
        box.Add(self.grille, 1, wx.EXPAND)
        self.SetSizer(box)

        self.Layout()

        # Autres événements
        self.Bind(wx.EVT_CLOSE, self.quitter)
        self.Bind(evt.EVT_RAFRAICHIR, self.rafraichir)
        self.grille.Bind(grl.grid.EVT_GRID_CELL_LEFT_DCLICK, self.grille_double_click)
        self.grille.Bind(wx.EVT_KEY_DOWN, self.grille_enter)

        # Rafraichir
        wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

    def grille_enter(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.grille_double_click(event)
        else:
            event.Skip()

    def grille_double_click(self, event):
        if tournois.tournoi() is not None:
            if self.grille.selection() is not None:
                statut = tournois.tournoi().statut
                if statut == cst.T_INSCRIPTION or (statut == cst.T_ATTEND_TIRAGE and tournois.tournoi().nb_parties() == 0):
                    self.modifier_equipe(event)
                else:
                    self.entrer_resultats(event)

    def rafraichir(self, event):
        t = tournois.tournoi()

        # Barre de menu
        if event.quoi == 'menu' or event.quoi == 'tout':
            if t is None:
                etat = None
                nom = ''
            else:
                nom = 'Tournoi  du %s' % t.debut.strftime('%d/%m/%Y')
                if t.statut == cst.T_INSCRIPTION and t.nb_equipes() == 0:
                    etat = '0 equipe'
                elif t.statut == cst.T_ATTEND_TIRAGE and t.nb_parties() == 0:
                    etat = '0 partie'
                else:
                    etat = t.statut
            self.barre_menu._rafraichir(etat)
            self.barre_bouton._rafraichir(etat, nom)

        # Barre d'état
        if event.quoi == 'etat' or event.quoi == 'tout':
            if t is None:
                self.barre_etat._rafraichir('', 0, 0, False)
            else:
                self.barre_etat._rafraichir(t.debut.strftime('%Hh%M'), t.nb_equipes(), t.nb_parties(), t.modifie)

        # Equipes
        p = self.barre_bouton.partie()
        if event.quoi == 'tout':
            if tournois.tournoi() is None:
                self.grille._rafraichir()
            else:
                for equipe in tournois.tournoi().equipes():
                    self.grille._rafraichir(equipe=equipe, partie=p)

        elif event.quoi.startswith('equipe'):
            num = int(event.quoi.split('_')[1])
            self.grille._rafraichir(equipe=tournois.tournoi().equipe(num), partie=p)

        # Classement
        if event.quoi == 'classement' or event.quoi == 'tout':
            if tournois.tournoi() is not None:
                avec_duree = self.config.get_typed('TOURNOI', 'classement_duree')
                self.grille._rafraichir(classement=tournois.tournoi().classement(avec_duree))
            else:
                self.grille._rafraichir(classement={})

    def demande_enregistrement(self):
        if tournois.tournoi() is not None:
            if tournois.tournoi().modifie:
                dlg = wx.MessageDialog(self, u"Le tournoi en cours n'est pas enregistré, si vous cliquez sur NON, les données seront perdues.",
                                       caption=u"Voulez-vous enregistrer le tournoi en cours?", style=wx.YES_NO | wx.ICON_QUESTION)
                val = dlg.ShowModal()
                dlg.Destroy()
                if val == wx.ID_YES:
                    self.enregistrer_sous(None)

    def nouveau(self, event):
        self.demande_enregistrement()

        if self.config.get_typed("INTERFACE", 'nouveau_affiche_preferences'):
            self.preferences(evt.PreferencesEvent(self.GetId(), 1))

        equipes_par_manche = self.config.get_typed("TOURNOI", "equipes_par_manche")
        joueurs_par_equipe = self.config.get_typed("TOURNOI", "joueurs_par_equipe")
        points_par_manche = self.config.get_typed("TOURNOI", "points_par_manche")
        tournois.nouveau_tournoi(equipes_par_manche, points_par_manche, joueurs_par_equipe)

        # Rafraichir
        self.grille.effacer()
        self.barre_bouton.chg_partie()
        wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

    def charger(self, event):
        self.demande_enregistrement()
        if tournois.FICHIER_TOURNOI is not None:
            l = os.path.split(tournois.FICHIER_TOURNOI)
            d = l[0]
            f = l[1]
        else:
            d = self.config.get('INTERFACE', 'enregistrement')
            f = ''

        dlg = wx.FileDialog(self, message="Charger", defaultDir=d, defaultFile=f,
                            wildcard=FILTRE_FICHIER, style=wx.OPEN)
        val = dlg.ShowModal()

        if val == wx.ID_OK:
            fichier = dlg.GetPath()
            tournois.charger_tournoi(fichier)

            # Rafraichir
            self.barre_bouton.chg_partie(tournois.tournoi().nb_parties())
            self.grille.effacer()
            for equipe in tournois.tournoi().equipes():
                self.grille.ajout_equipe(equipe)
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

        dlg.Destroy()

    def enregistrer(self, event):
        if tournois.FICHIER_TOURNOI is None:
            self.enregistrer_sous(event)
        else:
            tournois.enregistrer_tournoi()

        # Enregistrer l'historique joueurs
        joueurs.enregistrer_historique()
        # Rafraichir
        wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'etat'))

    def enregistrer_auto(self):
        if self.config.get_typed('INTERFACE', 'enregistrement_auto') and tournois.FICHIER_TOURNOI is not None:
            self.enregistrer(None)

    def enregistrer_sous(self, event):
        if tournois.FICHIER_TOURNOI is not None:
            l = os.path.split(tournois.FICHIER_TOURNOI)
            d = l[0]
            f = l[1]
        else:
            d = self.config.get('INTERFACE', 'enregistrement')
            f = u"tournoi_billon_%s.trb" % datetime.now().strftime('%d/%m/%Y')
        dlg = wx.FileDialog(self, message="Enregistrer", defaultDir=d, defaultFile=f,
                            wildcard=FILTRE_FICHIER, style=wx.SAVE)
        val = dlg.ShowModal()

        if val == wx.ID_OK:
            fichier = dlg.GetPath()
            tournois.enregistrer_tournoi(fichier)

            # Rafraichir
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'etat'))

        dlg.Destroy()

    def apercu_avant_impression(self, event):
        avec_duree = self.config.get_typed('TOURNOI', 'classement_duree')
        dlg = dlgim.DialogueImprimer(self, tournois.tournoi().classement(avec_duree))
        dlg.Preview()

    def imprimer(self, event):
        avec_duree = self.config.get_typed('TOURNOI', 'classement_duree')
        dlg = dlgim.DialogueImprimer(self, tournois.tournoi().classement(avec_duree))
        dlg.Print()

    def quitter(self, event):
        self.demande_enregistrement()
        # Enregistrer la géométrie de l'interface
        if self.IsMaximized():
            self.config.set('INTERFACE', 'maximiser', 'True')
        else:
            self.config.set('INTERFACE', 'maximiser', 'False')
            self.config.set('INTERFACE', 'geometrie', str(self.GetPositionTuple() + self.GetSizeTuple()))

        self.Destroy()
        event.Skip()

    def afficher_info(self, event):
        self.fenetre_info = not self.fenetre_info

        self.barre_bouton.FindItemById(barres.ID_INFO).Check(self.fenetre_info)
        self.barre_menu.FindItemById(barres.ID_INFO).Check(self.fenetre_info)
        print self.fenetre_info

    def afficher_tirage(self, event):
        num = self.barre_bouton.partie()

        dlg = dlgpa.DialogueAfficherTirage(self, num)
        val = dlg.Show()

    def afficher_partie_prec(self, event):
        if tournois.tournoi() is None:
            self.barre_bouton.chg_partie()
        else:
            try:
                tournois.tournoi().partie(self.barre_bouton.partie() - 1)
                self.barre_bouton.chg_partie(self.barre_bouton.partie() - 1)
            except expt.NumeroError, e:
                self.barre_etat.SetStatusText(unicode(e))

            # Rafraichir
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

    def afficher_partie_suiv(self, event):
        if tournois.tournoi() is None:
            self.barre_bouton.chg_partie()
        else:
            try:
                tournois.tournoi().partie(self.barre_bouton.partie() + 1)
                self.barre_bouton.chg_partie(self.barre_bouton.partie() + 1)
            except expt.NumeroError, e:
                self.barre_etat.SetStatusText(unicode(e))

            # Rafraichir
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

    def nouvelle_equipe(self, event):
        val = wx.ID_OK

        def creer(info):
            equipe = tournois.tournoi().ajout_equipe(info['numero'])
            for joueur in info['joueurs']:
                equipe.ajout_joueur(joueur[0], joueur[1], joueur[2])
            return equipe

        while val == wx.ID_OK:
            dlg = dlgeq.DialogueEquipe(self, dlgeq.STYLE_AJOUTER,
                                       numero_affiche=tournois.tournoi().nouveau_numero_equipe())
            val = dlg.ShowModal()
            info = dlg.donnees()
            dlg.Destroy()

            if val == wx.ID_OK:

                if tournois.tournoi().nb_parties() == 0:
                    # Le tournoi n'est pas commencé
                    equipe = creer(info)

                    # Rafraichir
                    self.grille.ajout_equipe(equipe)
                    self.enregistrer_auto()
                    wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

                elif tournois.tournoi().statut == cst.T_PARTIE_EN_COURS:
                    # Une partie est en cours: choix etat pour la partie en cours
                    dlg = dlgeq.DialogueMessageEquipe(self, info['numero'])
                    val = dlg.ShowModal()
                    if val == wx.ID_OK:
                        equipe = creer(info)
                        for partie in tournois.tournoi().parties():
                            if partie != tournois.tournoi().partie_courante():
                                # L'équipe est FORFAIT pour les autres parties.
                                partie.ajout_equipe(equipe, cst.FORFAIT)
                            else:
                                partie.ajout_equipe(equipe, dlg.etat(), dlg.creer_manche())

                        # Rafraichir
                        self.grille.ajout_equipe(equipe)
                        self.enregistrer_auto()
                        wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))
                    dlg.Destroy()

                else:
                    # Les parties sont toutes terminées
                    texte = u"L'équipe sera considérée comme forfait pour toutes les parties déjà jouées,\
cliquez sur ANNULER si vous ne voulez pas ajouter cette nouvelle équipe."
                    dlg = wx.MessageDialog(self, texte, caption=u"Tournoi en cours",
                                           style=wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    val = dlg.ShowModal()
                    dlg.Destroy()
                    if val == wx.ID_OK:
                        equipe = creer(info)
                        for partie in tournois.tournoi().parties():
                            partie.ajout_equipe(equipe, cst.FORFAIT)

                        # Rafraichir
                        self.grille.ajout_equipe(equipe)
                        self.enregistrer_auto()
                        wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

    def modifier_equipe(self, event):
        num = self.grille.selection()
        if num is None:
            num = 1

        dlg = dlgeq.DialogueEquipe(self, dlgeq.STYLE_MOFIFIER, choix=map(
            int, tournois.tournoi().equipes()), numero_affiche=num)
        val = dlg.ShowModal()

        if val == wx.ID_OK:
            info = dlg.donnees()
            equipe = tournois.tournoi().equipe(info['numero'])
            equipe.suppr_joueurs()
            for joueur in info['joueurs']:
                equipe.ajout_joueur(joueur[0], joueur[1], joueur[2])

            # Rafraichir
            self.enregistrer_auto()
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'etat'))
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'equipe_' + str(equipe.numero)))

        dlg.Destroy()

    def supprimer_equipe(self, event):
        num = self.grille.selection()
        if num is None:
            num = 1

        dlg = dlgeq.DialogueEquipe(self, dlgeq.STYLE_SUPPRIMER, choix=map(
            int, tournois.tournoi().equipes()), numero_affiche=num)
        val = dlg.ShowModal()

        if val == wx.ID_OK:
            info = dlg.donnees()

            # Rafraichir
            self.grille.suppr_equipe(tournois.tournoi().equipe(info['numero']))
            tournois.tournoi().suppr_equipe(info['numero'])
            self.enregistrer_auto()
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

        dlg.Destroy()

    def nouvelle_partie(self, event):
        dlg = dlgpa.DialogueAjouterPartie(self, self.config)
        dlg.Bind(evt.EVT_PREFERENCES, self.preferences, id=wx.ID_PREFERENCES)
        val = dlg.ShowModal()

        if val == True:
            partie = tournois.tournoi().ajout_partie()
            partie.demarrer(dlg.tirage(), dlg.chapeaux())

            # Rafraichir
            self.barre_bouton.chg_partie(partie.numero)
            self.enregistrer_auto()
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

        dlg.Destroy()

    def supprimer_partie(self, event):
        num = self.barre_bouton.partie()

        dlg = dlgpa.DialogueSupprimerPartie(self, map(int, tournois.tournoi().parties()), num)
        val = dlg.ShowModal()

        if val == wx.ID_OK:
            tournois.tournoi().suppr_partie(int(dlg.numero()))
            if tournois.tournoi().nb_parties() == 0:
                self.barre_bouton.chg_partie(0)
            elif tournois.tournoi().nb_parties() >= num:
                self.barre_bouton.chg_partie(num)
            else:
                self.barre_bouton.chg_partie(tournois.tournoi().nb_parties())

            # Rafraichir
            self.enregistrer_auto()
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

        dlg.Destroy()

    def entrer_resultats(self, event):
        num_partie = int(self.barre_bouton.partie())
        num_equipe = self.grille.selection()
        if num_equipe is None:
            num_equipe = 1
        else:
            num_equipe = int(num_equipe)
        etat = tournois.tournoi().equipe(num_equipe).resultat(num_partie)['etat']

        if etat != cst.FORFAIT and etat != cst.CHAPEAU:
            dlg = dlgre.DialogueResultat(self, num_partie, num_equipe)
            val = dlg.ShowModal()

            if val == wx.ID_OK:
                d = dlg.donnees()
                if dlg.fin():
                    fin = datetime.now()
                else:
                    fin = None
                tournois.tournoi().partie(num_partie).resultat(d, fin)

                # Rafraichir
                self.enregistrer_auto()
                wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'tout'))

            dlg.Destroy()
        else:
            self.barre_etat.SetStatusText(u"Le score d'une équipe %s n'est pas modifiable." % etat)

    def classement(self, event):
        print "classement"

    def preferences(self, event):
        if type(event) == evt.PreferencesEvent:
            # Ouverture d'une page spécifique
            dlg = dlgpref.DialoguePreferences(self, self.config, event.page)
        else:
            # Page générale
            dlg = dlgpref.DialoguePreferences(self, self.config)

        val = dlg.ShowModal()

        if val == wx.ID_OK:
            for section in dlg.donnees():
                for nom, valeur in dlg.donnees()[section].items():
                    self.config.set(section, nom, unicode(valeur))

        dlg.Destroy()

    def a_propos_de(self, event):
        info = wx.AboutDialogInfo()
        info.Name = "TourBillon"
        info.Version = "5.0.0"
        info.Copyright = "(C) 2010 La Billonnière"
        info.Description = wordwrap(
            "A \"hello world\" program is a software program that prints out "
            "\"Hello world!\" on a display device. It is used in many introductory "
            "tutorials for teaching a programming language."

            "\n\nSuch a program is typically one of the simplest programs possible "
            "in a computer language. A \"hello world\" program can be a useful "
            "sanity test to make sure that a language's compiler, development "
            "environment, and run-time environment are correctly installed.",
            800, wx.ClientDC(self))
        info.WebSite = ("http://en.wikipedia.org/wiki/Hello_world", "Hello World home page")
        info.Developers = ["La Billonnière"]

        info.License = wordwrap(tourbillon.__licence__, 800, wx.ClientDC(self))

        wx.AboutBox(info)

#--- Application ---------------------------------------------------------------


class Application(wx.App):

    def __init__(self, *args, **kwargs):
        wx.App.__init__(self, *args, **kwargs)

        # This catches events when the app is asked to activate by some other
        # process
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

    def OnInit(self):
        """
        Afficher la fenetre splash.
        """
        wx.InitAllImageHandlers()
        spl = FentetreSplash(None)
        return True

    def BringWindowToFront(self):
        """
        Il est possible que cet événement survinne quand la denière
        fenêtre est fermée.
        """
        try:
            self.GetTopWindow().Raise()
        except:
            pass

    def OnActivate(self, event):
        """
        Afficher les fenêtres de l'application si elle prend le focus.
        """
        if event.GetActive():
            self.BringWindowToFront()
        event.Skip()

    def MacReopenApp(self):
        """
        Appelé quant l'icone du DOC est cliquée.
        """
        self.BringWindowToFront()


def run(config):
    nom = "TourBillon v %s.%s.%s" % tourbillon.__version__

    # Créer l'application
    app = Application(False)
    app.SetAppName(nom)

    # Créer fenêtre GUI
    fen = TourBillonGUI(nom, config)

    # Afficher la fenêtre principale
    fen.Show()

    app.MainLoop()
