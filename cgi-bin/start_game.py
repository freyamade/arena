#!/usr/bin/env python3
from cgitb import enable
enable()
from http.cookies import SimpleCookie
from os import environ
from socket import *
from json import dumps, loads

try:
    cookie = SimpleCookie()
    cookie.load(environ['HTTP_COOKIE'])
    player_num = cookie.get('player_num').value
    ip_address, port = cookie.get('game_address').value.split(':')

    # Create the socket
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(('', 44446))
    sock.connect((ip_address, int(port)))
    msg = 'start=' + str(player_num)
    sock.sendall(msg.encode()) # Game will only start if the host clicks button
    response = loads(sock.recv(4096).decode())
    print('Content-Type: application/json')
    print()
    print(dumps(response))
    sock.close()
except Exception as e:
    print('Content-Type: text/plain')
    print()
    print(e)
