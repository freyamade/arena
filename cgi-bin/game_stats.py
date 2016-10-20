#!/usr/bin/env python3
from cgitb import enable
enable()
# Because the server runs in the same dir as this file, we don't need cookies
from shelve import open as shelf

"""/*
    Script: game_stats
    Displays the stats of the previous game ran on this server
*/"""

# string: players
# The table displaying the players in order of who dies
players = ''

# string: time
# Display of how long the game took
time = ''

statsfile = shelf('../stats/game_stats')
playerData = statsfile.get('players', [])
gameLength = statsfile.get('gameLength', ())
statsfile.close()

if len(playerData) > 0:
    players = '<table>'
    for i in range(len(playerData)):
        player = playerData[i]
        winner = ''
        if i == 0:
            winner = 'Winner!'
        players += '<tr style="color: %s;"><td>%i</td><td>%s</td><td>%s</td></tr>' % (
            player['colour'], i + 1, player['username'], winner)
    players += '</table>'

    if len(gameLength) == 2:
        time = '%i:%i' % (gameLength)
else:
    players = '<h2>No stats available! Go play a match first!</h2>'

print('Content-Type: text/html')
print()
print("""
<!DOCTYPE html>
<html>
    <head>
        <title>Arena - Stats</title>
    </head>

    <body>
        <h1>Last Game Stats</h1>
        <hr />
        %s
        <br />
        Game Time: %s
        <hr />
        <a href="../index.html">Home</a>
    </body>
</html>
""" % (players, time))
