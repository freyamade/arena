//AJAX the file to get the players, set up lobby.py to allow two displays
(function(){
    var players;

    window.addEventListener('DOMContentLoaded', init, false);

    function init(){
        players = document.querySelector('table tbody');

        //Check for updates every second
        window.setInterval(checkUpdates, 1000);
    }

    function checkUpdates(){
        $.ajax({
                url: 'lobby.py?format=json',
                dataType: 'json',
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
                            var playerUser = '?';
                            if(Number(getCookie('player_num')) === index){
                                playerUser = 'You';
                            }
                            $(players).append('<tr style="colour: ' + player.colour + ';"><td>' + player.userName + '</td><td>' + playerUser + '</td></tr>');
                        });
                    }
                    else{
                        window.location = 'game.html';
                    }
                }
            }
        )
    }

    function getCookie(cname) {
        var name = cname + "=";
        var ca = document.cookie.split(';');
        for(var i = 0; i <ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) == 0) {
                return c.substring(name.length,c.length);
            }
        }
        return "";
    }
}());
