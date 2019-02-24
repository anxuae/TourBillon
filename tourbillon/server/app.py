# -*- coding: UTF-8 -*-

from tourbillon.core import tournoi
from tourbillon import logger


class TourBillonServer(object):

    def __init__(self, config):
        self.config = config

    def run(self):
        logger.critical("Pas inplementé: dev serveur backend (Flask RESTfull server)")

    def ouvrir(self, fichier):
        tournoi.charger_tournoi(fichier)
