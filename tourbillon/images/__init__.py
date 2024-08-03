# -*- coding: UTF-8 -*-

import os
import glob
import codecs
import tourbillon
from tourbillon.core import constantes as cst
from tourbillon.images.splash import splash
try:
    import wx
except ImportError:
    # TourBillon est utilisé en mode server
    wx = None

IMAGES_PATHS = [os.path.dirname(os.path.abspath(__file__))]


def entete():
    """
    Return banner as ASCII Art.
    """
    with open(chemin('entete.txt'), encoding='utf-8') as fp:
        lignes = fp.readlines()
    texte = "#" + "#".join(lignes)
    return texte.format(version="%s.%s.%s" % tourbillon.__version__)


# --- Images (GUI) ------------------------------------------------------------


def chemin(*nom):
    for path in IMAGES_PATHS:
        path = os.path.normpath(os.path.join(path, *nom))
        if os.path.exists(path):
            return path
    raise IOError(f"No such file or directory: '{path}'")


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
    icon = wx.Icon()
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
