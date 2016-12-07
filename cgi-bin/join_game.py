#!/usr/bin/env python3
from cgitb import enable
enable()
from cgi import FieldStorage, escape
from socket import *
from os import environ
from http.cookies import SimpleCookie

"""/*
    Script: Join Game
    Handles join requests from the form on the index page.
    Servers can only be joined if they are not full and have not started.
*/"""

"""/*
    Group: Variables
*/"""


"""/*
    var: data
    A <FieldStorage> instance containing the form-data passed to this page
*/"""
data = FieldStorage()

"""/*
    var: username
    The username that the user inserts into the form
*/"""
username = ""

"""/*
    var: ip_address
    The ip address that the user inserts into the form
*/"""
ip_address = ""

"""/*
    var: port
    The port number that the user inserts into the form; defaults to 44444
*/"""
port = "44444"

"""/*
    var: error
    A string for outputting any errors that occur
*/"""
error = ''

"""/*
    Group: Functions
*/"""

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
        msg = 'join=' + username + ';' + password
        sock.sendall(msg.encode())
        # Receive the join status
        response = sock.recv(1024).decode()
        if 'joined' in response:
            cookie['game_address'] = ip_address + ':' + port
            #joined=num;token
            data = response.split('=')[1].split(';')
            cookie['player_num'] = data[0]
            cookie['game_token'] = data[1]
        elif 'incorrect' in response:
            error = 'Incorrect password for server'
        else:
            error = 'Lobby Full'
        sock.close()
    except OSError as e:
        num = int(e.errno)
        if num == 111:
            error = ('Connection failed. '
                     'Check that the server is open and the ip is correct.')
        else:
            error = str(e)
    except Exception as e:
        error = str(e)
    finally:
        return error

if len(data) > 0:
    # Check the passed address for connection
    username = escape(data.getfirst('username', 'Guest'))
    ip_address = escape(data.getfirst('ip_address', ''))
    port = escape(data.getfirst('port', port))
    password = escape(data.getfirst('password', 'None'))

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
        cookie_address = cookie.get('game_address', '')
        if cookie_address != '':
            cookie_address = cookie_address.value
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
        print('Content-Type: text/html')
        if error == '':
            print('Status: 200')
            print(cookie)
            print()
        else:
            print('Status: 400')
            print()
            print(error)
