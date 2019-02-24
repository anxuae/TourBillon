#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

from tourbillon.trb_test import t_equipe, t_tournoi, t_4eq_par_manche

TESTS = [t_equipe.TestEquipeVide,
         t_equipe.TestEquipeComplete,
         t_equipe.TestEquipePartie1,
         t_equipe.TestEquipePartie2,
         t_equipe.TestEquipePartie3,
         t_equipe.TestEquipePartie4,
         t_equipe.TestEquipePartie5,
         t_tournoi.TestCreationTournoi,
         t_tournoi.TestInscriptionTournoi,
         t_tournoi.TestEnregistrerTournoi,
         t_tournoi.TestChargerTournoi,
         t_4eq_par_manche.TestCreerTournoi,
         t_4eq_par_manche.TestAjoutParie1,
#         t_4eq_par_manche.TestAjoutParie2,
#         t_4eq_par_manche.TestAjoutParie3,
         t_tournoi.TestEnregistrerTournoi]


def suite():
    l = []
    for test in TESTS:
        l.append(unittest.TestLoader().loadTestsFromTestCase(test))
    return unittest.TestSuite(l)

unittest.TextTestRunner(verbosity=2).run(suite())
