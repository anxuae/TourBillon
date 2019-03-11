# -*- coding: utf8 -*-
# Ce module correspond au module principal de TourBillon
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

import re
import datetime

#####################################################
# Definition exceptions :
#####################################################


class TransfoDateError(Exception):
    pass


class InvalidDatetime(TransfoDateError):
    pass


class InvalidTimedelta(TransfoDateError):
    pass


class InvalidChain(TransfoDateError):
    pass

#####################################################
# Corps principal du module 'TransfoDateTrb.py' :
#####################################################

mois = {1: "Janvier",
        2: "Février",
        3: "Mars",
        4: "Avril",
        5: "Mai",
        6: "Juin",
        7: "Juillet",
        8: "Août",
        9: "Septembre",
        10: "Octobre",
        11: "Novembre",
        12: "Décembre", }


# Définition de l'expression régulière pour découper une date (chaine) du format iso
motifDateIso = re.compile(r"""
    ^           # Debut de la chaine,
    (\d{4})     # rechercher 4 chiffres exactement = la date,
    \D*         # recherche d'un eventuel séparateur (tout caractère autre qu'un chiffre),
    (\d{2})     # rechercher 2 chiffres exactement = le mois,
    \D*         # recherche d'un eventuel séparateur,
    (\d{2})     # rechercher 2 chiffres exactement = le jour,
    \D*         # recherche d'un eventuel séparateur,
    (\d{2})     # rechercher 2 chiffres exactement = les heures,
    \D*         # recherche d'un eventuel séparateur,
    (\d{2})     # rechercher 2 chiffres exactement = les minutes,
    \D*         # recherche d'un eventuel séparateur,
    (\d{2})     # rechercher 2 chiffres exactement = les secondes,
    \D*         # recherche d'un eventuel séparateur,
    (\d*)       # rechercher d'un nombre de chiffres indéfinis et opptionnels = les microsecondes,
    $           # fin de la chaine
    """, re.VERBOSE)


# Définition de l'expression régulière pour découper une différence (chaine) du format iso
motifDiffIso = re.compile(r"""
    ^           # Debut de la chaine,
    (\d{0,9})   # rechercher de 0 à 9 chiffres  = nombre de jours,
    \D*         # recherche d'un eventuel séparateur (tout caractère autre qu'un chiffre),
    (\d{0,2})   # rechercher de 0 à 2 chiffres = nombre d'heures,
    \D*         # recherche d'un eventuel séparateur,
    (\d{0,2})   # rechercher de 0 à 2 chiffres  = nombre de minutes,
    \D*         # recherche d'un eventuel séparateur,
    (\d{2})     # rechercher 2 chiffres exactement = nombre de secondes,
    \D*         # recherche d'un eventuel séparateur,
    (\d*)       # rechercher d'un nombre de chiffres indéfinis et opptionnels = nombre de microsecondes,
    $           # fin de la chaine
    """, re.VERBOSE)


def datetimeENchaine(date, formSortie='iso', com=True):
    """
    Retourne la date du systeme sous forme d'une chaine
    Si formSortie='iso' date selon la norme iso
    Si formSortie='Dfr' date langue française
    Si formSortie='Hfr' heure langue française
    """
    if type(date) != datetime.datetime:
        raise InvalidDatetime("'%s' => Cette date n'est pas un objet datetime" % date)

    if formSortie == 'iso':               # Retour la date au format ISO
        return date.isoformat(' ')

    elif formSortie == 'Dfr':             # Retourne jour mois ann�e
        return "%s %s %s" % (date.day, mois[date.month], date.year)

    elif formSortie == 'Hfr':             # Retourne heure minute seconde microseconde

        if com == False:
            if date.hour == 0:
                heure = ''
            else:
                heure = str(date.hour) + "hr"
            if date.minute == 0 and date.hour == 0:
                minute = ''
            else:
                minute = str(date.minute) + "min"
            seconde = str(date.second) + "sec"
            if date.microsecond == 0:
                microsec = ''
            else:
                microsec = date.microsecond * 10 ** (-5)
                microsec = str(microsec) + "'"

            return "%s %s %s %s" % (heure, minute, seconde, microsec)

        elif com == True:                   # Format compact
            heure = str(date.hour)
            if len(heure) == 1:
                heure = '0' + heure
            minute = str(date.minute)
            if len(minute) == 1:
                minute = '0' + minute
            seconde = str(date.second)
            if len(seconde) == 1:
                seconde = '0' + seconde

            return "%s:%s:%s" % (heure, minute, seconde)


