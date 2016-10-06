#!/usr/bin/env python3
from cgitb import enable
enable()
from http.cookies import SimpleCookie
from os import environ
from cgi import FieldStorage # For ajax queries
from socket import *
from json import loads

"""
Constantly monitor the setup of the file using ajax and display a list of
players currently in the lobby, in their player colours, along with a mark
beside the local player, and a start game button for player_num 0
"""

data = FieldStorage()
format = data.getfirst('format', 'not-json')
output = ''
player_num = -1
button = ''
cookie = SimpleCookie()
# try:
cookie.load(environ['HTTP_COOKIE'])
player_num = int(cookie.get('player_num').value)
ip_address, port = cookie.get('game_address').value.split(':')
if player_num == 0:
    button = '<button>Start Game</button>' # Add onclick

# Query the server for players
sock = socket(AF_INET, SOCK_STREAM)
sock.bind(('', 44445))
sock.connect((ip_address, int(port)))
msg = 'query=' + str(player_num) 
sock.sendall(msg.encode())
# Receive the status
response = sock.recv(4096).decode()
data = loads(response)
sock.close()
if format == 'json':
    # Handle the json output, done later
    from json import dumps
    print('Content-Type: application/json')
    print()
    print(dumps({'players': data['players'], 'started': data['started']}))
else:
    players = '<table><thead><tr><th>User Name</th></tr></thead><tbody>'
    for player in data['players']:
        players += '<tr style="color: %s;"><td>%s</td></tr>' % (player['colour'], player['userName'])
    players += '</tbody></table>'

    print('Content-Type: text/html')
    print()
    print("""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Arena - Lobby</title>
            <script src="https://code.jquery.com/jquery-3.1.0.min.js" integrity="sha256-cCueBR6CsyA4/9szpPfrX3s49M9vUU5BgtiJj06wt/s=" crossorigin="anonymous"></script>
            <script src="../scripts/lobby.js"></script>
        </head>

        <body>
            %s
            <br />
            %s
        </body>
    </html>""" % (players, button))

# except:
#     # Redirect home
#     print('Status: 303')
#     print('Location: ../')
