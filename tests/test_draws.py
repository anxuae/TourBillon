# -*- coding: UTF-8 -*-

import random
import datetime

import pytest

from tourbillon.core import cst
from tourbillon.core import draws


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


class NewTournament(object):

    scenarios = [('round2', {'draw_name': 'niveau2008_dt'}),
                 ('round3', {'draw_name': 'aleatoire_ag'}),
                 ('round4', {'draw_name': 'niveau_ag'}),
                 ('round5', {'draw_name': 'croissant'})]

    def test_nouveau_tirage(self, namespace, trb4e1j, cfg, draw_name):
        namespace.current_draw = draws.build(draw_name, trb4e1j.equipes_par_manche, trb4e1j.statistiques(), callback=trace)
        namespace.current_draw.gen.configurer(**cfg.get_options(draw_name))
        namespace.current_draw.gen.start(True)

    def test_coherence_tirage(self, namespace, trb4e1j, cfg, draw_name):
        opts = cfg.get_options(draw_name)
        assert not namespace.current_draw.chapeaux  # Nombre d'équipe pair
        for manche in namespace.current_draw.tirage:
            assert len(manche) == trb4e1j.equipes_par_manche
        if 'niveau' in draw_name:
            for manche in namespace.current_draw.tirage:
                assert sorted(manche) not in trb4e1j.manches()
                for combi2a2 in draws.utils.cnp(manche, 2):
                    vic0 = trb4e1j.equipe(combi2a2[0]).victoires()
                    vic1 = trb4e1j.equipe(combi2a2[1]).victoires()
                    assert abs(vic0 - vic1) <= opts['max_disparite']
        elif 'croissant' in draw_name:
            clmt = sorted(trb4e1j.equipes())
            for manche in namespace.current_draw.tirage:
                m = [eq.numero for eq in clmt[:trb4e1j.equipes_par_manche]]
                clmt = clmt[trb4e1j.equipes_par_manche:]
                assert manche == m

    def test_nouvelle_partie(self, namespace, trb4e1j):
        partie = trb4e1j.ajout_partie()

        assert trb4e1j.statut == cst.T_PARTIE_EN_COURS
        for equipe in trb4e1j.equipes():
            assert equipe.statut == cst.E_ATTEND_TIRAGE

        piquets = range(len(namespace.current_draw.tirage))
        partie.demarrer(dict(zip(piquets, namespace.current_draw.tirage)), namespace.current_draw.chapeaux)
        for equipe in trb4e1j.equipes():
            if equipe.resultat(partie.numero).etat in [cst.CHAPEAU, cst.FORFAIT]:
                assert equipe.statut == cst.E_ATTEND_TIRAGE
            else:
                assert equipe.statut == cst.E_EN_COURS
        assert partie.statut == cst.P_EN_COURS
        assert trb4e1j.statut == cst.T_PARTIE_EN_COURS

    def test_ajout_resultats(self, trb4e1j):
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
