#!/usr/bin/env python3
from cgitb import enable
enable()
from http.cookies import SimpleCookie
from os import environ
from cgi import FieldStorage # For ajax queries
from socket import *
from json import loads

"""/*
    Script: Lobby
    Webpage in Python for displaying the lobby information.
    Also can be queried with format=json to get the data in JSON format
*/"""

# Group: Variables

# obj: data
# A <FieldStorage> instance containing the form-data passed to this page
data = FieldStorage()

# string: format
# If format is 'json', this script will return a JSON string of the lobby
# status from the server. If not, this script will return a full HTML page.
format = data.getfirst('format', 'not-json')

# string: output
# Used for building up the output to be displayed by the script
output = ''

# int: player_num
# Index of the client in the <Server.players> array; stored in cookie
player_num = -1

# string: button
# String storing a button element iff the player is the hose
button = ''

# obj: cookie
# A <SimpleCookie> instance for reading and writing browser cookies
cookie = SimpleCookie()

# Group: Functions
# Currently there are no functions in this script. We may however re-write this
# script to use functions to make things a little neater
try:
    cookie.load(environ['HTTP_COOKIE'])
    player_num = int(cookie.get('player_num').value)
    ip_address, port = cookie.get('game_address').value.split(':')
    if player_num == 0:
        button = '<button>Start Game</button>' # Add onclick

    # Query the server for players
    sock = socket(AF_INET, SOCK_STREAM)
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
        players = ('<table class="table table-striped table-bordered">'
                   '<thead><tr><th>User Name</th></tr></thead><tbody>'
        for player in data['players']:
            players += '<tr style="color: %s;"><td>%s</td></tr>' % (
                player['colour'], player['userName'])
        players += '</tbody></table>'

        print('Content-Type: text/html')
        print()
        print("""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
                <!-- Latest compiled and minified CSS -->
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">

                <!-- Optional theme -->
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">

                <!--jQuery-->
                <script src="https://code.jquery.com/jquery-3.1.0.min.js" integrity="sha256-cCueBR6CsyA4/9szpPfrX3s49M9vUU5BgtiJj06wt/s=" crossorigin="anonymous"></script>

                <!-- Latest compiled and minified JavaScript -->
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
                <title>Arena - Lobby</title>
                <script src="../scripts/lobby.js"></script>
            </head>

            <body>
                %s
                <br />
                %s
            </body>
        </html>""" % (players, button))

except:
    # Redirect home
    print('Status: 303')
    print('Location: ../')
