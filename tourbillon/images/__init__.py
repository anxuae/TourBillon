# -*- coding: UTF-8 -*-

import os
import glob
import imp
import codecs
import tourbillon
from tourbillon.core import constantes as cst
from tourbillon.cli.terminal import TERM
from tourbillon.images.splash import splash
try:
    import wx
except ImportError:
    # TourBillon est utilisé en mode console
    wx = None

IMAGES_REP = [os.path.dirname(os.path.abspath(__file__))]

# Trouver un eventuel fichier terminé par '_rc' qui indique d'autre
# répertoires contenant des ressources (images, texte...)
images_rc = None
d = os.path.splitdrive(os.path.dirname(os.path.abspath(__file__)))[1]
while d != os.path.sep and d != '':
    for fichier in glob.glob(os.path.join(d, '*_rc')):
        if os.path.isfile(fichier):
            images_rc = fichier
            break
    if images_rc is not None:
        break
    else:
        d = os.path.splitdrive(os.path.abspath(os.path.join(d, os.path.pardir)))[1]

if images_rc is not None:
    base = os.path.dirname(os.path.abspath(images_rc))
    f = open(images_rc, 'r')
    reps = f.readlines()
    f.close()
    for rep in reps:
        IMAGES_REP.append(os.path.join(base, rep.strip()))

# --- Entete (CLI ou Fichier texte)--------------------------------------------

ENTETE_AVEC_COULEURS = {'CADRE': TERM.RED,
                        'FOND': TERM.NORMAL,
                        'CHAPEAU': TERM.NORMAL + TERM.BLUE,
                        'PIQUET': TERM.NORMAL + TERM.BG_BLUE,
                        'BILLON': TERM.NORMAL + TERM.YELLOW,
                        'LB': TERM.BG_GREEN,
                        'TEXTE': TERM.BG_GREEN,
                        'NORMAL': TERM.NORMAL,
                        'VERSION': "%s.%s.%s" % tourbillon.__version__}

ENTETE_SANS_COULEURS = {}

for p in ENTETE_AVEC_COULEURS:
    if p != 'VERSION':
        ENTETE_SANS_COULEURS[p] = ''
    else:
        ENTETE_SANS_COULEURS[p] = ENTETE_AVEC_COULEURS[p]


def entete(terminal=False):
    """
    Retourne l'entête. Si terminal == True, l'entête sera formatée pour
    être affichée dans le terminal.
    """
    f = codecs.open(chemin('entete.txt'), 'r', 'utf-8')
    if not terminal:
        lignes = f.readlines()
        f.close()
        texte = "#" + "#".join(lignes)
        return unicode(texte).format(**ENTETE_SANS_COULEURS)
    else:
        texte = f.read()
        f.close()
        return unicode(texte).format(**ENTETE_AVEC_COULEURS)


# --- Images (GUI) ------------------------------------------------------------


def chemin(*nom):
    for chem in IMAGES_REP:
        c = os.path.normpath(os.path.join(chem, *nom))
        if os.path.exists(c):
            return c
    raise IOError("No such file or directory: '%s'" % c)


def scale_bitmap(bitmap, largeur, hauteur):
    if bitmap == wx.NullBitmap:
        return wx.NullBitmap
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(largeur, hauteur, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result


def bitmap(nom, force_alpha=False, scale=-1):
    if not nom:
        return wx.NullBitmap
    _, ext = os.path.splitext(nom)
    if ext in ['.png']:
        t = wx.BITMAP_TYPE_PNG
    elif ext in ['.jpg', '.jpeg']:
        t = wx.BITMAP_TYPE_JPEG
    else:
        t = wx.BITMAP_TYPE_ANY

    bp = wx.Bitmap(chemin(nom), t)
    if not bp.IsOk():
        # Le fichier n'est pas valide
        return wx.NullBitmap

    image = bp.ConvertToImage()
    if force_alpha:
        image.ConvertAlphaToMask(threshold=128)
    if scale > 0:
        largeur, hauteur = image.GetWidth(), image.GetHeight()
        image.Rescale(largeur * scale, hauteur * scale, wx.IMAGE_QUALITY_HIGH)
    return image.ConvertToBitmap()


def TourBillon_icon():
    icon = wx.EmptyIcon()
    icon.CopyFromBitmap(wx.Bitmap(chemin('icon.png'), wx.BITMAP_TYPE_ANY))
    return icon


# --- Styles (GUI) ------------------------------------------------------------


STYLES = {'texte': (255, 255, 255),
          'bordure': (24, 91, 26),
          'gradient1': (34, 68, 13),
          'gradient2': (173, 255, 45),
          'texte_bouton': (70, 143, 255),
          'separateur': (60, 11, 112),
          'selection': (222, 233, 98),
          'grille': (234, 232, 227),
          'grille_paire': (226, 244, 215),
          'grille_impaire': (255, 255, 255),
          'piquet': (200, 200, 200),
          cst.GAGNE: (0, 255, 0),
          cst.PERDU: (255, 0, 0),
          cst.CHAPEAU: (253, 183, 75),
          cst.FORFAIT: (0, 0, 0)}


def couleur(stl=None):
    if stl is None:
        return wx.NullColour

    return wx.Colour(*STYLES[stl])
