#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#--- Import --------------------------------------------------------------------

import os
import tourbillon
from tourbillon.trb_core import constantes as cst
from tourbillon.trb_cli import terminal
from tourbillon.images.splash import splash
try:
    import wx
except ImportError, e:
    wx = None

#--- Variables globales --------------------------------------------------------

IMAGES_REP = os.path.dirname(os.path.abspath(__file__))

#--- Entete (CLI ou Fichier texte)----------------------------------------------

ENTETE_AVEC_COULEURS = {'CADRE':terminal.RED,
                        'FOND':terminal.NORMAL,
                        'CHAPEAU':terminal.NORMAL + terminal.BLUE,
                        'PIQUET':terminal.NORMAL + terminal.BG_BLUE,
                        'BILLON':terminal.NORMAL + terminal.YELLOW,
                        'LB':terminal.BG_GREEN ,
                        'TEXTE':terminal.BG_GREEN,
                        'NORMAL':terminal.NORMAL,
                        'VERSION':"%s.%s.%s" % tourbillon.__version__}

ENTETE_SANS_COULEURS = {}

for p in ENTETE_AVEC_COULEURS:
    if p != 'VERSION':
        ENTETE_SANS_COULEURS[p] = ''
    else:
        ENTETE_SANS_COULEURS[p] = ENTETE_AVEC_COULEURS[p]

def entete(terminal = False):
    """
    Retourne l'entête. Si terminal == True, l'entête sera formaté pour 
    être affichée dans le terminal.
    """
    f = open(os.path.join(IMAGES_REP, 'entete.txt'), 'r')
    if terminal == False:
        lignes = f.readlines()
        f.close()
        texte = u"#" + u"#".join(lignes)
        return texte % ENTETE_SANS_COULEURS
    else:
        texte = f.read()
        f.close()
        return texte % ENTETE_AVEC_COULEURS

#--- Images (GUI) --------------------------------------------------------------

def chemin(nom):
    return os.path.normpath(os.path.join(IMAGES_REP, nom))

def bitmap(nom, force_alpha = False):
    bp = wx.Bitmap(chemin(nom), wx.BITMAP_TYPE_PNG)
    if force_alpha:
        image = bp.ConvertToImage()
        image.ConvertAlphaToMask(threshold = 128)
        return image.ConvertToBitmap()
    else:
        return bp

def TourBillon_icon():
    icon = wx.EmptyIcon()
    icon.CopyFromBitmap(wx.Bitmap(chemin('icon.png'), wx.BITMAP_TYPE_ANY))
    return icon

#--- Styles (GUI) --------------------------------------------------------------

STYLES = {'texte':(255, 255, 255),
          'bordure':(24, 91, 26),
          'gradient1':(34, 68, 13),
          'gradient2':(173, 255, 45),
          'texte_bouton':(70, 143, 255),
          'separateur':(60, 11, 112),
          'selection':(222, 233, 98),
          'grille':(234, 234, 234),
          'grille_paire':(226, 244, 215),
          'grille_impaire':(255, 255, 255),
           cst.GAGNE:(0, 255, 0),
           cst.PERDU:(255, 0, 0),
           cst.CHAPEAU:(253, 183, 75),
           cst.FORFAIT:(0, 0, 0)}

def couleur(stl = None):
    if stl == None:
        return wx.NullColor

    return wx.Color(*STYLES[stl])
