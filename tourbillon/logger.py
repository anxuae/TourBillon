# -*- coding: utf-8 -*-

import sys
import time
import atexit
import logging
from pathlib import Path
from logging import handlers

import tourbillon

_logger = logging.getLogger(tourbillon.__long_name__)


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
        print("Execution summary: {errors} error(s), {warnings} warning(s), {infos} info(s)".format(
            **self.counters))
        print("*" * 80)


class CounterHandler(logging.Handler):
    """Silent handler that only tallies records into the shared counters.

    It never writes anything to a stream: it is meant to be attached to
    third-party loggers (e.g. uvicorn) so their records are included in the
    end-of-run summary without duplicating their console output.
    """

    def emit(self, record):
        if record.levelname == 'WARNING':
            LoggerHandler.counters['warnings'] += 1
        elif record.levelname in ('ERROR', 'CRITICAL'):
            LoggerHandler.counters['errors'] += 1
        elif record.levelname == 'INFO':
            LoggerHandler.counters['infos'] += 1
        elif record.levelname == 'DEBUG' and _logger.getEffectiveLevel() == logging.DEBUG:
            LoggerHandler.counters['infos'] += 1


def add_handler(handler, level: int = logging.INFO, pattern: str = "(%(levelname)s) %(asctime)s - %(message)s"):
    """
    Add a new handler with given config
    """
    handler.setLevel(level)
    formatter = logging.Formatter(pattern, "%Y/%m/%d %H:%M:%S")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return handler


def init_logger(level: int = logging.INFO, logdir: str = None):
    """
    Inititialize logging system and return logger object.

    :param level: verbosity level (DEBUG, INFO, ERROR, CRITICAL)
    :param logdir: path to the file where logs are saved
    """
    _logger.setLevel(logging.DEBUG)  # Let the possibility to have higher levels set on handlers

    console_handler = LoggerHandler()
    add_handler(console_handler, level)
    atexit.register(console_handler.bilan)

    # Include every other logger (third-party libraries, uvicorn / FastAPI, ...)
    # in the end-of-run summary without re-displaying their records: a silent
    # counter handler attached to the root logger tallies whatever propagates to
    # it. The tourbillon logger is excluded from propagation so its records are
    # not counted twice (they are already tallied by ``console_handler`` above).
    _logger.propagate = False
    counter_handler = CounterHandler()
    counter_handler.setLevel(level)
    logging.getLogger().addHandler(counter_handler)

    # Logger les messages dans un fichier
    if logdir:
        logdir = Path(logdir)
        logdir.mkdir(parents=True, exist_ok=True)
        log_filepath = str(logdir / ('%s.log' % time.strftime("%Y-%m-%d")))
        # Max taille de log 10Mo, 1000000 logs peuvent être créés avant de réécraser le premier
        file_handler = handlers.RotatingFileHandler(log_filepath, maxBytes=10000000, backupCount=1000000)
        add_handler(file_handler, logging.DEBUG, "(%(levelname)s),%(name)s,%(asctime)s,%(message)s,%(pathname)s,%(lineno)d")

    debug('Logger initialisé')
    return _logger


# Shortcut
CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG


def critical(msg):
    _logger.critical(msg, exc_info=sys.exc_info()[0] is not None)
    sys.exit(1)


def error(msg):
    _logger.error(msg, exc_info=sys.exc_info()[0] is not None)


warning = _logger.warning


info = _logger.info


debug = _logger.debug
