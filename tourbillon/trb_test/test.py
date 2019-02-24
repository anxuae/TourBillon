#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

from tourbillon.trb_test import t_equipe
from tourbillon.trb_test import t_tournoi

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
         t_tournoi.TestChargerTournoi]


def suite():
    l = []
    for test in TESTS:
        l.append(unittest.TestLoader().loadTestsFromTestCase(test))
    return unittest.TestSuite(l)

unittest.TextTestRunner(verbosity = 2).run(suite())
