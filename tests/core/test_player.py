# -*- coding: UTF-8 -*-

from tourbillon.core import player

PLAYER1 = ["Toto", "LeRigolo"]
PLAYER2 = ["Tata", "LeRigolo"]
PLAYER3 = ["Toto", "LéRigolo"]


def test_create_player():
    p = player.Player(PLAYER1[0], PLAYER1[1])
    assert p.firstname == PLAYER1[0]
    assert p.lastname == PLAYER1[1]


def test_change_player():
    p = player.Player("Tutu", "LeRigolo")

    p.firstname = PLAYER2[0]
    assert p.firstname == PLAYER2[0]

    p.lastname = PLAYER2[1]
    assert p.lastname == PLAYER2[1]


def test_make_key_is_normalized():
    # Accents and case are stripped when building the comparison key.
    assert player.make_key(*PLAYER3) == player.make_key(*PLAYER1)


def test_player_equality_uses_key():
    p1 = player.Player(*PLAYER1)
    p3 = player.Player(*PLAYER3)
    assert p1 == p3
    assert p1 != player.Player(*PLAYER2)
