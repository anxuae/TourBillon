# -*- coding: UTF-8 -*-

import sys

from tourbillon.core import tournoi
from tourbillon import logger


class TourBillonServer(object):

    def __init__(self, config):
        self.config = config

    def run(self):
        logger.critical("Pas inplementé: dev serveur HTTP RESTful")
        sys.exit(1)

    def ouvrir(self, fichier):
        tournoi.charger_tournoi(fichier)
