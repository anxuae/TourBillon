# -*- coding: utf8 -*-
# Ce module correspond au module principal de TourBillon
# Il doit être placé dans le même dossier que TourBillon.py
#
#####################################################
__author__ = "La Billonnière"
__version__ = "Version : 4.0"
__date__ = "Date: 2008/03/09 21:57:19"
__copyright__ = "La Billonnière, 2008"
#####################################################

#####################################################
# Importation de Modules ou fonctions externes :
#####################################################

import os
import ConfigParser

#####################################################
# Définition locale de fonctions :
#####################################################


def estModif(val=''):
    """
    Retourner ou enregistrer si les données ont été modifiées
    """
    if val == '':
        return vg.estModif
    elif val == True:
        vg.estModif = True
        vg.fenetreIHM.barre.voyantModif.upDate()
    elif val == False:
        vg.estModif = False
        vg.fenetreIHM.barre.voyantModif.upDate()
    else:
        print u"Erreur estModif"

#####################################################
# Variables globales de TourBillon :
#####################################################


class vg(object):
    # Instanciation au demarrage de TourBillon
    cheminInstall = os.path.abspath('')
    config = ConfigParser.ConfigParser()          # Fichier de configuration
    if os.path.isfile(cheminInstall + '//TourBillon.cfg') == True:
        config.read(cheminInstall + '//TourBillon.cfg')
    fenetreIHM = ''          # Référence à l'ojet "wx.frame" de la fenêtre principale

    # A modifier à chaque nouvelle partie
    fichierActuel = ''          # Nom du fichier actuel
    nbrPart = 0           # Nombre de parties effectuées (dont tous les résultats ont étés entrés)
    heureEnregistrement = ''          # Heure du dernier enregistrement
    heureDebutTournoi = ''          # Heure debut
    heureFinTournoi = ''          # Heure fin
    estModif = False       # La variable est mise à 1 si une modification est faite depuis le dernier enregistrement
    listeEq = []          # Liste des équipes
    listeRenc = []          # Lste des rencontres
    arret = False       # Variable indiquant l'abandont de tous les calculs en cours
