# -*- coding: UTF-8 -*-

from tourbillon.core import cst

import data2e2j


def test_status(part3e2j, debut=None, manches=[], equipes=[], chapeaux=[],
                forfaits=[], incompletes=[], piquets=[]):
    assert part3e2j.numero == 1
    assert part3e2j.debut() == debut
    assert part3e2j.manches() == manches
    assert [eq.numero for eq in part3e2j.equipes()] == equipes
    assert [eq.numero for eq in part3e2j.chapeaux()] == chapeaux
    assert [eq.numero for eq in part3e2j.forfaits()] == forfaits
    assert [eq.numero for eq in part3e2j.equipes_incompletes()] == incompletes
    assert part3e2j.locations() == piquets


def test_demarrer(part3e2j):
    assert part3e2j.statut == cst.P_ATTEND_TIRAGE
    assert part3e2j.nb_equipes() == 0
    assert part3e2j.is_location_available(11) == True

    part3e2j.demarrer({11: [1, 2]})
    assert part3e2j.statut == cst.P_EN_COURS
    assert part3e2j.nb_equipes() == 2
    assert part3e2j.is_location_available(11) == False

    debut = part3e2j.equipes()[0].resultat(part3e2j.numero).debut
    test_status(part3e2j, debut, manches=[[1, 2]], equipes=[1, 2, 3],
                forfaits=[3], incompletes=[1, 2], piquets=[11])


def test_delete(part3e2j):
    part3e2j.delete()
    test_status(part3e2j)


def test_demarrer_avec_chapeau(part3e2j):
    part3e2j.demarrer({1: [3, 2]}, [1])
    assert part3e2j.statut == cst.P_EN_COURS
    assert part3e2j.nb_equipes() == 2
    assert part3e2j.is_location_available(11) == True

    debut = part3e2j.equipes()[0].resultat(part3e2j.numero).debut
    test_status(part3e2j, debut, manches=[[2, 3]], equipes=[1, 2, 3], chapeaux=[1],
                forfaits=[], incompletes=[2, 3], piquets=[1])


def test_resultat(part3e2j):
    part3e2j.add_result({3: 12, 2: 9})
    assert part3e2j.statut == cst.P_COMPLETE

    debut = part3e2j.equipes()[0].resultat(part3e2j.numero).debut
    test_status(part3e2j, debut, manches=[[2, 3]], equipes=[1, 2, 3], chapeaux=[1],
                forfaits=[], incompletes=[], piquets=[1])


def test_equipe_apres_demarrage(part3e2j):
    eq = part3e2j.tournoi.ajout_equipe(9)
    for joueur in data2e2j.JOUEURS_9:
        eq.ajout_joueur(*joueur)

    debut = part3e2j.equipes()[0].resultat(part3e2j.numero).debut
    test_status(part3e2j, debut, manches=[[2, 3]], equipes=[1, 2, 3], chapeaux=[1],
                forfaits=[], incompletes=[], piquets=[1])

    part3e2j.add_team(eq, cst.CHAPEAU)
    assert part3e2j.statut == cst.P_EN_COURS
    assert part3e2j.nb_equipes() == 4

    test_status(part3e2j, debut, manches=[[1, 9], [2, 3]], equipes=[1, 2, 3, 9], chapeaux=[],
                forfaits=[], incompletes=[1, 9], piquets=[1, 2])
