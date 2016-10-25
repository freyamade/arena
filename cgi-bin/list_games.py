#!/usr/bin/env python3
from cgitb import enable
enable()
# For this we need a socket to broadcast with
from socket import *
from json import loads

"""/*
    Script: List Games
    Webpage in Python that lists all open public servers.
    Uses <Socket>s and broadcasting to find servers.
    Waits for 3 <timeout>s before displaying results
*/"""

# Group: Variables

# array: servers
# A list of server data returned from the broadcast
servers = []

# obj: sock
# <Socket> that will be used to send a broadcast and receive responses
sock = socket(AF_INET, SOCK_DGRAM)
sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

# int: timeouts
# The number of timeouts remaining before results are displayed
timeouts = 3

# string: form_template
# A template for the form that will be used to join the game
# Will bootstrap after this file works TODO
form_template = """
<form action="join_game.py" method="POST">
    <label for="username">Username</label>
    <input type="text" id="username" name="username" placeholder="Guest"
    value="" class="form-control" />

    <input type="hidden" name="ip_address" value="%s" />
    <input type="hidden" name="port" value="%s" />
</form>"""