def chaineENdatetime(date):
    """
    Retourne la date du systeme sous forme d'un objet date time
    L'argument entré doit être une chaine exprimant une date sous forme iso
    """
    if type(date) != bytes:
        raise InvalidChain("'%s' => Cette date n'est pas une chaine de caractères" % date)

    def ENint(chn):
        if chn == '':
            return 0
        else:
            return int(chn)

    grp = motifDateIso.search(date).groups()  # Cr�ation d'un tuple en utilisant les expressions r�guli�res

    elsa = datetime.datetime(year=ENint(grp[0]), month=ENint(grp[1]), day=ENint(grp[2]),
                             hour=ENint(grp[3]), minute=ENint(grp[4]), second=ENint(grp[5]), microsecond=ENint(grp[6]))
    return elsa


def timedeltaENchaine(temps, formSortie='iso', jrs=True, hrs=True, mins=True, secs=True, msecs=True, ind=None):
    """
    Retourne une différence sous forme d'une chaine
    Si form='iso' différence selon la norme iso : jour/secondes/microsecondes
    Si form='fr' différence langue française : jr hr min sec microsec
        Affecter arg='' pour ne pas afficher la valeur 'arg' dans la chaine
    """
    if type(temps) != datetime.timedelta and temps != None:
        raise InvalidTimedelta("'%s' => Ce temps n'est pas un objet timedelta" % temps)

    if temps == None:
        return ''

    jours = str(temps.days)                              #
    heures = int(temps.seconds / 3600.)                    # Partie entière de (total secondes/3600)
    secondes = str((temps.seconds - 3600 * heures) % 60)       # Reste de la division euclidienne par 60
    minutes = str(int((temps.seconds - (3600 * heures)) / 60.))
    heures = str(heures)                                 #
    microsecondes = temps.microseconds                   #

    zeroSupm = ''
    lala = [e for e in minutes if 1 == 1]
    if len(lala) == 1:
        zeroSupm = '0'
    zeroSups = ''
    lala = [e for e in secondes if 1 == 1]
    if len(lala) == 1:
        zeroSups = '0'

    if formSortie == 'iso':
        return "%s days, %s:%s:%s.%s" % (jours, heures, zeroSupm + minutes, zeroSups + secondes, str(microsecondes))

    elif formSortie == 'fr':
        chaine = ""
        if jours != '0' and jrs == True:
            chaine = chaine + jours + " jr" + " "
        if heures != '0' and hrs == True:
            chaine = chaine + heures + " hr" + " "
        if minutes != '0' and mins == True:
            chaine = chaine + minutes + " min" + " "
        if secondes != '0' and secs == True:
            chaine = chaine + secondes + " sec" + " "
        if microsecondes != '0' and msecs == True:
            microsecondes = str(microsecondes * 10 ** (-5))
            chaine = chaine + microsecondes + "'"

        if chaine == "":
            if secs == True:
                chaine = "0 sec"
            elif mins == True:
                chaine = "0 min"
            elif hrs == True:
                chaine = "0 hr"
            elif jrs == True:
                chaine = "0 jr"

        return chaine


def chaineENtimedelta(temps):
    """
    Retourne une différence sous forme d'un objet timedelta
    L'argument entré doit être une chaine exprimant une différence sous forme iso
    """
    if type(temps) != bytes:
        raise InvalidChain("'%s' => Ce temps n'est pas une chaine de caractères" % temps)

    def ENint(chn):
        if chn == '':
            return 0
        else:
            return int(chn)

    grp = motifDiffIso.search(temps).groups()    # Création d'un tuple en utilisant les expressions régulières
    elsa = datetime.timedelta(ENint(grp[0]), ENint(grp[1]) * 3600 + ENint(grp[2]) * 60 + ENint(grp[3]), ENint(grp[4]))
    return elsa
