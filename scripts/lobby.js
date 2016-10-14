/*
    Script: Lobby Client
    AJAX script for updating the <Lobby>
*/
(function(){
    //ptr: players
    //Points to the body of the table in order to add or remove players
    //from the display as needed
    var players;

    window.addEventListener('DOMContentLoaded', init, false);

    /*
        Function: init
        Initialises the program.
        Sets the value for <players>, and adds event listeners to the
        nodes that require them.
        Creates an <Interval> to check for updates every second
    */
    function init(){
        players = document.querySelector('table tbody');
        var buttons = document.querySelectorAll('button');
        for(var i = 0; i < buttons.length; i++){
            buttons[i].addEventListener('click', startGame, false);
        }

        //Check for updates every second
        window.setInterval(checkUpdates, 1000);
    }

    /*
        Function: checkUpdates
        Queries the server through the <Lobby> by receiving JSON data
        through an AJAX request.
        If the data received has changed since the last request, update the table.
        If the host has started the game, run <startGame>.
    */
    function checkUpdates(){
        var player_num = getCookie('player_num');
        $.ajax({
                url: 'lobby.py?format=json',
                dataType: 'json',
                data: {
                    query: player_num
                },
                ifModified : true,
                success : function(json){
                    if(!json.started){
                        //Since it only succeeds if modified, just remove and redraw every row in the table any time things change
                        $(players).empty();
                        // $('button').prop('disabled', true);
                        json.players.forEach(function(player, index){
                            if(index > 0){
                                $('button').prop('disabled', false);
                            }
                            $(players).append('<tr style="color: ' + player.colour + ';"><td>' + player.userName + '</td></tr>');
                        });
                    }
                    else{
                        //Other players get an onclick
                        startGame();
                    }
                },
                error : function(req,error){
                    checkIfServerCrashed(req);
                    //console.log(">>start_game_error: " + req.status);
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
                    window.location = 'game.html';
                }
            },
            error: function(req, error){
                checkIfServerCrashed(req);
                console.log(">>start_game_error: " + req.status);
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

    function checkIfServerCrashed(req){
        //console.log("Status Code: "+);
        if (req.readyState < 4 || req.status >= 500){
            window.location = "../";
        }
    }
}());
