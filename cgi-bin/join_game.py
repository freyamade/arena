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
    error = ''
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect((ip_address, int(port)))
        msg = 'join=' + username
        sock.sendall(msg.encode())
        # Receive the join status
        response = sock.recv(1024).decode()
        if 'joined' in response:
            cookie['game_address'] = ip_address + ':' + port
            #joined=num;token
            data = response.split('=')[1].split(';')
            cookie['player_num'] = data[0]
            cookie['game_token'] = data[1]
        else:
            error = 'Lobby Full'
        sock.close()
    except OSError as e:
        num = int(e.errno)
        if num == 111:
            error = ('Connection failed. '
                     'Check that the server is open and try again.')
        else:
            error = str(e) + """<br />Please report that you found error
                    number %i
                    <a href="https://github.com/CompSci2k18/Arena/issues">
                    here</a>""" % num
    except Exception as e:
        error = str(e)
    finally:
        return error

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
        error += newGame()
    else:
        # Cookie exists, check if the address in the form is equal to the
        # address in the cookie
        cookie_address = cookie.get('game_address').value
        if cookie_address != (ip_address + ':' + port):
            # The player has connected to a new game
            error += newGame()
        # Else, check if they are already in this game
        else:
            sock = socket(AF_INET, SOCK_STREAM)
            try:
                sock.connect((ip_address, int(port)))
                msg = 'token=' + cookie.get('player_num').value
                sock.sendall(msg.encode())
                # Receive the token and compare it with cookie token
                response = sock.recv(4096).decode()
                sock.close()
                cookie_token = cookie.get('game_token').value
                if 'rejoin' in response or response != cookie_token:
                    # This player has to be join the game
                    error += newGame()
            except:
                error += newGame()
    finally:
        print(cookie)
        if error == '':
            print('Status: 303')
            print('Location: lobby.py')

form = """
<form action="" method="POST">
Username: <input type="text" name="username" placeholder="Guest" value="%s"/>
<br />
IP Address: <input type="text" name="address" required value="%s" /><br />
Port Number: <input type="text" name="port" value="44444" required value="%s"
/><br />
<input type="submit" />
</form>""" % (username, ip_address, port)

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
