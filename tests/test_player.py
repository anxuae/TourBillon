# -*- coding: UTF-8 -*-

from datetime import datetime
from tourbillon.core import player

DATE = datetime.now()


def test_create_player():
    p = player.Player("Toto", "LeRigolo", 12, DATE)

    assert p.prenom == "Toto"
    assert p.nom == "LeRigolo"
    assert p.age == 12


def test_change_player():
    p = player.Player("Tutu", "LeRigolo", 12, DATE)

    p.prenom = "Tata"
    assert p.prenom == "Tata"

    p.nom = "LeRigolo"
    assert p.nom == "LeRigolo"

    p.age = 20
    assert p.age == 20


def test_history(players_history):
    assert players_history.get("toto_lerigolo") == [["Toto", "LeRigolo", "12", DATE.strftime('%d/%m/%Y')]]


def test_duplicate_history_key(players_history):
    player.Player("Toto", "LéRigolo", 24, DATE)

    assert players_history.get("toto_lerigolo") == [
        ["Toto", "LeRigolo", "12", DATE.strftime('%d/%m/%Y')],
        ["Toto", "LéRigolo", "24", DATE.strftime('%d/%m/%Y')]
    ]
