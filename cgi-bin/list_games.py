#!/usr/bin/env python3
from cgitb import enable
enable()
# For this we need a socket to broadcast with
from socket import *
from json import loads

"""/*
    Script: List Games
    Webpage in Python that lists all open public servers.
    Uses <Socket>s and broadcasting to find servers.
    Waits for 3 <timeout>s before displaying results
*/"""

# Group: Variables

# hash: servers
# A dict of server data returned from the broadcast
# K: V = Server Address: Server Data
servers = {}

# obj: sock
# <Socket> that will be used to send a broadcast and receive responses
sock = socket(AF_INET, SOCK_DGRAM)
sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

# int: timeouts
# The number of timeouts remaining before results are displayed
# Timeouts are set to 1 second
timeouts = 3

# string: form_template
# A template for the form that will be used to join the game
form_template = """
<form action="join_game.py" method="POST">
    <div class="input-group">
        <span class="input-group-addon">
            Username
        </span>
        <input type="text" name="username" placeholder="Guest"
        value="" class="form-control username" />
        <span class="input-group-btn">
            <button class="btn btn-primary" type="submit">
                <span class="glyphicon glyphicon-share-alt"></span>
                 Join Game
            </button>
        </span>
    </div>

    <input type="hidden" class="ip" name="ip_address" value="%s" />
    <input type="hidden" class="port" name="port" value="%s" />
</form>"""

# string: protected_form_template
# An alternate version of <form_template> for use when passwords are needed
protected_form_template = """
<form action="join_game.py" method="POST">
    <div class="input-group">
        <span class="input-group-addon">
            Username
        </span>
        <input type="text" name="username" placeholder="Guest"
        value="" class="form-control username" />
    </div>
    <div class="input-group">
        <span class="input-group-addon">
            Password
        </span>
        <input type="text" name="password"
        value="" class="form-control password" />
    </div>
    <button class="btn btn-primary" type="submit">
        <span class="glyphicon glyphicon-share-alt"></span>
         Join Game
    </button>

    <input type="hidden" class="ip" name="ip_address" value="%s" />
    <input type="hidden" class="port" name="port" value="%s" />
</form>"""

# string: error
# A string that will contain any error message.
# Will be put in a Bootstrap alert
error = ''

# string: server_table
# A string containing the table of the servers and their data
server_table = """<div class="alert alert-info">
                      <strong>No Servers Found</strong>
                  </div>"""

try:
    sock.sendto('arena_broadcast_req'.encode(), ('255.255.255.255', 44445))
    # Set the timeout and wait for responses
    sock.settimeout(1)
    while timeouts > 0:
        try:
            data, address = sock.recvfrom(1024)
            data = loads(data.decode())
            servers[tuple(data['address'])] = data['data']
        except timeout:
            timeouts -= 1
except Exception as e:
    error = e

if len(servers) != 0:
    server_table = """<table class="table table-bordered table-striped">
                          <thead>
                              <tr>
                                  <th class="text-center col-sm-4">
                                      Address
                                  </th>
                                  <th class="text-center col-sm-4">
                                      Players
                                  </th>
                                  <th class="text-center col-sm-4">
                                      Join
                                  </th>
                              </tr>
                          </thead>
                          <tbody>
                   """
    for addr in servers:
        data = servers[addr]
        player_data = [player for player in data['players']
                       if player is not None]
        players = ''
        if len(player_data) > 0:
            players = '<ol>'
            for player in player_data:
                players += """<li style="color: %s;">
                                  %s
                              </li>
                           """ % (player['colour'], player['userName'])
            players += '</ol>'
        else:
            players = 'No Players in Lobby'
        this_form = (form_template if not data['password'] else
            protected_form_template)
        this_form = this_form % (addr[0], addr[1])
        server_table += """<tr>
                               <td class="text-center">
                                   %s
                               </td>
                               <td class="text-center">
                                   %s
                               </td>
                               <td>
                                   %s
                               </td>
                           </tr>
                        """ % (addr[0], players, this_form)
    server_table += '</tbody></table>'
if error != '':
    error = """<div class="alert alert-danger">
                   %s
               </div>""" % (str(error))

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
        <title>Arena - Server List</title>
        <script>
            var join_status;
            var modal_shown = false;
            $(document).ready(init);

            function init(){
            join_status = $('#join_status');
            join_status.on('hide.bs.modal', function(){modal_shown = false;});
                $("form").submit(function(e){
                    var target = $(e.target);
                    var username = target.find('.username').val();
                    if(username === ''){
                        username = 'Guest';
                    }
                    var password = target.find('.password');
                    if(password.length === 0){
                        password = 'None';
                    }
                    else{
                        password = password.val();
                        if(password === ''){
                            password = 'None';
                        }
                    }
                    var data = {
                        username: username,
                        ip_address: target.find('.ip').val(),
                        port: target.find('.port').val(),
                        password: password
                    }
                    $.post('join_game.py', data);
                    e.preventDefault();
                });
            }

            $(document).ajaxSuccess(function(e, xhr){
                //Redirect to lobby.py
                //Might have to fix things to make cookies work
                window.location = 'lobby.py';
            });

            $(document).ajaxError(function(e, xhr){
                message('Error - ' + xhr.responseText, 'danger');
            });

            
            function message(msg, level){
                if(!modal_shown){
                    join_status.modal('show');
                    modal_shown = true;
                }
                $('.modal-title').html(msg);
            }
        </script>
        <link rel='icon' href='../images/favicon.ico' type='image/x-icon' />
    </head>

    <body>
        <div class="container">
            <h1 class="page-heading">
                Open Public Servers
            </h1>
            %s
            %s
            <a href=".." class="btn btn-primary"><span
            class="glyphicon glyphicon-home"></span> Home</a>
        </div>

        <div id="join_status" class="modal fade" role="dialog">
        <div class="modal-dialog">
            <!--Content-->
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal">
                        &times;
                    </button>
                    <h4 class="modal-title"></h4>
                </div>
            </div>
        </div>
    </div>
    </body>
</html>""" % (error, server_table))
