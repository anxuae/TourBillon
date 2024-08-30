# -*- coding: utf-8 -*-

import sys
import os
import os.path as osp
import time
import atexit
import traceback
import logging
from logging import handlers
import tourbillon

_logger = logging.getLogger(tourbillon.__nom__)


class LoggerHandler(logging.StreamHandler):

    counters = {'errors': 0, 'warnings': 0, 'infos': 0}

    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        if record.levelname == 'WARNING':
            self.counters['warnings'] += 1
            self.stream = sys.stderr
        elif record.levelname == 'ERROR' or record.levelname == 'CRITICAL':
            self.counters['errors'] += 1
            self.stream = sys.stderr
        elif record.levelname == 'INFO':
            self.counters['infos'] += 1
            self.stream = sys.stdout
        elif record.levelname == 'DEBUG' and _logger.getEffectiveLevel() == logging.DEBUG:
            self.counters['infos'] += 1
            self.stream = sys.stdout

        self.format(record)
        logging.StreamHandler.emit(self, record)

    def bilan(self):
        print("*" * 80)
        print("Résumé de l'éxécution: {errors} error(s), {warnings} warning(s), {infos} info(s)".format(**self.counters))
        print("*" * 80)


def ajouter_handler(handler, level=logging.INFO, pattern="(%(levelname)s) %(asctime)s - %(message)s"):
    """
    Ajouter un manipulateur de log
    """
    handler.setLevel(level)
    formatter = logging.Formatter(pattern, "%Y/%m/%d %H:%M:%S")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return handler


def init_logger(level=logging.INFO, logdir=None):
    """
    Initialiser le système de logging et retourner le handler.

    :param level: niveau de verbosité defini par le module logging (DEBUG, INFO, ...)
    :type level: int

    :param logdir: chemin du dossier ou les messages sont enregistrés
    :type logdir: str
    """
    _logger.setLevel(logging.DEBUG)  # Pour laisser la possibilité d'avoir des niveau différents

    console_handler = LoggerHandler()
    ajouter_handler(console_handler, level)
    atexit.register(console_handler.bilan)

    # Logger les messages dans un fichier
    if logdir:
        if not osp.isdir(logdir):
            os.makedirs(logdir)
        log_filepath = osp.join(logdir, '%s.log' % time.strftime("%Y-%m-%d"))
        # Max taille de log 10Mo, 1000000 logs peuvent être créés avant de réécraser le premier
        file_handler = handlers.RotatingFileHandler(log_filepath, maxBytes=10000000, backupCount=1000000)
        ajouter_handler(file_handler, logging.DEBUG, "(%(levelname)s),%(name)s,%(asctime)s,%(message)s,%(pathname)s,%(lineno)d")

    debug('Logger initialisé')
    return _logger


# Raccourcis
CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG


def critical(msg):
    tb = traceback.format_exc()
    if tb:
        _logger.critical("%s:\n%s", msg, tb)
    else:
        _logger.critical(msg)
    sys.exit(1)


def error(msg):
    tb = traceback.format_exc()
    if tb:
        _logger.error("%s:\n%s", msg, tb)
    else:
        _logger.error(msg)


warning = _logger.warning


info = _logger.info


debug = _logger.debug
