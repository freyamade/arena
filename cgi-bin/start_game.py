#!/usr/bin/env python3
from cgitb import enable
enable()
from http.cookies import SimpleCookie
from os import environ
from socket import *
from json import dumps, loads

"""/*
    Script: Start Game
    Backend Python script for joining a game
*/"""

"""/*
    Group: Variables
*/"""
try:
    """/*
        var: cookie
        A <SimpleCookie> instance for reading and writing browser cookies
    */"""
    cookie = SimpleCookie()
    cookie.load(environ['HTTP_COOKIE'])

    """/*
        var: player_num
        The index of this player in <Server.players>
    */"""
    player_num = cookie.get('player_num').value

    """/*
        var: ip_address, port
        The ip_address and port number of the server
    */"""
    ip_address, port = cookie.get('game_address').value.split(':')

    # Create the socket

    """/*
        var: sock
        <Socket> object used to connect to the server
    */"""
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((ip_address, int(port)))
    msg = 'start=' + str(player_num)
    # Game will only start if the host clicks button
    sock.sendall(msg.encode())
    response = loads(sock.recv(4096).decode())
    print('Content-Type: application/json')
    print()
    print(dumps(response))
    sock.close()
except Exception as e:
    print('Content-Type: text/plain')
    print()
    print(e)
