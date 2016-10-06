//AJAX the file to get the players, set up lobby.py to allow two displays
(function(){
    var players;

    window.addEventListener('DOMContentLoaded', init, false);

    function init(){
        players = document.querySelector('table tbody');
        var buttons = document.querySelectorAll('button');
        for(var i = 0; i < buttons.length; i++){
            buttons[i].addEventListener('click', startGame, false);
        }

        //Check for updates every second
        window.setInterval(checkUpdates, 1000);
    }

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
                }
            }
        )
    }

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
                console.log(error);
            }
        });
    }

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
}());
