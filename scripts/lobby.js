/*
    Script: Lobby Client
    AJAX script for updating the <Lobby>
*/
(function(){
    /*
        Group: Variables
    */
    /*
        var: players
        Points to the body of the table in order to add or remove players
        from the display as needed
    */
    var players;

    /*
        var: playerNum
        The value of the cookie data representing this player's index in the list of players
    */
    var playerNum;

    window.addEventListener('DOMContentLoaded', init, false);

    /*
        Group: Functions
    */

    /*
        Function: init
        Initialises the program.
        Sets the value for <players>, and adds event listeners to the
        nodes that require them.
        Creates an <Interval> to check for updates every second
    */
    function init(){
        playerNum = parseInt(getCookie('playerNum'));
        players = document.querySelector('table tbody');
        document.querySelector('#startbtn').addEventListener('click', startGame, false);

        //Check for updates every second
        window.setInterval(checkUpdates, 1000);

        window.onbeforeunload = function(e){
            console.log(e);
            return 'Are you sure you want to leave?';
        };
        window.onunload = function(e){
            var serverAddress = getCookie('gameAddress');
            var playerNum = getCookie('playerNum');
            $.ajax({
                type: 'GET',
                async: false,
                url: 'http://' + serverAddress,
                data: 'quit=' + playerNum
            });
        }
    }

    /*
        Function: checkUpdates
        Queries the server through the <Lobby> by receiving JSON data
        through an AJAX request.
        If the data received has changed since the last request, update the table.
        If the host has started the game, run <startGame>.
    */
    function checkUpdates(){
        $.ajax({
                url: 'lobby.py?format=json',
                dataType: 'json',
                data: {
                    query: playerNum
                },
                ifModified : true,
                success : function(json){
                    if(!json.started){
                        //Since it only succeeds if modified, just remove and redraw every row in the table any time things change
                        $(players).empty();
                        var numPlayers = 0;
                        $('#startbtn').prop('disabled', true);
                        json.players.forEach(function(player, index){
                            if(player !== null){
                                numPlayers ++;
                                var hostIcon = 'times';
                                var youIcon = 'times';
                                if(playerNum === index){
                                    youIcon = 'check';
                                }
                                if(player.host){
                                    hostIcon = 'check';
                                }
                                $(players).append('<tr style="color: ' + player.colour + ';"><td class="text-center col-xs-2"><span class="fa fa-' + hostIcon + '"></span></td><td class="text-center col-xs-8">' + player.userName + '</td><td class="text-center col-xs-2"><span class="fa fa-' + youIcon + '"></span></td></tr>');
                            }
                        });
                        if(numPlayers > 1 && json.players[playerNum].host){
                            $('#startbtn').prop('disabled', false);
                        }
                    }
                    else{
                        //Other players get an onclick
                        startGame();
                    }
                },
                error : function(req, error){
                    console.log(req.responseText);
                    checkIfServerCrashed(req);
                }
            }
        )
    }

    /*
        Function: startGame
        Sends an ajax request to the server to inform it that this player
        is ready to start, then redirects to the game on success
    */
    function startGame(){
        $.ajax({
            url: 'start_game.py',
            dataType: 'json',
            success : function(json){
                console.log(json);
                if(json.ready){
                    window.onbeforeunload = null;
                    window.onunload = null;
                    window.location = 'game.html';
                }
            },
            error: function(req, error){
                console.log(">>start_game_error: " + req.responseText);
                checkIfServerCrashed(req);
            }
        });
    }

    /*
        Function: getCookie
        Read cookie data by name

        Parameters:
            string cname - Name of the cookie

        Returns:
            string value - Value of the cookie, or '' if cname is
                           not found in the cookie
    */
    function getCookie(cname) {
        var name = cname + "=";
        var ca = document.cookie.split(';');
        for(var i = 0; i <ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0)===' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) === 0) {
                return c.substring(name.length,c.length);
            }
        }
        return "";
    }

    /*
        Function: checkIfServerCrashed
        Checks if the server has crashed if an AJAX request fails

        Parameters:
            jqXHR req - <jqXHR> object containing the response information
    */
    function checkIfServerCrashed(req){
        if (req.readyState < 4 || req.status >= 500){
            window.onbeforeunload = null;
            window.onunload = null;
            window.location = "../";
        }
    }
}());
