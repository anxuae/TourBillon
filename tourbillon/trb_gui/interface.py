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
from wx.lib.agw import toasterbox as toast

import tourbillon
from tourbillon.trb_core import constantes as cst
from tourbillon.trb_core import tournoi, joueur
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
from tourbillon.trb_gui import dlginformations as dlginfo

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


class FenetrePrincipale(wx.Frame):

    def __init__(self, config):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=tourbillon.__nom__,
                          size=(640, 400), style=wx.DEFAULT_FRAME_STYLE)
        self.SetBackgroundColour(images.couleur('grille'))

        # Initialiser
        self.config = config
        self.config.get_typed('INTERFACE', 'plein_ecran')
        if self.config.get_typed('INTERFACE', 'maximiser') or self.config.get_typed('INTERFACE', 'plein_ecran'):
            self.Maximize()
        else:
            geo = self.config.get_typed('INTERFACE', 'geometrie')
            self.SetPosition(geo[:2])
            self.SetSize(geo[2:])
        joueur.charger_historique(config.get_typed('TOURNOI', 'historique'))

        # Fenêtre informations montrée
        self.fenetre_affichage = dlginfo.DialogueInformations(self, self.config)
        self.affichage_visible = False
        self.fenetre_affichage.Bind(wx.EVT_CLOSE, self.masquer_info)

        # Icon
        self.SetIcon(images.TourBillon_icon())

        # Créer la barre de menu
        self.barre_menu = barres.BarreMenu(self)
        self.SetMenuBar(self.barre_menu)

        self.Bind(wx.EVT_MENU, self.nouveau, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.ouvrir, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.enregistrer, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.enregistrer_sous, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.apercu_avant_impression, id=wx.ID_PREVIEW_PRINT)
        self.Bind(wx.EVT_MENU, self.imprimer, id=wx.ID_PRINT)
        self.Bind(wx.EVT_MENU, self.quitter, id=wx.ID_EXIT)

        self.Bind(wx.EVT_MENU, self.afficher_statistiques, id=barres.ID_STATISTIQUES)
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
        chemin_image = self.config.get_typed('INTERFACE', 'image')
        if not chemin_image:
            chemin_image = 'fond.jpg'
        self.grille = grl.GrillePanel(self, images.bitmap(chemin_image))
        self.barre_menu.FindItemById(barres.ID_STATISTIQUES).Check(
            self.config.get_typed('INTERFACE', 'afficher_statistiques'))
        self.afficher_statistiques(False)

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
        if tournoi.tournoi() is not None:
            if self.grille.selection() is not None:
                statut = tournoi.tournoi().statut
                if statut == cst.T_INSCRIPTION or (statut == cst.T_ATTEND_TIRAGE and tournoi.tournoi().nb_parties() == 0):
                    self.modifier_equipe(event)
                else:
                    self.entrer_resultats(event)

    def rafraichir(self, event):
        t = tournoi.tournoi()

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
                self.barre_etat._rafraichir('', 0, 0, 0, False)
            else:
                # Indication équipe incomplète
                nb_incompletes = 0
                num_partie = self.barre_bouton.numero()
                if self.barre_bouton.numero() > 0:
                    for equipe in tournoi.tournoi().partie(num_partie).equipes():
                        if equipe.resultat(num_partie).etat is None:
                            nb_incompletes += 1
                self.barre_etat._rafraichir(t.debut.strftime('%Hh%M'), t.nb_parties(), t.nb_equipes(),
                                            nb_incompletes / tournoi.tournoi().equipes_par_manche, t.modifie)

        # Equipes
        p = self.barre_bouton.numero()
        if event.quoi == 'tout':
            if tournoi.tournoi() is None:
                self.grille._rafraichir()
            else:
                for equipe in tournoi.tournoi().equipes():
                    self.grille._rafraichir(equipe=equipe, partie=p)

        elif event.quoi.startswith('equipe'):
            num = int(event.quoi.split('_')[1])
            self.grille._rafraichir(equipe=tournoi.tournoi().equipe(num), partie=p)

        # Classement
        if event.quoi == 'classement' or event.quoi == 'tout':
            if tournoi.tournoi() is not None:
                avec_victoires = self.config.get_typed('TOURNOI', 'CLASSEMENT_VICTOIRES')
                avec_duree = self.config.get_typed('TOURNOI', 'CLASSEMENT_DUREE')
                self.grille._rafraichir(classement=tournoi.tournoi().classement(avec_victoires, avec_duree))
            else:
                self.grille._rafraichir(classement={})

        # Informations
        if t is not None:
            self.fenetre_affichage._rafraichir(t.statut)

        # fond
        if event.quoi == 'fond':
            chemin_image = self.config.get_typed('INTERFACE', 'image')
            if not chemin_image:
                chemin_image = 'fond.jpg'
            self.grille.chg_fond(images.bitmap(chemin_image))

    def info(self, texte):
        if self.config.get_typed('INTERFACE', 'BAVARDE'):
            tb = toast.ToasterBox(self, toast.TB_SIMPLE, toast.TB_DEFAULT_STYLE, toast.TB_ONTIME | toast.TB_ONCLICK)

            w = 200
            h = 125
            tb.SetPopupSize((w, h))

            rect = self.GetRect()
            x = rect[0] + rect[2] - w
            y = rect[1] + rect[3] - h - self.barre_etat.GetSize()[1] - 5
            tb.SetPopupPosition((x, y))

            tb.SetPopupPauseTime(3000)
            tb.SetPopupScrollSpeed(1)

            tb.SetPopupBackgroundColour(images.couleur('selection'))
            tb.SetPopupTextColour(images.couleur('texte_bouton'))

            tb.SetPopupText(texte)
            tb.SetPopupTextFont(wx.Font(12, wx.SWISS, wx.ITALIC, wx.NORMAL))

            tb.Play()

    def nouveau(self, event):
        ret = self.demande_enregistrement()

        if ret != wx.ID_CANCEL:
            if self.config.get_typed("INTERFACE", 'NOUVEAU_AFFICHE_PREFERENCES'):
                ret = self.preferences(evt.PreferencesEvent(self.GetId(), 1))
            else:
                ret = wx.ID_OK

            if ret == wx.ID_OK:
                tournoi.nouveau_tournoi(self.config.get_typed("TOURNOI", "EQUIPES_PAR_MANCHE"),
                                        self.config.get_typed("TOURNOI", "POINTS_PAR_MANCHE"),
                                        self.config.get_typed("TOURNOI", "JOUEURS_PAR_EQUIPE"))

                # Rafraichir
                self.grille.effacer()
                self.barre_bouton.chg_partie()
                wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

                self.info(u"Il est %s, un nouveau tournoi commence..." % tournoi.tournoi().debut.strftime('%Hh%M'))

    def ouvrir(self, event):
        ret = self.demande_enregistrement()

        if ret != wx.ID_CANCEL:
            if tournoi.FICHIER_TOURNOI is not None:
                l = os.path.split(tournoi.FICHIER_TOURNOI)
                d = l[0]
                f = l[1]
            else:
                d = self.config.get('INTERFACE', 'ENREGISTREMENT')
                f = ''

            dlg = wx.FileDialog(self, message="Ouvrir", defaultDir=d, defaultFile=f,
                                wildcard=FILTRE_FICHIER, style=wx.OPEN)
            ret = dlg.ShowModal()

            if ret == wx.ID_OK:
                fichier = dlg.GetPath()
                tournoi.charger_tournoi(fichier)

                # Rafraichir
                self.barre_bouton.chg_partie(tournoi.tournoi().nb_parties())
                self.grille.effacer()
                for equipe in tournoi.tournoi().equipes():
                    self.grille.ajout_equipe(equipe)
                wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

                self.info(u"Chargé, prêt à jouer mon commandant!")

            dlg.Destroy()

    def demande_enregistrement(self):
        continuer = wx.ID_OK
        if tournoi.tournoi() is not None:
            if tournoi.tournoi().modifie:
                dlg = wx.MessageDialog(self, u"Le tournoi en cours n'est pas enregistré, si vous cliquez sur NON, les données seront perdues.",
                                       caption=u"Voulez-vous enregistrer le tournoi en cours?", style=wx.CANCEL | wx.YES | wx.NO | wx.ICON_QUESTION)
                ret = dlg.ShowModal()
                dlg.Destroy()
                if ret == wx.ID_YES:
                    continuer = self.enregistrer_sous(None)
                elif ret == wx.ID_CANCEL:
                    continuer = wx.ID_CANCEL

        return continuer

    def enregistrer(self, event):
        if tournoi.FICHIER_TOURNOI is None:
            self.enregistrer_sous(event)
        else:
            tournoi.enregistrer_tournoi()

        # Enregistrer l'historique joueurs
        joueur.enregistrer_historique()
        # Rafraichir
        wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'etat'))

    def enregistrer_auto(self):
        if self.config.get_typed('INTERFACE', 'ENREGISTREMENT_AUTO') and tournoi.FICHIER_TOURNOI is not None:
            self.enregistrer(None)

    def enregistrer_sous(self, event):
        if tournoi.FICHIER_TOURNOI is not None:
            l = os.path.split(tournoi.FICHIER_TOURNOI)
            d = l[0]
            f = l[1]
        else:
            d = self.config.get('INTERFACE', 'ENREGISTREMENT')
            f = u"tournoi_billon_%s.trb" % datetime.now().strftime('%d/%m/%Y')
        dlg = wx.FileDialog(self, message="Enregistrer", defaultDir=d, defaultFile=f,
                            wildcard=FILTRE_FICHIER, style=wx.SAVE)
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            fichier = dlg.GetPath()
            p, ext = os.path.splitext(fichier)
            if ext != '.trb':
                fichier += '.trb'
            tournoi.enregistrer_tournoi(fichier)

            # Rafraichir
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'etat'))
            self.info(u"C'est dans la boîte.")

        dlg.Destroy()
        return ret

    def apercu_avant_impression(self, event):
        avec_victoires = self.config.get_typed('TOURNOI', 'CLASSEMENT_VICTOIRES')
        avec_duree = self.config.get_typed('TOURNOI', 'CLASSEMENT_DUREE')
        dlg = dlgim.DialogueImprimer(self, tournoi.tournoi().classement(avec_victoires, avec_duree))
        dlg.Preview()

    def imprimer(self, event):
        avec_victoires = self.config.get_typed('TOURNOI', 'CLASSEMENT_VICTOIRES')
        avec_duree = self.config.get_typed('TOURNOI', 'CLASSEMENT_DUREE')
        dlg = dlgim.DialogueImprimer(self, tournoi.tournoi().classement(avec_victoires, avec_duree))
        dlg.Print()

    def quitter(self, event):
        ret = self.demande_enregistrement()

        if ret != wx.ID_CANCEL:
            # Enregistrer la géométrie de l'interface
            if self.IsMaximized():
                self.config.set('INTERFACE', 'MAXIMISER', 'True')
            else:
                self.config.set('INTERFACE', 'MAXIMISER', 'False')
                self.config.set('INTERFACE', 'GEOMETRIE', str(self.GetPositionTuple() + self.GetSizeTuple()))
            self.config.set('INTERFACE', 'afficher_statistiques', str(
                self.barre_menu.FindItemById(barres.ID_STATISTIQUES).IsChecked()))

            self.Destroy()
            event.Skip()

    def afficher_statistiques(self, event):
        """
        Affiche la grille des statistiques du
        tournoi en cours.
        """
        valeur = self.barre_menu.FindItemById(barres.ID_STATISTIQUES).IsChecked()
        self.grille.afficher_statistiques(valeur)

    def afficher_info(self, event):
        self.affichage_visible = not self.affichage_visible

        if self.affichage_visible:
            self.barre_bouton.FindItemById(barres.ID_INFO).Check(self.affichage_visible)
            self.barre_menu.FindItemById(barres.ID_INFO).Check(self.affichage_visible)

            self.fenetre_affichage.Show()
            self.SetFocus()
        else:
            self.fenetre_affichage.Close()

    def masquer_info(self, event):
        self.affichage_visible = False
        self.barre_bouton.FindItemById(barres.ID_INFO).Check(self.affichage_visible)
        self.barre_menu.FindItemById(barres.ID_INFO).Check(self.affichage_visible)
        event.Skip()

    def afficher_tirage(self, event):
        num = self.barre_bouton.numero()

        dlg = dlgpa.DialogueAfficherTirage(self, num)
        ret = dlg.Show()

    def afficher_partie_prec(self, event):
        if tournoi.tournoi() is None:
            self.barre_bouton.chg_partie()
        else:
            try:
                tournoi.tournoi().partie(self.barre_bouton.numero() - 1)
                self.barre_bouton.chg_partie(self.barre_bouton.numero() - 1)
            except expt.NumeroError, e:
                self.barre_etat.SetStatusText(unicode(e))

            # Rafraichir
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

    def afficher_partie_suiv(self, event):
        if tournoi.tournoi() is None:
            self.barre_bouton.chg_partie()
        else:
            try:
                tournoi.tournoi().partie(self.barre_bouton.numero() + 1)
                self.barre_bouton.chg_partie(self.barre_bouton.numero() + 1)
            except expt.NumeroError, e:
                self.barre_etat.SetStatusText(unicode(e))

            # Rafraichir
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

    def nouvelle_equipe(self, event):
        ret = wx.ID_OK

        def creer(info):
            equipe = tournoi.tournoi().ajout_equipe(info['numero'])
            for joueur in info['joueurs']:
                equipe.ajout_joueur(joueur[0], joueur[1], joueur[2])
            return equipe

        while ret == wx.ID_OK:
            dlg = dlgeq.DialogueEquipe(self, dlgeq.STYLE_AJOUTER, numero_affiche=tournoi.tournoi(
            ).nouveau_numero_equipe(), completion=self.config.get_typed('TOURNOI', 'joueur_completion'))
            ret = dlg.ShowModal()
            info = dlg.donnees()
            dlg.Destroy()

            if ret == wx.ID_OK:

                if tournoi.tournoi().nb_parties() == 0:
                    # Le tournoi n'est pas commencé
                    equipe = creer(info)

                    # Rafraichir
                    self.grille.ajout_equipe(equipe)
                    self.enregistrer_auto()
                    wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

                    self.info(u"Mini holà à l'équipe n°%s.\nHoooollaaaa...!!" % (equipe.numero))

                elif tournoi.tournoi().statut == cst.T_PARTIE_EN_COURS:
                    p = tournoi.tournoi().piquets()[-1] + 1
                    # Une partie est en cours: choix etat pour la partie en cours
                    dlg = dlgeq.DialogueMessageEquipe(self, info['numero'])
                    ret = dlg.ShowModal()
                    if ret == wx.ID_OK:
                        equipe = creer(info)
                        for partie in tournoi.tournoi().parties():
                            if partie != tournoi.tournoi().partie_courante():
                                # L'équipe est FORFAIT pour les autres parties.
                                partie.ajout_equipe(equipe, cst.FORFAIT, piquet=p)
                            else:
                                partie.ajout_equipe(equipe, dlg.etat(), dlg.creer_manche(), piquet=p)

                        # Rafraichir
                        self.grille.ajout_equipe(equipe)
                        self.enregistrer_auto()
                        wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

                        self.info(u"Un peu tard pour %s, mais ça passe..." % (equipe.numero))

                    dlg.Destroy()

                else:
                    p = tournoi.tournoi().piquets()[-1] + 1
                    # Les parties sont toutes terminées
                    texte = u"L'équipe sera considérée comme forfait pour toutes les parties déjà jouées,\
cliquez sur ANNULER si vous ne voulez pas ajouter cette nouvelle équipe."
                    dlg = wx.MessageDialog(self, texte, caption=u"Tournoi en cours",
                                           style=wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    ret = dlg.ShowModal()
                    dlg.Destroy()
                    if ret == wx.ID_OK:
                        equipe = creer(info)
                        for partie in tournoi.tournoi().parties():
                            partie.ajout_equipe(equipe, cst.FORFAIT, piquet=p)

                        # Rafraichir
                        self.grille.ajout_equipe(equipe)
                        self.enregistrer_auto()
                        wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

                        self.info(u"Un peu tard pour %s, mais ça passe..." % (equipe.numero))

    def modifier_equipe(self, event):
        num = self.grille.selection()

        dlg = dlgeq.DialogueEquipe(self, dlgeq.STYLE_MOFIFIER, choix=map(int, tournoi.tournoi().equipes(
        )), numero_affiche=num, completion=self.config.get_typed('TOURNOI', 'joueur_completion'))
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            info = dlg.donnees()
            equipe = tournoi.tournoi().equipe(info['numero'])
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

        dlg = dlgeq.DialogueEquipe(self, dlgeq.STYLE_SUPPRIMER, choix=map(
            int, tournoi.tournoi().equipes()), numero_affiche=num)
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            info = dlg.donnees()

            equipe = tournoi.tournoi().equipe(info['numero'])
            self.info(u"En ce jour exceptionel, l'équipe n°%s nous quitte." % (equipe.numero))

            # Rafraichir
            self.grille.suppr_equipe(equipe)
            tournoi.tournoi().suppr_equipe(equipe.numero)
            self.enregistrer_auto()
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

        dlg.Destroy()

    def nouvelle_partie(self, event):
        dlg = dlgpa.DialogueAjouterPartie(self, self.config)
        dlg.Bind(evt.EVT_PREFERENCES, self.preferences, id=wx.ID_PREFERENCES)
        ret = dlg.ShowModal()

        if ret == True:
            partie = tournoi.tournoi().ajout_partie()
            partie.demarrer(dlg.tirage(), dlg.chapeaux())

            # Rafraichir
            self.barre_bouton.chg_partie(partie.numero)
            self.enregistrer_auto()
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

            self.info(u"C'est Partie mon kiki!")

        dlg.Destroy()

    def supprimer_partie(self, event):
        num = self.barre_bouton.numero()

        dlg = dlgpa.DialogueSupprimerPartie(self, map(int, tournoi.tournoi().parties()), num)
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            tournoi.tournoi().suppr_partie(int(dlg.numero()))
            if tournoi.tournoi().nb_parties() == 0:
                self.barre_bouton.chg_partie(0)
            elif tournoi.tournoi().nb_parties() >= num:
                self.barre_bouton.chg_partie(num)
            else:
                self.barre_bouton.chg_partie(tournoi.tournoi().nb_parties())

            # Rafraichir
            self.enregistrer_auto()
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

            self.info(u"La partie n°%s, c'est ce qu'on appelle un 'coupourin'." % dlg.numero())

        dlg.Destroy()

    def entrer_resultats(self, event):
        num_partie = int(self.barre_bouton.numero())
        num_equipe = self.grille.selection()
        if num_equipe is None:
            num_equipe = 1
        else:
            num_equipe = int(num_equipe)
        etat = tournoi.tournoi().equipe(num_equipe).resultat(num_partie).etat

        if etat != cst.FORFAIT and etat != cst.CHAPEAU:
            dlg = dlgre.DialogueResultat(self, num_partie, num_equipe)
            ret = dlg.ShowModal()

            if ret == wx.ID_OK:
                d = dlg.donnees()
                if dlg.fin():
                    fin = datetime.now()
                else:
                    fin = None
                tournoi.tournoi().partie(num_partie).resultat(d, fin)

                # Rafraichir
                self.enregistrer_auto()
                wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'tout'))

                nb = len(tournoi.tournoi().partie_courante().equipes_incompletes())
                if nb != 0:
                    self.info(u"Manque encore %s équipes." % nb)
                else:
                    self.info(u"Prêt pour casser du billon.")

            dlg.Destroy()
        else:
            self.barre_etat.SetStatusText(u"Le score d'une équipe %s n'est pas modifiable." % etat)

    def classement(self, event):
        print "Non implémenté"

    def preferences(self, event):
        if type(event) == evt.PreferencesEvent:
            # Ouverture d'une page spécifique
            dlg = dlgpref.DialoguePreferences(self, self.config, event.page)
        else:
            # Page générale
            dlg = dlgpref.DialoguePreferences(self, self.config)

        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            for section in dlg.donnees():
                for nom, valeur in dlg.donnees()[section].items():
                    self.config.set(section, nom, unicode(valeur))

        dlg.Destroy()
        self.fenetre_affichage.configurer(self.config.get_options('AFFICHAGE', upper_keys=True))
        wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'affichage'))
        wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'fond'))
        return ret

    def a_propos_de(self, event):
        info = wx.AboutDialogInfo()
        info.Name = tourbillon.__nom__
        info.Version = "%s.%s.%s" % tourbillon.__version__
        info.Copyright = u"%s  Copyright © 2010  La Billonnière." % (tourbillon.__nom__)
        info.Description = wordwrap(
            u"TourBillon est un logiciel libre distribué sous licence GPL, aussi appelée "
            u"en français Licence Publique Générale GNU. Cette licence vous garantit les "
            u"libertés suivantes :\n"
            u"\n"
            u"    -  la liberté d’installer et d’utiliser TourBillon pour quelque usage "
            u"que ce soit ;\n"
            u"    -  la liberté d’étudier le fonctionnement de TourBillon et de l’adapter "
            u"à vos propres besoins en modifiant le code source, auquel vous avez "
            u"un accès immédiat;\n"
            u"    -  la liberté de distribuer des copies à qui que ce soit, tant que vous "
            u"n’altérez ni ne supprimez la licence ;\n"
            u"    -  la liberté d’améliorer TourBillon et de diffuser vos améliorations au "
            u"public, de façon à ce que l’ensemble de la communauté puisse en tirer "
            u"avantage, tant que vous n’altérez ni ne supprimez la licence.\n"
            u"\n"
            u"Il ne faut pas confondre logiciel libre et logiciel en domaine public. L’intérêt "
            u"de la licence GPL (licence du logiciel libre) est de garantir la non-confiscation "
            u"du logiciel, au contraire d’un logiciel du domaine public qui peut se voir "
            u"transformé en logiciel propriétaire. Vous bénéficiez des libertés ci-dessus "
            u"dans le respect de la licence GPL ; en particulier, si vous redistribuez ou si "
            u"vous modifiez TourBillon, vous ne pouvez cependant pas y appliquer une licence "
            u"qui contredirait la licence GPL (par exemple, qui ne donnerait plus le droit à "
            u"autrui de modifier le code source ou de redistribuer le code source modifié).", 800, wx.ClientDC(self))
        info.WebSite = ("https://www.facebook.com/labillonniere", "Billon home page")
        info.Developers = ["La Billonnière"]

        info.License = u"Retrouver la licence dans sa version complète sur http://www.gnu.org/licenses/gpl.html"

        wx.AboutBox(info)

