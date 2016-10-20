#!/usr/bin/env python3
from cgitb import enable
enable()
# Because the server runs in the same dir as this file, we don't need cookies

"""/*
    Script: Game Stats
    Displays the stats of the previous game ran on this server
*/"""

# string: stats
# The output from the statsfile written by the server
stats = ''

try:
    statsfile = open('../stats/game_stats')
    stats = statsfile.read()
except IOError:
    stats = '<h2>Stats not available</h2>'

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
        <hr />
        <a href="../index.html">Home</a>
    </body>
</html>
""" % (stats))
