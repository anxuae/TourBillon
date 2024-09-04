# -*- coding: UTF-8 -*-

import wx
import string
from wx.lib import scrolledpanel as scrolled
try:
    import wx.lib.platebtn as platebtn
except ImportError:
    import platebtn

from tourbillon.core import cst
from tourbillon.core import player
from tourbillon.core import tournament

from tourbillon.gui import evenements as evt


ID_PRENOM = wx.NewId()
ID_NOM = wx.NewId()
ID_NUMERO = wx.NewId()

STYLE_AJOUTER = "Ajouter"
STYLE_MOFIFIER = "Modifier"
STYLE_SUPPRIMER = "Supprimer"


class CompleterPopup(wx.PopupWindow):

    def __init__(self, parent, nombre_de_choix=5):
        wx.PopupWindow.__init__(self, parent, wx.SIMPLE_BORDER)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.nombre_de_choix = nombre_de_choix

        self.box = wx.BoxSizer(wx.VERTICAL)
        for _i in range(self.nombre_de_choix):
            btn = platebtn.PlateButton(self, wx.ID_ANY, '', style=platebtn.PB_STYLE_SQUARE | wx.BU_LEFT)
            btn.Bind(wx.EVT_BUTTON, self.selection)
            self.box.Add(btn, 1, wx.EXPAND)

        self.SetSizer(self.box)
        self.Layout()

    def proposer(self, position, choix, largeur=300):
        choix = choix[:self.nombre_de_choix]
        self.SetPosition(position)
        self.SetSize((largeur, 25 * len(choix)))
        for i in range(self.nombre_de_choix):
            btn = self.box.GetItem(i).GetWindow()
            if i < len(choix):
                btn.valeur = choix[i]
                btn.SetLabel(choix[i][0] + ' ' + choix[i][1])
                btn.Show()
            else:
                btn.valeur = []
                btn.SetLabel('')
                btn.Hide()
        self.Layout()
        self.Show()

    def selection(self, event):
        wx.PostEvent(self, evt.CompleterSelectionEvent(event.GetId(), event.GetEventObject().valeur))
        self.Hide()
        event.Skip()


class EntrerJoueur(wx.Panel):

    def __init__(self, parent, titres=True):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self._completion = True
        self._popup = None

        prenom, nom = "", ""
        if titres:
            prenom, nom = "  Prenom:", "  Nom   :"

        self.txt_prenom = wx.StaticText(self, wx.ID_ANY, prenom, size=(65, -1))
        self.ctl_prenom = wx.TextCtrl(self, ID_PRENOM, "")
        self.ctl_prenom._selection = ""

        self.txt_nom = wx.StaticText(self, wx.ID_ANY, nom, size=(65, -1))
        self.ctl_nom = wx.TextCtrl(self, ID_NOM, "")
        self.ctl_nom._selection = ""

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.txt_prenom, 0, wx.EXPAND)
        box.Add(self.ctl_prenom, 1, wx.EXPAND)
        box.Add(self.txt_nom, 0, wx.EXPAND)
        box.Add(self.ctl_nom, 1, wx.EXPAND)
        self.SetSizer(box)

        self.Layout()

        self.ctl_prenom.Bind(wx.EVT_TEXT, self.montrer_popup)
        self.ctl_nom.Bind(wx.EVT_TEXT, self.montrer_popup)
        self.Bind(wx.EVT_LEFT_DOWN, self.masquer_popup)

    def activer_completion(self, valeur=True):
        self._completion = valeur

    def montrer_popup(self, event):
        if self._completion:
            choix = player.PlayerHistory().complete(self.ctl_prenom.GetValue(), self.ctl_nom.GetValue())

            if not choix and self._popup:
                self._popup.Hide()
            else:
                if not self._popup:
                    self._popup = CompleterPopup(self.GetTopLevelParent(), 5)
                    self._popup.Bind(evt.EVT_COMPLETER_SELECTION, self.selectionner)

                position = (self.ctl_prenom.GetPosition().x, self.ctl_prenom.GetPosition().y + self.ctl_prenom.GetSize().y)
                largeur = self.ctl_prenom.GetSize().x + self.txt_nom.GetSize().x + self.ctl_nom.GetSize().x
                self._popup.proposer(self.ClientToScreen(position), choix, largeur)

                self.GetTopLevelParent().Raise()
                ctl = event.GetEventObject()
                ctl.SetFocus()
        event.Skip()

    def masquer_popup(self, event):
        if self._popup:
            self._popup.Hide()
        event.Skip()

    def selectionner(self, event):
        self.chg_joueur(event.selection[0], event.selection[1])
        event.Skip()

    def chg_joueur(self, prenom, nom):
        completion_active = self._completion
        self.activer_completion(False)
        self.ctl_prenom.SetValue(prenom)
        self.ctl_nom.SetValue(nom)
        self.ctl_prenom.SetSelection(len(self.ctl_prenom.GetValue()), len(self.ctl_prenom.GetValue()))
        self.ctl_nom.SetSelection(len(self.ctl_nom.GetValue()), len(self.ctl_nom.GetValue()))
        if completion_active:
            self.activer_completion(True)

    def chg_editable(self, valeur=True):
        self.ctl_prenom.SetEditable(valeur)
        self.ctl_nom.SetEditable(valeur)

    def complet(self):
        if self.ctl_prenom.GetValue() != "" and self.ctl_nom.GetValue() != "":
            return True
        else:
            return False

    def donnees(self):
        return (self.ctl_prenom.GetValue(), self.ctl_nom.GetValue())


