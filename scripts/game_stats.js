(function(){
    /*
        Script: Game Stats AJAX
        AJAX to get the data from the relevant file to populate the
        modal
    */
    $(document).ready(function(){
        $('table button').click(request);
    });

    /*
        Function: request
        Request the file data from the selected match stats.
        Uses the dataset attributes from the button to determine the
        correct file
    */
    function request(e){
        var datestring = e.target.dataset.id;
        var date = [
            datestring.substring(0, 2),   //day
            datestring.substring(2, 4),   //month
            datestring.substring(4, 8),   //year
            datestring.substring(8, 10),  //hour
            datestring.substring(10, 12), //minute
            datestring.substring(12, 14), //second
        ]
        var filename = datestring + '.ast';
        //Send a request to load the filename
        $.getJSON('../stats/' + filename, function(data){
            var time = data.gameLength;
            var players = data.players;
            $('.modal-title').html(date[0] + '/' + date[1] + '/' +
            date[2] + ' @ ' + date[3] + ':' + date[4] + ':' + date[5])
            $('#modal .alert').html('<strong>Game Time:</strong> '
                + time[0] + ' mins, ' + time[1] + ' secs.');
            //Clear the modal table
            $('#modal tbody').empty();
            players.forEach(function(player, index){
                $('#modal tbody').append('<tr style="color: '
                + player.colour + '"><td class="text-center">'
                + player.username + '</td><td class="text-center">'
                + (index + 1) + '</td></tr>');
            });
            $('#modal').modal();
        });
    }
}())