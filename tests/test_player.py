# -*- coding: UTF-8 -*-

from datetime import datetime
from tourbillon.core import player

DATE = datetime.now()
PLAYER1 = ["Toto", "LeRigolo", "", DATE.strftime('%d/%m/%Y')]
PLAYER2 = ["Tata", "LeRigolo", "", DATE.strftime('%d/%m/%Y')]
PLAYER3 = ["Toto", "LéRigolo", "", DATE.strftime('%d/%m/%Y')]


def test_create_player():
    p = player.Player(PLAYER1[0], PLAYER1[1], DATE)
    assert p.prenom == PLAYER1[0]
    assert p.nom == PLAYER1[1]


def test_change_player():
    p = player.Player("Tutu", "LeRigolo", DATE)

    p.prenom = PLAYER2[0]
    assert p.prenom == PLAYER2[0]

    p.nom = PLAYER2[1]
    assert p.nom == PLAYER2[1]


def test_history_singleton(players_history):
    assert players_history == player.PlayerHistory()
    assert players_history.filename == player.PlayerHistory().filename


def test_history(players_history):
    assert players_history.get("toto_lerigolo") == [PLAYER1]
    assert players_history.get("tutu_lerigolo") == []


def test_duplicate_history_key(players_history):
    player.Player(PLAYER3[0], PLAYER3[1], DATE)
    assert players_history.get("toto_lerigolo") == [PLAYER1, PLAYER3]


def test_history_complete(players_history):
    assert players_history.complete("Tata", "LeRigolo") == [PLAYER2]
    assert players_history.complete("Ta", "LeRigolo") == [PLAYER2, PLAYER1, PLAYER3]