class EquipeValidateur(wx.Validator):

    def __init__(self, pyVar=None):
        wx.Validator.__init__(self)
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

    def TransferToWindow(self):
        return True
 
    def TransfertFromWindow(self):
        return True


class EntrerNumero(wx.Panel):

    def __init__(self, parent, choix=[]):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.SetMinSize((-1, 40))

        if choix == []:
            self.ctl_numero = wx.TextCtrl(self, wx.ID_ANY, "", validator=EquipeValidateur())
            self.ctl_numero.SetMinSize((100, -1))
            self.combo = False
        else:
            self.ctl_numero = wx.Choice(self, ID_NUMERO, choices=[str(i) for i in choix])
            self.ctl_numero.SetMinSize((100, -1))
            self.combo = True

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(wx.StaticText(self, wx.ID_ANY, "Equipe n° "), 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
        box.Add(self.ctl_numero, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(box)
        self.Layout()

    def chg_numero(self, numero):
        if self.combo is True:
            self.ctl_numero.SetSelection(self.ctl_numero.FindString(str(numero)))
        else:
            self.ctl_numero.SetValue(str(numero))

    def complet(self):
        if self.combo is True:
            return True
        else:
            if self.ctl_numero.GetValue() != "":
                try:
                    tournament.tournoi().equipe(int(self.ctl_numero.GetValue()))
                    return False
                except:
                    return True
            else:
                return False

    def numero(self):
        if self.combo is True:
            return self.ctl_numero.GetString(self.ctl_numero.GetSelection())
        else:
            return self.ctl_numero.GetValue()


class DialogueEquipe(wx.Dialog):

    def __init__(self, parent, style=STYLE_AJOUTER, choix=[], numero_affiche=1, completion=True):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title=style + " une équipe", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.SetMinSize((500, 220))
        self.entrees = []
        self.choix = choix

        # Panel avec les entrées des joueurs
        self.panel = scrolled.ScrolledPanel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        box_panel = wx.BoxSizer(wx.VERTICAL)
        for _i in range(tournament.tournoi().joueurs_par_equipe):
            e = EntrerJoueur(self.panel)
            e.activer_completion(completion)
            self.entrees.append(e)
            box_panel.Add(e, 0, wx.EXPAND | wx.ALL, 15)
        self.panel.SetSizer(box_panel)
        self.panel.SetupScrolling()

        if style == STYLE_SUPPRIMER:
            for entree in self.entrees:
                entree.chg_editable(False)

        # Numero joker (utilisé pour départager les ex-aequo)
        self.spin_joker = wx.SpinCtrl(self, -1, "", (30, 30))
        self.spin_joker.SetForegroundColour(wx.Colour(0, 0, 200))
        self.spin_joker.SetRange(0, 1000)
        self.spin_joker.SetValue(0)
        self.spin_joker.SetMaxSize((50, -1))
        self.spin_joker.SetToolTip("Ce numéro 'Joker' est utilisé pour départager\n"
                                   "les équipes ex-aequo (laisser 0 si pas de departage).")

        # Boutons
        self.btn_gen = platebtn.PlateButton(self, wx.ID_ANY, "  Joker n° ")
        self.btn_gen.SetForegroundColour(wx.Colour(0, 0, 200))
        self.btn_gen.SetPressColor(wx.Colour(0, 0, 200))
        self.btn_ok = wx.Button(self, id=wx.ID_OK, label=style, size=(100, -1))
        self.btn_ok.SetDefault()
        self.btn_cancel = wx.Button(self, id=wx.ID_CANCEL, label="Annuler", size=(100, -1))
        box_btn = wx.StdDialogButtonSizer()
        box_btn.Add(self.btn_gen, 0, wx.WEST | wx.ALIGN_CENTER_VERTICAL, 15)
        box_btn.Add(self.spin_joker, 0, wx.WEST | wx.ALIGN_CENTER_VERTICAL)
        box_btn.Add((50, 50), 1, wx.EXPAND)
        box_btn.Add(self.btn_cancel, 0, wx.EAST | wx.ALIGN_CENTER_VERTICAL, 30)
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
        box.Add(box_btn, 0, wx.EXPAND)

        self.SetSizer(box)
        self.Layout()
        self.CenterOnParent()

        hauteur_necessaire = (self.entrees[0].GetSize()[1] + 30) * len(self.entrees) + 130
        if hauteur_necessaire < wx.GetDisplaySize()[1]:
            self.SetSize(wx.Size(500, hauteur_necessaire))
        else:
            self.SetSize(wx.Size(500, wx.GetDisplaySize()[1] - 10))

        self.Bind(wx.EVT_CHOICE, self._maj, id=ID_NUMERO)
        self.Bind(wx.EVT_TEXT, self._btn_satut)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self._masquer_popup)
        self.Bind(wx.EVT_LEFT_DOWN, self._masquer_popup)
        self.Bind(wx.EVT_BUTTON, self._generer_joker, self.btn_gen)

    def _maj(self, event):
        num = int(self.txt_numero.numero())
        equipe = tournament.tournoi().equipe(num)
        i = 0
        for joueur in equipe.joueurs():
            self.entrees[i].chg_joueur(joueur.prenom, joueur.nom)
            i += 1
        self.spin_joker.SetValue(equipe.joker)
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

    def _masquer_popup(self, event):
        for e in self.entrees:
            e.masquer_popup(event)
        event.Skip()

    def _generer_joker(self, event):
        num = tournament.tournoi().generer_numero_joker()
        self.spin_joker.SetValue(num)

    def donnees(self):
        d = {'numero': int(self.txt_numero.numero()), 'joker': self.spin_joker.GetValue() or 0, 'joueurs': []}
        for entree in self.entrees:
            d['joueurs'].append(entree.donnees())
        return d


class DialogueMessageEquipe(wx.Dialog):

    def __init__(self, parent, equipe):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title="Tournoi en cours", style=wx.DEFAULT_DIALOG_STYLE, pos=wx.DefaultPosition, size=wx.DefaultSize)
        self.SetMinSize((500, 220))
        self.SetSize(wx.Size(500, 200))

        texte = "La partie n° %s est en cours, pour toutes les parties précédentes l'équipe\n\
sera considérée comme forfait, choisissez l'état de l'équipe n° %s pour la\n\
partie en cours:" % (tournament.tournoi().partie_courante().numero, equipe)
        self.txt_info = wx.StaticText(self, wx.ID_ANY, texte, size=wx.Size(-1, 200))
        self.chx_etat = wx.Choice(self, ID_NUMERO, choices=[cst.FORFAIT, cst.CHAPEAU])
        self.chk_cree_manche = wx.CheckBox(self, wx.ID_ANY, "Créer une manche avec les équipes chapeaux si possible.")

        # Boutons
        self.btn_ok = wx.Button(self, id=wx.ID_OK, label="Valider", size=(100, -1))
        self.btn_ok.SetDefault()
        self.btn_cancel = wx.Button(self, id=wx.ID_CANCEL, label="Annuler", size=(100, -1))

        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        box_btn.Add((50, 50), 1, wx.EXPAND)
        box_btn.Add(self.btn_cancel, 0, wx.EAST | wx.ALIGN_CENTER_VERTICAL, 30)
        box_btn.Add(self.btn_ok, 0, wx.EAST | wx.ALIGN_CENTER_VERTICAL, 15)

        # Assembler
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.txt_info, 1, wx.ALL, 20)
        box.Add(self.chx_etat, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
        box.Add(self.chk_cree_manche, 1, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        box.Add(box_btn, 0, wx.EXPAND)

        self.SetSizer(box)
        self.Layout()
        self.CenterOnParent()

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
