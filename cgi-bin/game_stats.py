#!/usr/bin/env python3
from cgitb import enable
enable()
from json import loads
# Because the server runs in the same dir as this file, we don't need cookies

"""/*
    Script: Game Stats
    Displays the stats of the previous game ran on this server
*/"""

# string: stats
# Player stats data from the server, to be put into a HTML table
stats = ''

# string: gameLength
# The time the game took overall
gameLength = ''
try:
    statsfile = open('../stats/game_stats')
    data = loads(statsfile.read())
    statsfile.close()
    stats = ('<table class="table table-striped table-hover table-bordered">'
             '<thead><tr><th class="text-center">User Name</th>'
             '<th class="text-center">Position</th></tr></thead><tbody>')
    players = data['players']
    for i in range(len(players)):
        player = players[i]
        stats += '<tr style="color: %s;"><td class="text-center">%s</td><td class="text-center">%i</td></tr>' % (
            player['colour'], player['username'], i + 1)
    stats += '</tbody></table>'

    mins, secs = data['gameLength']
    gameLength = ('<div class="alert alert-info">'
                  '<strong>Game Time:</strong> %i mins, %i secs'
                  '</div>')
    gameLength = gameLength % (mins, secs)
except IOError:
    stats = '<h2>Stats not available</h2>'

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
        <title>Arena - Stats</title>
    </head>

    <body>
        <div class="container">
            <h1 class="page-heading">Last Game Stats</h1>
            %s
            %s
            <a class="btn btn-primary" href="../index.html">
                <span class="glyphicon glyphicon-home"></span> 
                Home
            </a>
        </div>
    </body>
</html>
""" % (gameLength, stats))
