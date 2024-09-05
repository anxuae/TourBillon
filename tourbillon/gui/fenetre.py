# -*- coding: UTF-8 -*-

import os
from glob import glob
from datetime import datetime

import wx
from wx import grid
from wx.lib.agw import aui
from wx.py.shell import Shell
from wx.lib.wordwrap import wordwrap

import tourbillon
from tourbillon import images, logger
from tourbillon.config import system_config
from tourbillon.core import cst
from tourbillon.core import tournament

from tourbillon.gui import barres
from tourbillon.gui import evenements as evt
from tourbillon.gui import grille as grl
from tourbillon.gui import dlgequipe as dlgeq
from tourbillon.gui import dlgpartie as dlgpa
from tourbillon.gui import dlgresultat as dlgre
from tourbillon.gui import dlgimpression as dlgim
from tourbillon.gui import dlgpreferences as dlgpref
from tourbillon.gui import dlginformations as dlginfo

FILTRE_FICHIER = "Fichier YAML (*.yml)|*.yml|Fichier Tourbillon (*.trb)|*.trb"


class FenetrePrincipale(wx.Frame):

    def __init__(self, config):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=tourbillon.__nom__,
                          size=(640, 400), style=wx.DEFAULT_FRAME_STYLE)
        self.SetBackgroundColour(images.couleur('grille'))
        self.config = config

        # Création d'un gestionnaire de fenetres pour la gestion des fenêtres flottantes
        self._mgr = aui.AuiManager(self, aui.AUI_MGR_ALLOW_FLOATING | aui.AUI_MGR_TRANSPARENT_HINT |
                                   aui.AUI_MGR_TRANSPARENT_DRAG | aui.AUI_MGR_ALLOW_ACTIVE_PANE)

        # Fenêtre informations montrée
        self.fenetre_affichage = dlginfo.DialogueInformations(self, self.config)
        self.affichage_visible = False
        self.fenetre_affichage.Bind(wx.EVT_CLOSE, self.masquer_info)

        # Icon
        self.SetIcon(images.TourBillon_icon())

        # Créer la barre de menu
        self.barre_menu = barres.BarreMenu(self)
        self.SetMenuBar(self.barre_menu)

        # Créer la barre de statut
        self.barre_etat = barres.BarreEtat(self)
        self.SetStatusBar(self.barre_etat)

        # Créer la barre des boutons (pas la guerre)
        self.barre_bouton = barres.BarreBouton(self)
        self._mgr.AddPane(self.barre_bouton, aui.AuiPaneInfo().
                          Name("controles").Top().CaptionVisible(False).
                          MinSize(wx.Size(-1, 60)).DockFixed().Floatable(False))

        # Créer la grille
        if self.config.get_typed('INTERFACE', 'image'):
            chemin_image = glob(self.config.join_path('fond_perso*'))[0]
        else:
            chemin_image = ""
        self.grille = grl.GrillePanel(self, images.bitmap(chemin_image))
        self.barre_menu.FindItemById(barres.ID_STATISTIQUES).Check(
            self.config.get_typed('INTERFACE', 'afficher_statistiques'))
        self.afficher_statistiques(None)
        self._mgr.AddPane(self.grille, aui.AuiPaneInfo().Name("grille").CenterPane())

        # Creation d'un shell Python (utile pour le debug)
        self.shell = Shell(self, introText='',
                           locals={'intf': self, 'trb': tournament.tournoi(), 'cfg': self.config, 'cst': cst},
                           InterpClass=None,
                           startupScript=None,
                           execStartupScript=True)
        self.shell.SetSize((600, 200))
        self._mgr.AddPane(self.shell, aui.AuiPaneInfo().
                          Name('shell').Caption("Python Shell").
                          Bottom().CloseButton(True).MaximizeButton(True).Hide())
        self.barre_menu.FindItemById(barres.ID_SHELL).Check(self.config.get_typed('INTERFACE', 'afficher_shell'))
        self.afficher_shell(None)

        # Effectuer les connections sur les evenements

        # ... de la barre de menu
        self.Bind(wx.EVT_MENU, self.nouveau, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.ouvrir_demande, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.enregistrer, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.enregistrer_sous, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.apercu_avant_impression, id=wx.ID_PREVIEW_PRINT)
        self.Bind(wx.EVT_MENU, self.imprimer, id=wx.ID_PRINT)
        self.Bind(wx.EVT_MENU, self.quitter, id=wx.ID_EXIT)

        self.Bind(wx.EVT_MENU, self.afficher_statistiques, id=barres.ID_STATISTIQUES)
        self.Bind(wx.EVT_MENU, self.afficher_info, id=barres.ID_INFO)
        self.Bind(wx.EVT_MENU, self.afficher_tirage, id=barres.ID_TIRAGE)
        self.Bind(wx.EVT_MENU, self.afficher_shell, id=barres.ID_SHELL)

        self.Bind(wx.EVT_MENU, self.nouvelle_equipe, id=barres.ID_NOUVELLE_E)
        self.Bind(wx.EVT_MENU, self.modifier_equipe, id=barres.ID_MODIFIER_E)
        self.Bind(wx.EVT_MENU, self.supprimer_equipe, id=barres.ID_SUPPRIMER_E)
        self.Bind(wx.EVT_MENU, self.nouvelle_partie, id=barres.ID_NOUVELLE_P)
        self.Bind(wx.EVT_MENU, self.supprimer_partie, id=barres.ID_SUPPRIMER_P)
        self.Bind(wx.EVT_MENU, self.entrer_resultats, id=barres.ID_RESULTATS)
        self.Bind(wx.EVT_MENU, self.classement, id=barres.ID_CLASSEMENT)
        self.Bind(wx.EVT_MENU, self.preferences, id=wx.ID_PREFERENCES)

        self.Bind(wx.EVT_MENU, self.info_systeme, id=wx.ID_PROPERTIES)
        self.Bind(wx.EVT_MENU, self.a_propos_de, id=wx.ID_ABOUT)

        # ... de la barre de contrôle
        self.Bind(wx.EVT_BUTTON, self.afficher_partie_prec, self.barre_bouton.btn_precedente)
        self.Bind(wx.EVT_BUTTON, self.afficher_partie_suiv, self.barre_bouton.btn_suivante)

        self.Bind(wx.EVT_BUTTON, self.enregistrer, id=wx.ID_SAVE)
        self.Bind(wx.EVT_BUTTON, self.afficher_info, id=barres.ID_INFO)
        self.Bind(wx.EVT_BUTTON, self.afficher_tirage, id=barres.ID_TIRAGE)
        self.Bind(wx.EVT_BUTTON, self.nouvelle_equipe, id=barres.ID_NOUVELLE_E)
        self.Bind(wx.EVT_BUTTON, self.nouvelle_partie, id=barres.ID_NOUVELLE_P)
        self.Bind(wx.EVT_BUTTON, self.entrer_resultats, id=barres.ID_RESULTATS)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.grille.rechercher_suivant, id=wx.ID_FIND)
        self.Bind(wx.EVT_TEXT_ENTER, self.grille.rechercher_suivant, id=wx.ID_FIND)
        self.Bind(wx.EVT_TEXT, self.grille.rechercher, id=wx.ID_FIND)
        self.Bind(evt.EVT_MENU_RECHERCHE, self.grille.chg_recherche_colonne, self.barre_bouton)

        # ... des autres événements
        self.Bind(wx.EVT_CLOSE, self.quitter)
        self.Bind(aui.EVT_AUI_PANE_CLOSE, self.masquer_shell)
        self.Bind(evt.EVT_RAFRAICHIR, self.rafraichir)
        self.grille.Bind(grl.grid.EVT_GRID_CELL_LEFT_DCLICK, self.grille_double_click)
        self.grille.Bind(grl.grid.EVT_GRID_CELL_RIGHT_CLICK, self.grille_contexte)
        self.grille.Bind(wx.EVT_KEY_DOWN, self.grille_enter)

        # Rafraichir
        self._mgr.Update()
        self.Layout()
        wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

    def grille_enter(self, event):
        """
        Ouvre le fenêtre correspondant à l'activitée en cours
        pour l'équipe selectionnée si la touche [ENTER] et
        pressée (voir la fonction 'grille_double_click' pour
        plus de details).
        """
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.grille_double_click(event)
        else:
            event.Skip()

    def grille_double_click(self, event):
        """
        Ouvre le fenêtre correspondant à l'activitée en cours
        pour l'équipe selectionnée:
            - "Ajout de Joueur" si le tournoi n'est pas commencé
            - "Entrer les Résultats" si le tournoi est commencé
        """
        if tournament.tournoi() is not None:
            if self.grille.selection() is not None:
                statut = tournament.tournoi().statut
                if statut == cst.T_INSCRIPTION or (statut == cst.T_ATTEND_TIRAGE and tournament.tournoi().nb_parties() == 0):
                    self.modifier_equipe(event)
                else:
                    self.entrer_resultats(event)

    def grille_contexte(self, event):
        """
        Ouvre le menu contextuel
        """
        if tournament.tournoi() is not None:
            if self.grille.selection() is not None:
                menu = barres.cree_contexte_menu()
                self.PopupMenu(menu, wx.GetMousePosition() - self.GetPosition() -
                               (self.grille.GetPosition().x // 2, self.grille.GetPosition().y // 2))
                menu.Destroy()

    def rafraichir(self, event):
        """
        Appelle la methode 'rafraichir' de chaque widget qui a besoin de l'être.
        """
        t = tournament.tournoi()

        # Titre
        if tournament.FICHIER_TOURNOI is not None:
            self.SetTitle("%s - %s" % (tourbillon.__nom__, tournament.FICHIER_TOURNOI))
        else:
            self.SetTitle(tourbillon.__nom__)

        # Barre de menu
        if event.quoi == 'menu' or event.quoi == 'tout':
            if t is None:
                nom = ''
            else:
                nom = 'Tournoi  du %s' % t.debut.strftime('%d/%m/%Y')

            self.barre_menu._rafraichir()
            self.barre_bouton._rafraichir(nom)

        # Barre d'état
        if event.quoi == 'etat' or event.quoi == 'tout':
            if t is None:
                self.barre_etat._rafraichir('', 0, 0, 0, False)
            else:
                # Indication équipe incomplète
                nb_incompletes = 0
                num_partie = self.barre_bouton.numero()
                if self.barre_bouton.numero() > 0:
                    for equipe in tournament.tournoi().partie(num_partie).equipes():
                        if equipe.resultat(num_partie).etat is None:
                            nb_incompletes += 1
                self.barre_etat._rafraichir(t.debut.strftime('%Hh%M'), t.nb_parties(), t.nb_equipes(),
                                            nb_incompletes // tournament.tournoi().equipes_par_manche, t.changed)

        p = self.barre_bouton.numero()

        # Limite de raffraichissement
        limite = None
        if self.config.get_typed('INTERFACE', 'CUMULE_STATISTIQUES') == 1:
            limite = p

        # Equipes
        if event.quoi == 'tout':
            if tournament.tournoi() is None:
                self.grille._rafraichir()
            else:
                for equipe in tournament.tournoi().equipes():
                    self.grille._rafraichir(equipe=equipe, partie=p, partie_limite=limite)

        elif event.quoi.startswith('equipe'):
            num = int(event.quoi.split('_')[1])
            self.grille._rafraichir(equipe=tournament.tournoi().equipe(num), partie=p, partie_limite=limite)

        # Classement
        if event.quoi == 'classement' or event.quoi == 'tout':
            if tournament.tournoi() is not None:
                avec_victoires = self.config.get_typed('TOURNOI', 'CLASSEMENT_VICTOIRES')
                avec_joker = self.config.get_typed('TOURNOI', 'CLASSEMENT_JOKER')
                avec_duree = self.config.get_typed('TOURNOI', 'CLASSEMENT_DUREE')
                self.grille._rafraichir(classement=tournament.tournoi().classement(
                    avec_victoires, avec_joker, avec_duree, limite))
            else:
                self.grille._rafraichir(classement={})

        # Informations
        if t is not None:
            try:
                self.fenetre_affichage._rafraichir(t.statut)
            except wx._core.PyAssertionError:
                # HACK wxpython 3.0 sur Windows 8.1: wxTextMeasure::BeginMeasuring()
                # must not be used with non-native wxDCs
                # A resoudre, mais comment?????
                logger.info("Je ne peux pas rafraichir la fenêtre d'information aux joueurs (wxpython + Windows bug)")
        # fond
        if event.quoi == 'fond':
            if self.config.get_typed('INTERFACE', 'image'):
                chemin_image = glob(self.config.join_path('fond_perso*'))[0]
            else:
                chemin_image = ""
            self.grille.chg_fond(images.bitmap(chemin_image))

    def nouveau(self, event):
        ret = self.enregister_demande()

        if ret != wx.ID_CANCEL:
            if self.config.get_typed("INTERFACE", 'NOUVEAU_AFFICHE_PREFERENCES'):
                ret = self.preferences(evt.PreferencesEvent(self.GetId(), 1))
            else:
                ret = wx.ID_OK

            if ret == wx.ID_OK:
                self.shell.interp.locals['trb'] = tournament.nouveau_tournoi(self.config.get_typed("TOURNOI", "EQUIPES_PAR_MANCHE"),
                                                                             self.config.get_typed(
                    "TOURNOI", "POINTS_PAR_MANCHE"),
                    self.config.get_typed("TOURNOI", "JOUEURS_PAR_EQUIPE"))

                # Rafraichir
                self.grille.effacer()
                self.barre_bouton.chg_partie()
                wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

                logger.info("Il est %s, un nouveau tournoi commence..." % tournament.tournoi().debut.strftime('%Hh%M'))

    def ouvrir_demande(self, event):
        """
        Demander à l'utilisateur quel fichier il souhaite ouvrir.
        """
        ret = self.enregister_demande()

        if ret != wx.ID_CANCEL:
            if tournament.FICHIER_TOURNOI is not None:
                l = os.path.split(tournament.FICHIER_TOURNOI)
                d = l[0]
                f = l[1]
            else:
                d = self.config.get('INTERFACE', 'ENREGISTREMENT')
                f = ''

            dlg = wx.FileDialog(self, message="Ouvrir", defaultDir=d, defaultFile=f,
                                wildcard=FILTRE_FICHIER, style=wx.FD_OPEN)
            ret = dlg.ShowModal()

            if ret == wx.ID_OK:
                fichier = dlg.GetPath()
                self.ouvrir(fichier)
            dlg.Destroy()

    def ouvrir(self, fichier):
        self.shell.interp.locals['trb'] = tournament.charger_tournoi(fichier)

        # Rafraichir
        self.barre_bouton.chg_partie(tournament.tournoi().nb_parties())
        self.grille.effacer()
        self.grille.ajout_equipe(*tournament.tournoi().equipes())
        wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

        self.SetTitle("%s - %s" % (tourbillon.__nom__, fichier))
        logger.info("Chargé, prêt à jouer mon commandant!")

    def enregister_demande(self):
        """
        Demander à l'utilisateur s'il veux enregristrer le
        tournoi courrant.
        """
        continuer = wx.ID_OK
        if tournament.tournoi() is not None:
            if tournament.tournoi().changed:
                dlg = wx.MessageDialog(self, "Le tournoi en cours n'est pas enregistré, si vous cliquez sur NON, les données seront perdues.",
                                       caption="Voulez-vous enregistrer le tournoi en cours?", style=wx.CANCEL | wx.YES | wx.NO | wx.ICON_QUESTION)
                ret = dlg.ShowModal()
                dlg.Destroy()
                if ret == wx.ID_YES:
                    continuer = self.enregistrer_sous(None)
                elif ret == wx.ID_CANCEL:
                    continuer = wx.ID_CANCEL

        return continuer

    def enregistrer(self, event):
        if tournament.FICHIER_TOURNOI is None:
            self.enregistrer_sous(event)
        else:
            tournament.enregistrer_tournoi()

        # Rafraichir
        wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'etat'))

    def enregistrer_auto(self):
        if self.config.get_typed('INTERFACE', 'ENREGISTREMENT_AUTO') and tournament.FICHIER_TOURNOI is not None:
            self.enregistrer(None)

    def enregistrer_sous(self, event):
        if tournament.FICHIER_TOURNOI is not None:
            l = os.path.split(tournament.FICHIER_TOURNOI)
            d = l[0]
            f = l[1]
        else:
            d = self.config.get('INTERFACE', 'ENREGISTREMENT')
            f = "tournoi_billon_%s.yml" % datetime.now().strftime('%d/%m/%Y')
        dlg = wx.FileDialog(self, message="Enregistrer", defaultDir=d, defaultFile=f,
                            wildcard=FILTRE_FICHIER, style=wx.SAVE)
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            fichier = dlg.GetPath()
            _p, ext = os.path.splitext(fichier)
            if ext not in ['.trb', '.yml']:
                fichier += '.yml'
            tournament.enregistrer_tournoi(fichier)

            # Rafraichir
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'etat'))
            logger.info("C'est dans la boîte.")

        dlg.Destroy()
        return ret

    def apercu_avant_impression(self, event):
        avec_victoires = self.config.get_typed('TOURNOI', 'CLASSEMENT_VICTOIRES')
        avec_joker = self.config.get_typed('TOURNOI', 'CLASSEMENT_JOKER')
        avec_duree = self.config.get_typed('TOURNOI', 'CLASSEMENT_DUREE')
        dlg = dlgim.DialogueImprimer(self, tournament.tournoi().classement(avec_victoires, avec_joker, avec_duree))
        dlg.Preview()

    def imprimer(self, event):
        avec_victoires = self.config.get_typed('TOURNOI', 'CLASSEMENT_VICTOIRES')
        avec_joker = self.config.get_typed('TOURNOI', 'CLASSEMENT_JOKER')
        avec_duree = self.config.get_typed('TOURNOI', 'CLASSEMENT_DUREE')
        dlg = dlgim.DialogueImprimer(self, tournament.tournoi().classement(avec_victoires, avec_joker, avec_duree))
        dlg.Print()

    def quitter(self, event):
        ret = self.enregister_demande()

        if ret != wx.ID_CANCEL:
            # Enregistrer la géométrie de l'interface
            if self.IsMaximized():
                self.config.set('INTERFACE', 'MAXIMISER', 'True')
            else:
                self.config.set('INTERFACE', 'MAXIMISER', 'False')
                self.config.set('INTERFACE', 'GEOMETRIE', str(tuple(self.GetPosition()) + tuple(self.GetSize())))
            self.config.set('INTERFACE', 'afficher_statistiques', str(
                self.barre_menu.FindItemById(barres.ID_STATISTIQUES).IsChecked()))
            self.config.set('INTERFACE', 'afficher_shell', str(
                self.barre_menu.FindItemById(barres.ID_SHELL).IsChecked()))

            self.Destroy()

    def afficher_statistiques(self, event):
        """
        Affiche la grille des statistiques du
        tournoi en cours.
        """
        valeur = self.barre_menu.FindItemById(barres.ID_STATISTIQUES).IsChecked()
        self.grille.afficher_statistiques(valeur)

    def afficher_shell(self, event):
        """
        Affiche un shell Python qui donne accées à l'ensemble des variables
        du programme.
        """
        valeur = self.barre_menu.FindItemById(barres.ID_SHELL).IsChecked()
        self._mgr.GetPane('shell').Show(valeur)
        self._mgr.Update()

    def masquer_shell(self, event):
        """Masquer le shell (appelé lorsque l'utilisateur click sur le croix
        rouge de la fenêtre)
        """
        self.barre_menu.FindItemById(barres.ID_SHELL).Check(False)
        event.Skip()

    def afficher_info(self, event):
        """Afficher la fenêtre d'information joueurs.
        """
        self.affichage_visible = not self.affichage_visible

        if self.affichage_visible:
            self.barre_bouton.FindItemById(barres.ID_INFO).Check(self.affichage_visible)
            self.barre_menu.FindItemById(barres.ID_INFO).Check(self.affichage_visible)
            self.fenetre_affichage.Show()
            self.SetFocus()
        else:
            self.fenetre_affichage.Close()

    def masquer_info(self, event):
        """Masquer la fenêtre d'information joueurs (appelé lorsque l'utilisateur
        click sur le croix rouge de la fenêtre)
        """
        self.affichage_visible = False
        self.barre_bouton.FindItemById(barres.ID_INFO).Check(False)
        self.barre_menu.FindItemById(barres.ID_INFO).Check(False)
        event.Skip()

    def afficher_tirage(self, event):
        num = self.barre_bouton.numero()

        dlg = dlgpa.DialogueAfficherTirage(self, num)
        dlg.Show()

    def afficher_partie_prec(self, event):
        if tournament.tournoi() is None:
            self.barre_bouton.chg_partie()
        else:
            try:
                tournament.tournoi().partie(self.barre_bouton.numero() - 1)
                self.barre_bouton.chg_partie(self.barre_bouton.numero() - 1)
            except ValueError as ex:
                self.barre_etat.SetStatusText(str(e))

            # Rafraichir
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

    def afficher_partie_suiv(self, event):
        if tournament.tournoi() is None:
            self.barre_bouton.chg_partie()
        else:
            try:
                tournament.tournoi().partie(self.barre_bouton.numero() + 1)
                self.barre_bouton.chg_partie(self.barre_bouton.numero() + 1)
            except ValueError as ex:
                self.barre_etat.SetStatusText(str(e))

            # Rafraichir
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

    def nouvelle_equipe(self, event):
        ret = wx.ID_OK

        def creer(info):
            equipe = tournament.tournoi().ajout_equipe(info['numero'], info['joker'])
            for joueur in info['joueurs']:
                equipe.ajout_joueur(joueur[0], joueur[1], joueur[2])
            return equipe

        while ret == wx.ID_OK:
            dlg = dlgeq.DialogueEquipe(self, dlgeq.STYLE_AJOUTER,
                                       numero_affiche=tournament.tournoi().generer_numero_equipe(),
                                       completion=self.config.get_typed('TOURNOI', 'joueur_completion'))
            ret = dlg.ShowModal()
            info = dlg.donnees()
            dlg.Destroy()
            print(info)

            if ret == wx.ID_OK:

                if tournament.tournoi().nb_parties() == 0:
                    # Le tournoi n'est pas commencé
                    equipe = creer(info)

                    # Rafraichir
                    self.grille.ajout_equipe(equipe)
                    self.enregistrer_auto()
                    wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

                    logger.info("Mini holà à l'équipe n°%s.\nHoooollaaaa...!!" % (equipe.numero))

                elif tournament.tournoi().statut in [cst.T_PARTIE_EN_COURS]:
                    p = tournament.tournoi().locations()[-1] + 1
                    # Une partie est en cours: choix etat pour la partie en cours
                    dlg = dlgeq.DialogueMessageEquipe(self, info['numero'])
                    ret = dlg.ShowModal()
                    if ret == wx.ID_OK:
                        equipe = creer(info)
                        for partie in tournament.tournoi().parties():
                            if partie != tournament.tournoi().partie_courante():
                                # L'équipe est FORFAIT pour les autres parties.
                                partie.add_team(equipe, cst.FORFAIT, location=p)
                            else:
                                partie.add_team(equipe, dlg.etat(), dlg.creer_manche(), location=p)

                        # Rafraichir
                        self.grille.ajout_equipe(equipe)
                        self.enregistrer_auto()
                        wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

                        logger.info("Un peu tard pour %s, mais ça passe..." % (equipe.numero))

                    dlg.Destroy()

                else:
                    p = tournament.tournoi().locations()[-1] + 1
                    # Les parties sont toutes terminées
                    texte = "L'équipe sera considérée comme forfait pour toutes les parties déjà jouées,\
cliquez sur ANNULER si vous ne voulez pas ajouter cette nouvelle équipe."
                    dlg = wx.MessageDialog(self, texte, caption="Tournoi en cours",
                                           style=wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    ret = dlg.ShowModal()
                    dlg.Destroy()
                    if ret == wx.ID_OK:
                        equipe = creer(info)
                        for partie in tournament.tournoi().parties():
                            partie.add_team(equipe, cst.FORFAIT, location=p)

                        # Rafraichir
                        self.grille.ajout_equipe(equipe)
                        self.enregistrer_auto()
                        wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

                        logger.info("Un peu tard pour %s, mais ça passe..." % (equipe.numero))

    def modifier_equipe(self, event):
        num = self.grille.selection()
        dlg = dlgeq.DialogueEquipe(self, dlgeq.STYLE_MOFIFIER, choix=[int(e) for e in tournament.tournoi().equipes()],
                                   numero_affiche=num, completion=self.config.get_typed('TOURNOI', 'joueur_completion'))
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            info = dlg.donnees()
            equipe = tournament.tournoi().equipe(info['numero'])
            equipe.suppr_joueurs()
            for joueur in info['joueurs']:
                equipe.ajout_joueur(joueur[0], joueur[1], joueur[2])
            equipe.joker = info['joker']

            # Rafraichir
            self.enregistrer_auto()
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'etat'))
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'classement'))
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'equipe_' + str(equipe.numero)))

        dlg.Destroy()

    def supprimer_equipe(self, event):
        num = self.grille.selection()

        dlg = dlgeq.DialogueEquipe(self, dlgeq.STYLE_SUPPRIMER,
                                   choix=[int(i) for i in tournament.tournoi().equipes()],
                                   numero_affiche=num)
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            info = dlg.donnees()

            equipe = tournament.tournoi().equipe(info['numero'])
            logger.info("En ce jour exceptionel, l'équipe n°%s nous quitte." % (equipe.numero))

            # Rafraichir
            self.grille.suppr_equipe(equipe)
            tournament.tournoi().suppr_equipe(equipe.numero)
            self.enregistrer_auto()
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

        dlg.Destroy()

    def nouvelle_partie(self, event):
        dlg = dlgpa.DialogueAjouterPartie(self, self.config)
        dlg.Bind(evt.EVT_PREFERENCES, self.preferences, id=wx.ID_PREFERENCES)
        ret = dlg.ShowModal()

        if ret is True:
            partie = tournament.tournoi().ajout_partie()
            partie.demarrer(dlg.tirage(), dlg.chapeaux())

            # Rafraichir
            self.barre_bouton.chg_partie(partie.numero)
            self.enregistrer_auto()
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

            logger.info("C'est Partie mon kiki!")

        dlg.Destroy()

    def supprimer_partie(self, event):
        num = self.barre_bouton.numero()

        dlg = dlgpa.DialogueSupprimerPartie(self, [int(i) for i in tournament.tournoi().parties()], num)
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            tournament.tournoi().suppr_partie(int(dlg.numero()))
            if tournament.tournoi().nb_parties() == 0:
                self.barre_bouton.chg_partie(0)
            elif tournament.tournoi().nb_parties() >= num:
                self.barre_bouton.chg_partie(num)
            else:
                self.barre_bouton.chg_partie(tournament.tournoi().nb_parties())

            # Rafraichir
            self.enregistrer_auto()
            wx.PostEvent(self, evt.RafraichirEvent(self.GetId()))

            logger.info("La partie n°%s, c'est ce qu'on appelle un 'coupourin'." % dlg.numero())

        dlg.Destroy()

    def entrer_resultats(self, event):
        num_partie = int(self.barre_bouton.numero())
        num_equipe = self.grille.selection()
        if num_equipe is None:
            num_equipe = 1
        else:
            num_equipe = int(num_equipe)
        etat = tournament.tournoi().equipe(num_equipe).resultat(num_partie).etat

        if etat != cst.FORFAIT and etat != cst.CHAPEAU:
            dlg = dlgre.DialogueResultat(self, num_partie, num_equipe)
            ret = dlg.ShowModal()

            if ret == wx.ID_OK:
                d = dlg.donnees()
                if dlg.fin():
                    fin = datetime.now()
                else:
                    fin = None
                tournament.tournoi().partie(num_partie).add_result(d, fin)

                # Rafraichir
                self.enregistrer_auto()
                wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'tout'))

                nb = len(tournament.tournoi().partie_courante().equipes_incompletes())
                if nb != 0:
                    logger.info("Manque encore %s équipes." % nb)
                else:
                    logger.info("Prêt pour casser du billon.")

            dlg.Destroy()
        else:
            self.barre_etat.SetStatusText("Le score d'une équipe %s n'est pas modifiable." % etat)

    def classement(self, event):
        if not dlgpa.DialogueAfficherClassement.single:
            dlgpa.DialogueAfficherClassement(self)
            dlgpa.DialogueAfficherClassement.single.Show()
        dlgpa.DialogueAfficherClassement.single.Raise()

    def preferences(self, event):
        if isinstance(event, evt.PreferencesEvent):
            # Ouverture d'une page spécifique
            dlg = dlgpref.DialoguePreferences(self, self.config, event.page, event.sous_page)
        else:
            # Page générale
            dlg = dlgpref.DialoguePreferences(self, self.config)

        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            for section in dlg.donnees():
                for nom, valeur in dlg.donnees()[section].items():
                    self.config.set(section, nom, str(valeur))

        dlg.Destroy()
        self.fenetre_affichage.configurer(self.config.get_options('AFFICHAGE', upper_keys=True))
        wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'classement'))
        wx.PostEvent(self, evt.RafraichirEvent(self.GetId(), 'fond'))
        return ret

    def info_systeme(self, event):
        dlg = wx.Dialog(self, style=wx.DEFAULT_DIALOG_STYLE)
        dlg.CenterOnScreen()

        grille = grid.Grid(dlg, wx.ID_ANY)
        grille.CreateGrid(0, 2)
        grille.SetRowLabelSize(0)
        grille.SetDefaultCellBackgroundColour(images.couleur('grille'))
        grille.SetColLabelValue(0, "Elément")
        grille.SetColSize(0, dlg.GetSize()[0] // 2)
        grille.SetColLabelValue(1, "Valeur")
        grille.SetColSize(1, dlg.GetSize()[0] // 2)

        for a, b in system_config():
            grille.AppendRows(1)
            index = grille.GetNumberRows() - 1
            grille.SetCellValue(index, 0, " %s" % a)
            grille.SetCellValue(index, 1, b)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grille, 1)
        dlg.SetSizer(sizer)
        dlg.Layout()

        dlg.ShowModal()
        dlg.Destroy()

    def a_propos_de(self, event):
        info = wx.adv.AboutDialogInfo()
        info.Name = tourbillon.__nom__
        info.Version = "%s.%s.%s" % tourbillon.__version__
        info.Copyright = "%s  Copyright © 2010  La Billonnière." % (tourbillon.__nom__)
        info.Description = wordwrap(
            "TourBillon est un logiciel libre distribué sous licence GPL, aussi appelée "
            "en français Licence Publique Générale GNU. Cette licence vous garantit les "
            "libertés suivantes :\n"
            "\n"
            "    -  la liberté d’installer et d’utiliser TourBillon pour quelque usage "
            "que ce soit ;\n"
            "    -  la liberté d’étudier le fonctionnement de TourBillon et de l’adapter "
            "à vos propres besoins en modifiant le code source, auquel vous avez "
            "un accès immédiat;\n"
            "    -  la liberté de distribuer des copies à qui que ce soit, tant que vous "
            "n’altérez ni ne supprimez la licence ;\n"
            "    -  la liberté d’améliorer TourBillon et de diffuser vos améliorations au "
            "public, de façon à ce que l’ensemble de la communauté puisse en tirer "
            "avantage, tant que vous n’altérez ni ne supprimez la licence.", 800, wx.ClientDC(self))
        info.WebSite = ("https://www.facebook.com/labillonniere", "Billon home page")
        info.Developers = ["La Billonnière"]
        info.License = "Retrouver la licence dans sa version complète sur http://www.gnu.org/licenses/gpl.html"

        wx.adv.AboutBox(info, self)
