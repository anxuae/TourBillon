# -*- coding: UTF-8 -*-

import pytest
import random
import datetime

from tourbillon.core import constantes as cst
from tourbillon.core import tirages


def trace(prog, msg, tps):
    assert 0 <= prog <= 100
    print("%s%%: %s (reste %s)" % (prog, msg, tps))


@pytest.mark.parametrize('numero', [5, 4, 3, 1])
def test_inscription(trb4e1j, numero):
    """Suppression de 4 parties sur les 5 (on garde la 2eme voir si ça marche)"""
    trb4e1j.suppr_partie(numero)
    assert trb4e1j.statut == cst.T_ATTEND_TIRAGE
    assert trb4e1j.nb_equipes() == 92


class TestAjoutParie(object):

    scenarios = [('partie2', {'type_tirage': 'niveau2008_dt'}),
                 ('partie3', {'type_tirage': 'aleatoire_ag'}),
                 ('partie4', {'type_tirage': 'niveau_ag'}),
                 ('partie5', {'type_tirage': 'croissant'})]

    gen = None

    def test_nouveau_tirage(self, trb4e1j, cfg, type_tirage):
        TestAjoutParie.gen = tirages.creer_generateur(type_tirage, trb4e1j.equipes_par_manche, trb4e1j.statistiques(), callback=trace)
        TestAjoutParie.gen.configurer(**cfg.get_options(type_tirage))
        TestAjoutParie.gen.start(True)

    def test_coherence_tirage(self, trb4e1j, cfg, type_tirage):
        tir = TestAjoutParie.gen
        opts = cfg.get_options(type_tirage)
        assert not tir.chapeaux  # Nombre d'équipe pair
        for manche in tir.tirage:
            assert len(manche) == trb4e1j.equipes_par_manche
        if 'niveau' in type_tirage:
            for manche in tir.tirage:
                assert sorted(manche) not in trb4e1j.manches()
                for combi2a2 in tirages.utils.cnp(manche, 2):
                    vic0 = trb4e1j.equipe(combi2a2[0]).victoires()
                    vic1 = trb4e1j.equipe(combi2a2[1]).victoires()
                    assert abs(vic0 - vic1) <= opts['max_disparite']
        elif 'croissant' in type_tirage:
            clmt = sorted(trb4e1j.equipes())
            for manche in tir.tirage:
                m = [eq.numero for eq in clmt[:trb4e1j.equipes_par_manche]]
                clmt = clmt[trb4e1j.equipes_par_manche:]
                assert manche == m

    def test_nouvelle_partie(self, trb4e1j, type_tirage):
        tir = TestAjoutParie.gen
        partie = trb4e1j.ajout_partie()

        assert trb4e1j.statut == cst.T_PARTIE_EN_COURS
        for equipe in trb4e1j.equipes():
            assert equipe.statut == cst.E_ATTEND_TIRAGE

        piquets = range(len(tir.tirage))
        partie.demarrer(dict(zip(piquets, tir.tirage)), tir.chapeaux)
        for equipe in trb4e1j.equipes():
            if equipe.resultat(partie.numero).etat in [cst.CHAPEAU, cst.FORFAIT]:
                assert equipe.statut == cst.E_ATTEND_TIRAGE
            else:
                assert equipe.statut == cst.E_EN_COURS
        assert partie.statut == cst.P_EN_COURS
        assert trb4e1j.statut == cst.T_PARTIE_EN_COURS

    def test_ajout_resultats(self, trb4e1j, type_tirage):
        p = trb4e1j.partie_courante()
        for manche in p.manches():
            d = {}
            for eq in manche:
                if trb4e1j.points_par_manche not in d.values():
                    d[eq] = 7
                else:
                    d[eq] = random.randint(2, 9)
            p.resultat(d, datetime.datetime.now())

        for equipe in trb4e1j.equipes():
            assert equipe.statut == cst.E_ATTEND_TIRAGE
        assert p.statut == cst.P_COMPLETE
        assert trb4e1j.statut == cst.T_ATTEND_TIRAGE
