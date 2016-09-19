#!/usr/bin/env python3
# Script that will return the needed content to run the game in single player
from cgitb import enable
enable()
from json import dumps
from cgi import FieldStorage
from os import environ
del environ['QUERY_STRING']
print('Content-Type: application/json; charset=utf-8')
print()
data = FieldStorage()
width = int(data.getfirst('width', '650'))
height = int(data.getfirst('height', '650'))
# Be sure to mark the local player
players = [
    {"x": width / 4, "y": height / 4, "colour": "blue", "userName": "Guest",
     "local": True},
    {"x": (3 * width) / 4, "y": height / 4, "colour": "red",
     "userName": "Bot-1", "local": False},
    {"x": width / 4, "y": (3 * height) / 4, "colour": "green",
     "userName": "Bot-2", "local": False},
    {"x": (3 * width) / 4, "y": (3 * height) / 4, "colour": "orange",
     "userName": "Bot-3", "local": False}
]
data = {"players": players, "ready": True}
print(dumps(data))
