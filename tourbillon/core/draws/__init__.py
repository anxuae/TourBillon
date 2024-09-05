# -*- coding: UTF-8 -*-

"""Draws collection"""

import os
import sys
import importlib.util

from ..exception import DrawError

HERE = os.path.dirname(os.path.abspath(__file__))
TIRAGES = {}

# Dynamic draw modules import
for filename in os.listdir(HERE):
    if filename.endswith('.py') and filename not in ('__init__.py', 'utils.py'):
        name = '.'.join((__name__, os.path.splitext(filename)[0]))
        spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, filename))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        TIRAGES[module.ThreadTirage.NOM] = module.ThreadTirage


def build(name: str, teams_by_match: int, all_rounds_data: dict, bye_teams: list = (), callback=None):
    """
    Create a new draw generator (Thread object). The draw is configured with its default
    parameters. The "configure" method of the generator allows them to be updated.

    :param name: name of the algorithm to use
    :param teams_by_match: number of teams in a match (i.e. nb opponents)
    :param all_rounds_data: data from all previous rounds
    :param bye_teams: list of teams to be set as BYE if necessary (let empty for automatic choice)
    :param callback: function to call after the end of the draw generation
    """
    if name not in TIRAGES:
        raise DrawError(f"Unknown draw name '{name}'")
    return TIRAGES[name](teams_by_match, all_rounds_data, bye_teams, callback)
