#!/usr/bin/env python3
from cgitb import enable
enable()
from datetime import datetime
import os
# Because the server runs in the same dir as this file, we don't need cookies

"""/*
    Script: Game Stats
    Displays the stats of all games saved on the server
*/"""

# string: files
# HTML table containing the date for each game and a link to see the stats
files = '<div class="alert alert-info">There are no stats yet</div>'
# File name will be %d%m%Y%H%M%S.ast
# We should sort them so the latest game is at the top
if os.path.exists('../stats'):
    # Loop through the directory
    filenames = sorted([filename.split('.ast')[0] for filename in os.listdir(
        '../stats')], key=lambda date: datetime.now() - datetime.strptime(
        date, '%d%m%Y%H%M%S'))
    if len(filenames) > 0:
        files = """
        <table class="table table-striped table-hover table-bordered">
        <thead><tr><th class="text-center">Game Date</th><th></th></tr></thead>
        <tbody>"""
        for filename in filenames:
            # Button uses AJAX to request the data from the file
            files += """<tr><td class="text-center">%s</td>
            <td class="text-center">
            <button class="btn btn-primary btn-xs" data-id="%s">
            <span class="glyphicon glyphicon-file"></span> View Stats
            </button></td></tr>""" % (datetime.strptime(
            filename, '%d%m%Y%H%M%S').strftime('%d/%m/%Y @ %H:%M:%S'),
            filename)
        files += '</tbody></table>'

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
        <link rel='icon' href='favicon.ico' type='image/x-icon' />
        <script src="../scripts/game_stats.js"></script>
    </head>

    <body>
        <div class="container">
            <h1 class="page-heading">Last Game Stats</h1>
            %s
            <a class="btn btn-primary" href="../index.html">
                <span class="glyphicon glyphicon-home"></span> 
                Home
            </a>
        </div>

        <!--Modal-->
        <div class="modal fade" role="dialog" id="modal">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal">
                            &times;
                        </button>
                        <h4 class="modal-title"></h4>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info">
                        </div>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th class="text-center">
                                        User Name
                                    </th>
                                    <th class="text-center">
                                        Position
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </body>
</html>
""" % (files))
