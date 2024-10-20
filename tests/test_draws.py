# -*- coding: UTF-8 -*-

import pytest
import random
import datetime

from tourbillon.core import cst, draws

SENARIOS = [('partie2', {'type_tirage': 'level_dt'}),
            ('partie3', {'type_tirage': 'random_ag'}),
            ('partie4', {'type_tirage': 'level_ag'}),
            ('partie5', {'type_tirage': 'ascending'})]


def trace(prog, msg, tps):
    assert 0 <= prog <= 100
    print("%s%%: %s (reste %s)" % (prog, msg, tps))


@pytest.mark.order(1)
@pytest.mark.parametrize('numero', [5, 4, 3, 1])
def test_inscription(trb4e1j, numero):
    """Suppression de 4 parties sur les 5 (on garde la 2eme voir si ça marche)"""
    trb4e1j.suppr_partie(numero)
    assert trb4e1j.statut == cst.T_ATTEND_TIRAGE
    assert trb4e1j.nb_equipes() == 92


@pytest.mark.order(2)
def test_nouveau_tirage(namespace, trb4e1j, cfg, type_tirage):
    namespace.current_draw = draws.build(type_tirage, trb4e1j.equipes_par_manche, trb4e1j.statistiques(), callback=trace)
    namespace.current_draw.configurer(**cfg.get_options(type_tirage))
    namespace.current_draw.start(True)


@pytest.mark.order(3)
def test_coherence_tirage(namespace, trb4e1j, cfg, type_tirage):
    opts = cfg.get_options(type_tirage)
    assert not namespace.current_draw.chapeaux  # Nombre d'équipe pair
    for manche in namespace.current_draw.tirage:
        assert len(manche) == trb4e1j.equipes_par_manche
    if 'level' in type_tirage:
        for manche in namespace.current_draw.tirage:
            assert sorted(manche) not in trb4e1j.manches()
            for combi2a2 in draws.utils.cnp(manche, 2):
                vic0 = trb4e1j.equipe(combi2a2[0]).victoires()
                vic1 = trb4e1j.equipe(combi2a2[1]).victoires()
                assert abs(vic0 - vic1) <= opts['max_disparite']
    elif 'ascending' in type_tirage:
        clmt = sorted(trb4e1j.equipes())
        for manche in namespace.current_draw.tirage:
            m = [eq.numero for eq in clmt[:trb4e1j.equipes_par_manche]]
            clmt = clmt[trb4e1j.equipes_par_manche:]
            assert manche == m

@pytest.mark.order(4)
def test_nouvelle_partie(namespace, trb4e1j):
    partie = trb4e1j.ajout_partie()

    assert trb4e1j.statut == cst.T_PARTIE_EN_COURS
    for equipe in trb4e1j.equipes():
        assert equipe.statut == cst.E_ATTEND_TIRAGE

    piquets = range(len(namespace.current_draw.tirage))
    partie.start(dict(zip(piquets, namespace.current_draw.tirage)), namespace.current_draw.chapeaux)
    for equipe in trb4e1j.equipes():
        if equipe.resultat(partie.numero).etat in [cst.CHAPEAU, cst.FORFAIT]:
            assert equipe.statut == cst.E_ATTEND_TIRAGE
        else:
            assert equipe.statut == cst.E_EN_COURS
    assert partie.statut == cst.P_EN_COURS
    assert trb4e1j.statut == cst.T_PARTIE_EN_COURS

@pytest.mark.order(5)
def test_ajout_resultats(trb4e1j):
    p = trb4e1j.partie_courante()
    for manche in p.manches():
        d = {}
        for eq in manche:
            if trb4e1j.points_par_manche not in d.values():
                d[eq] = 7
            else:
                d[eq] = random.randint(2, 9)
        p.add_result(d, datetime.datetime.now())

    for equipe in trb4e1j.equipes():
        assert equipe.statut == cst.E_ATTEND_TIRAGE
    assert p.statut == cst.P_COMPLETE
    assert trb4e1j.statut == cst.T_ATTEND_TIRAGE
