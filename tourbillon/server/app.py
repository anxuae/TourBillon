# -*- coding: UTF-8 -*-

from .. import logger
from ..core import tournament


class TourBillonServer:

    def __init__(self, config):
        self.config = config
        self.tournament = None

    def run(self):
        logger.critical("Pas inplementé: dev serveur backend (Flask RESTfull server)")

    def load(self, filename):
        self.tournament = tournament.load(filename)
