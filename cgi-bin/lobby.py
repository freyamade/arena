#!/usr/bin/env python3
from cgitb import enable
enable()
from cgi import FieldStorage
from http.cookies import SimpleCookie
from os import environ
from shelve import open as shelf

"""
Constantly monitor the setup of the file using ajax and display a list of
players currently in the lobby, in their player colours, along with a mark
beside the local player, and a start game button for player_num 0
"""
data = FieldStorage()
format = data.getfirst('format', 'not-json')
output = ''
filename = ''
# If player is player 1, give them a start game button
player_num = -1
button = ''
cookie = SimpleCookie()
try:
    cookie.load(environ['HTTP_COOKIE'])
    filename = cookie.get('filename').value
    player_num = int(cookie.get('player_num').value)
    if player_num == 0:
        button = '<button>Start Game</button>'
except KeyError:
    # Redirect to home
    print('Status: 303')
    print('Location: ../')

# Get the players currently in the file
gamefile = shelf('../games/' + filename)
if format == 'json':
    from json import dumps
    print('Content-Type: application/json')
    print()
    print(dumps({"players": gamefile["players"]}))
    gamefile.close()
else:
    players = '<table><thead><tr><th>Player Name</th><th>Player</th></tr></thead><tbody>'
    index = 0
    for player in gamefile['players']:
        players += '<tr style="color: %s;"><td>%s</td><td>%s</td></tr>' % (
            player['colour'], player['userName'], 'You' if player_num == index else '?')
        index += 1
    players += '</tbody></table>'
    gamefile.close()

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
    </html>""" %(players, button))
