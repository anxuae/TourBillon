# -*- coding: UTF-8 -*-

from tourbillon import logger
from tourbillon.core import tournament


class TourBillonServer:

    def __init__(self, config):
        self.config = config

    def run(self):
        logger.critical("Pas inplementé: dev serveur backend (Flask RESTfull server)")

    def load(self, fichier):
        tournament.charger_tournoi(fichier)