#--- Application ---------------------------------------------------------------


class TourBillonGUI(wx.App):

    def __init__(self, config):
        self.config = config
        self.fenetre = None
        wx.App.__init__(self, False)

        self.SetAppName(tourbillon.__nom__)
        # This catches events when the app is asked to activate by some other
        # process
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

    def OnInit(self):
        """
        Afficher la fenetre splash et la fenêtre principale.
        """
        wx.InitAllImageHandlers()
        spl = FentetreSplash(None, wx.ID_ANY, 1000)

        self.fenetre = FenetrePrincipale(self.config)
        self.fenetre.Show()

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
        Appelé quand l'icone du DOC est cliquée.
        """
        self.BringWindowToFront()

    def MacOpenFile(self, fichier):
        """
        Appelé quand un fichier est déposé sur l'icon située dans le
        dock ou ouvert via le menu contextuel du Finder.
        """
        self.ouvrir(fichier)

    def ouvrir(self, fichier):
        tournoi.charger_tournoi(fichier)
        self.fenetre.barre_bouton.chg_partie(tournoi.tournoi().nb_parties())
        self.fenetre.grille.effacer()
        for equipe in tournoi.tournoi().equipes():
            self.fenetre.grille.ajout_equipe(equipe)
        wx.PostEvent(self.fenetre, evt.RafraichirEvent(self.fenetre.GetId()))
