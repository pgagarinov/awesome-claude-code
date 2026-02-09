"""Tests that guard app.py - the Stop hook runs these before Claude can finish."""

from app import add, greet


def test_greet_returns_hello():
    assert greet("World") == "Hi, World!"


def test_greet_with_empty_string():
    assert greet("") == "Hi, !"


def test_add_positive_numbers():
    assert add(2, 3) == 5


def test_add_negative_numbers():
    assert add(-1, -2) == -3
