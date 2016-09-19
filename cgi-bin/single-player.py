#!/usr/bin/env python3
# Script that will return the needed content to run the game in single player
from json import dumps
print('Content-Type: application/json; charset=utf-8')
print()
# Be sure to mark the local player
players = [
    {"sector": 1, "colour": "blue", "userName": "Guest", "local": False},
    {"sector": 2, "colour": "red", "userName": "Bot-1", "local": True},
    {"sector": 3, "colour": "green", "userName": "Bot-2", "local": False},
    {"sector": 4, "colour": "orange", "userName": "Bot-3", "local": False}
]
data = {"players": players}
print(dumps(data))
