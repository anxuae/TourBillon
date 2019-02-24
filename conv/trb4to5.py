#!/usr/bin/env python
# -*- coding: utf8 -*-

#--- Import --------------------------------------------------------------------

import os
import sys
import datetime
from optparse import OptionParser, Option
import cPickle

from conv4to5 import GlobTrb
from conv4to5.EqTrb import Equipe
from conv4to5.ListeEqTrb import ListeEquipes
from conv4to5.RencTrb import Rencontre
from conv4to5.ListeRencTrb import ListeRencontres

import tourbillon
from tourbillon.trb_core import tournoi
from tourbillon.trb_core import constantes as cst

#--- Functions -----------------------------------------------------------------


def split_prenom_nom(chaine):
    l = chaine.strip().split(' ')
    if len(l) == 1:
        prenom = l[0]
        nom = ''
    else:
        nom = l[-1]
        l = l[:-1]
        prenom = " ".join(l)
    return prenom.strip(), nom.strip()


def extraire(chaine, fich):
    """
    Retourne la liste [chaine,data], 'data' étant la la donnée
    sérialisée dans le fichier 'fich' à la section 'chaine'
    """
    while 1:
        t = fich.readline()
        if t.strip() == chaine or t.strip() == "<<<<<<<<<<<<<FIN>>>>>>>>>>>":
            break

    data = cPickle.load(fich)         # Lecture de la donnée sérialisée
    return data


def charger(fichier):
    """
    Extraction des données
    """
    f = TextReader(fichier)

    date_enregistrement = extraire("<<<<DATE ENREGISTREMENT>>>>", f)
    date_debut = extraire("<<<<<<<<HEURE DEBUT>>>>>>>>", f)
    date_fin = extraire("<<<<<<<<<HEURE FIN>>>>>>>>>", f)
    nbr_parties = extraire("<<<<<NOMBRE DE PARTIES>>>>>", f)
    listeEq = extraire("<<<<<LISTE DES EQUIPES>>>>>", f)
    listeRenc = extraire("<<<<LISTE DES RENCONTRES>>>", f)

    f.close()

    # Creation d'un tournoi
    t = tournoi.nouveau_tournoi()

    # Dates
    t.date_enregistrement = date_enregistrement
    if date_debut == '':
        date_debut = date_enregistrement - datetime.timedelta(seconds=12600)  # durée théorique de 4 heures
    t.debut = date_debut

    # Création des équipes
    equipes = {}
    for equipe in listeEq.ListeEq:
        num = int(equipe.numeroEquipe())
        nouv_equipe = t.ajout_equipe(num)
        prenom, nom = split_prenom_nom(equipe.nomJoueur1())
        nouv_equipe.ajout_joueur(prenom, nom)
        prenom, nom = split_prenom_nom(equipe.nomJoueur2())
        nouv_equipe.ajout_joueur(prenom, nom)
        equipes[num] = []

    # Nombre de parties
    parties = []
    for rencontre in listeRenc.ListeRenc:
        num = int(rencontre.numeroPartie())
        if num not in parties:
            parties.append(num)
    parties.sort(reverse=False)
    nb_parties = len(parties)
    import GlobTrb
    GlobTrb.vg.nbrPart = nb_parties

    # statistiques par équipes
    for partie in parties:
        font_partie = []
        rencontres = listeRenc.rencontre(partie, ref='Renc')
        for rencontre in rencontres:
            eqA, eqB = rencontre.numeroEquipes()
            ptsA, ptsB = rencontre.pointsEquipes()
            etA, etB = rencontre.etatEquipes()
            if etA == u"G":
                etA = cst.GAGNE
            elif etA == u"P":
                etA = cst.PERDU
            elif etA == u"C":
                etA = cst.CHAPEAU

            if etB == u"G":
                etB = cst.GAGNE
            elif etB == u"P":
                etB = cst.PERDU
            elif etB == u"C":
                etB = cst.CHAPEAU

            if eqB is None:
                equipes[eqA].append({'points': 12, 'etat': cst.CHAPEAU,
                                     'debut': rencontre.debutRenc(), 'duree': None, 'adversaires': []})
                font_partie.append(eqA)
            else:
                equipes[eqA].append({'points': ptsA, 'etat': etA, 'debut': rencontre.debutRenc(),
                                     'duree': rencontre.dureeRenc(), 'adversaires': [eqB]})
                equipes[eqB].append({'points': ptsB, 'etat': etB, 'debut': rencontre.debutRenc(),
                                     'duree': rencontre.dureeRenc(), 'adversaires': [eqA]})
                font_partie.append(eqA)
                font_partie.append(eqB)

        # Ajout des forfaits
        for equipe in equipes:
            if equipe not in font_partie:
                equipes[equipe].append({'points': 0, 'etat': cst.FORFAIT,
                                        'debut': rencontre.debutRenc(), 'duree': None, 'adversaires': []})

    # Maj des nouvelles équipes
    for equipe in t.equipes():
        equipe._resultats = equipes[equipe.numero]

    return t

#--- Cross platform reader -----------------------------------------------------


class TextReader(object):

    def __init__(self, file):
        self.file = file
        self.fh = open(file, 'r')
        self.lineno = 0

    def readline(self):
        self.lineno = self.lineno + 1
        line = self.fh.readline()
        if not line:
            return None
        if line.endswith("\r\n"):
            line = line[:-2] + "\n"
        return line

    def read(self, size=None):
        return self.fh.read(size)

    def close(self):
        self.fh.close()


if __name__ == '__main__':
    info = """TourBillon fichier_v4 [options]

Ce module permet de convertir les fichiers de sauvegarde de TourBillon 4.x.x
en fichiers de sauvegarde compatibles 5.x.x."""

    Option.ALWAYS_TYPED_ACTIONS += ('callback',)  # Display metavar also for options with callback
    parser = OptionParser(usage=info, version="TourBillon v %s.%s.%s" % tourbillon.__version__)
    parser.formatter.max_help_position = 45
    parser.add_option("-f", "--fichier", metavar='<fichier>', dest="fichier", default=None, help=u"fichier de sortie")
    Option.ALWAYS_TYPED_ACTIONS = ('store', 'append')

    OPTIONS, ARGS = parser.parse_args()

    if len(ARGS) == 0:
        sys.exit("ERREUR - Un fichier de sauvegarde doit être donné en argument.")
    else:
        source = os.path.abspath(ARGS[0])
        nom = os.path.split(source)[1]
        nom = os.path.splitext(nom)[0] + u"_conv" + u".trb"

        if OPTIONS.fichier is not None:
            fichier = os.path.abspath(OPTIONS.fichier)
        else:
            fichier = os.path.abspath(nom)

        charger(source)
        print "Sauvegarde convertie: ", fichier
        tournoi.enregistrer_tournoi(fichier)
