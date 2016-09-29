#!/usr/bin/env python3

from cgitb import enable
enable()
import os
from http.cookies import SimpleCookie
from shelve import open as shelf

# List all games, the usernames of the players and provide a link to join if
# it's possible

join_form_template = """<form action="join_game.py" method="POST">
<input type="hidden" name="filename" value="%s"/>
<input type="submit" value="Join Game" /> 
</form>"""
cant_join = 'Lobby Full'

os.chdir('../games')
filenames = set()
for filename in os.listdir():
    filenames.add(filename.split('.')[0])

# Go back to this directory just in case
os.chdir('../cgi-bin')

if len(filenames) > 0:
    output = '<table><thead><tr><th>Game</th><th>Players</th><th>Join</th></tr></thead><tbody>'
    num = 1
    for filename in filenames:
        gamefile = shelf('../games/' + filename)
        players_list = '<ul>'
        for player in gamefile['players']:
            players_list += '<li style="color: %s;"">%s</li>' % (player['colour'], player['userName'])
        players_list += '</ul>'
        status = ''
        if gamefile['joinable']:
            status = join_form_template % (filename)
        else:
            status = cant_join
        output += '<tr><td>%i</td><td>%s</td><td>%s</td></tr>' % (num, players_list, status)
    output += '</tbody></table>'

else:
    output = '<h3>No Games in progress</h1><p>Click <a href="create-game.py">here</a> to create your own</p>'
print('Content-Type: text/html')
print()
print("""
<!DOCTYPE html>
<html>
    <head>
        <title>Arena - All Games</title>
    </head>

    <body>
        %s
    </body>
</html>
""" % (output))
