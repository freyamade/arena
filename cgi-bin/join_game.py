#!/usr/bin/env python3
from cgitb import enable
enable()
from cgi import FieldStorage, escape
from socket import *
from http.cookies import SimpleCookie
data = FieldStorage()

username = ""
ip_address = ""
port = "44444"
error = ''
if len(data) > 0:
    # Check the passed address for connection
    # TODO - Clean the inputs, ensure everything is good
    username = escape(data.getfirst('username', 'Guest'))
    ip_address = escape(data.getfirst('address', ''))
    port = escape(data.getfirst('port', port))
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.bind(('', 44445))
        sock.connect((ip_address, int(port)))
        msg = 'join=' + username
        sock.sendall(msg.encode())
        # Receive the join status
        response = sock.recv(256).decode()
        if 'joined' in response:
            cookie = SimpleCookie()
            cookie['game_address'] = ip_address + ':' + port
            cookie['player_num'] = response.split('=')[1] #joined=num
            print(cookie)
            print('Status: 303')
            print('Location: lobby.py')
        else:
            error = 'Lobby Full'
        sock.close()
    except Exception as e:
        error = str(e)

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
