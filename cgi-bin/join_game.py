#!/usr/bin/env python3
from cgitb import enable
enable()
from cgi import FieldStorage, escape
from socket import *
from os import environ
from http.cookies import SimpleCookie

"""/*
    Script: Join Game
    Webpage in Python to allow a user to join an active game server.
    Servers can only be joined if they are not full and have not started.
*/"""

# obj: data
# A <FieldStorage> instance containing the form-data passed to this page
data = FieldStorage()

# string: username
# The username that the user inserts into the form
username = ""

# string: ip_address
# The ip address that the user inserts into the form
ip_address = ""

# string: port
# The port number that the user inserts into the form; defaults to 44444
port = "44444"

# string: error
# A string for outputting any errors that occur
error = ''

"""/*
    Function: newGame
    Set up the player in the lobby of the passed address, if they aren't
    already connected to the server at the address
*/"""
def newGame():
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.bind(('', 44445))
        sock.connect((ip_address, int(port)))
        msg = 'join=' + username
        sock.sendall(msg.encode())
        # Receive the join status
        response = sock.recv(256).decode()
        if 'joined' in response:
            cookie['game_address'] = ip_address + ':' + port
            cookie['player_num'] = response.split('=')[1] #joined=num
        else:
            error = 'Lobby Full'
        sock.close()
    except Exception as e:
        # #12 will be fixed here
        error = str(e)

if len(data) > 0:
    # Check the passed address for connection
    username = escape(data.getfirst('username', 'Guest'))
    ip_address = escape(data.getfirst('address', ''))
    port = escape(data.getfirst('port', port))

    cookie = SimpleCookie()
    try:
        # Try to load a cookie for this website
        cookie.load(environ['HTTP_COOKIE'])
    except KeyError:
        # No cookie, run the new game function
        newGame()
    else:
        # Cookie exists, check if the address in the form is equal to the
        # address in the cookie
        cookie_address = cookie.get('game_address').value
        if cookie_address != (ip_address + ':' + port):
            # The player has connected to a new game
            newGame()
        # Else, they've already joined this game
    finally:
        print(cookie)
        print('Status: 303')
        print('Location: lobby.py')

form = """
<form action="" method="POST">
Username: <input type="text" name="username" placeholder="Guest" value="%s"/><br />
IP Address: <input type="text" name="address" required value="%s" /><br />
Port Number: <input type="text" name="port" value="44444" required  value="%s" /><br />
<input type="submit" />
</form>""" %(username, ip_address, port)

print('Content-Type: text/html')
print()
print("""
<!DOCTYPE html>
<html>
    <head>
        <title>Arena - Join Game</title>
    </head>

    <body>
        <h1>Join A Game</h1>
        %s
        <h3>%s</h3>
    </body>
</html>""" % (form, error))
