#!/usr/bin/env python3
from cgitb import enable
enable()
from os import environ
from http.cookies import SimpleCookie
from cgi import FieldStorage
from json import dumps, loads
from socket import *

# Get the version of this file that is required, and return the necessary
# json
form_data = FieldStorage()
start_up = form_data.getfirst('start_up', False)
# try:
cookie = SimpleCookie()
cookie.load(environ['HTTP_COOKIE'])
ip_address, port = cookie['game_address'].value.split(':')
port = int(port)

sock = socket(AF_INET, SOCK_STREAM)
sock.bind(('', 44446))
sock.connect((ip_address, port))

if start_up:
    # Send out the json for all the players with the local key
    # Once the game starts, prevent it from being joined
    # Get players from server
    player_num = int(cookie['player_num'].value)
    msg = "start_up=" + str(player_num)
    sock.sendall(msg.encode())
    # Receive the players and print it out back to the ajax
    response = sock.recv(4096).decode()
else:
    player = form_data.getfirst('player')
    if player:
        msg = "update=" + dumps(loads(player))
        sock.sendall(msg.encode())
        # Receive the players from the server
        response = sock.recv(4096).decode()
# else:
#     # Update the player that is sent and send back all players
#     # Receive player data in two pieces
#     # The id is now in the JSON object so we no longer need the cookie
#     # This will be handled by the third loop in the server
#     player = form_data.getfirst('player')
#     if player:
#         player = loads(player)
#         players = gamefile['players']
#         players[player['id']] = player
#         gamefile['players'] = players
#         data = {'players': players}


# except Exception as e:
#     data = {'error': e}
sock.close()
print('Content-Type: application/json; charset=utf-8')
print()
print(response)
