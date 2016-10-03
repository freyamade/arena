var address;
var port;
var result;

window.addEventListener('DOMContentLoaded', init, false);

function init(){
    address = document.querySelector('#server_address');
    port = document.querySelector('#port_num');
    result = document.querySelector('#result');
    document.querySelector('button').addEventListener('click', test, false);
}

function test(){
    var player = {x: 500, y: 500, id: 0}
    $.ajax({
        type : 'POST',
        url : 'http://' + address.value + ':' + port.value,
        dataType : 'json',
        data : {
            player : JSON.stringify(player)
        },
        success : function(json){
            result.innerHTML = json;
        },
        error : function(req){
            if(req.readyState === 4){
                result.innerHTML = req.responseText;
            }
            else if(req.readyState === 0){
                result.innerHTML = 'Connection Error';
            }
        },
        jsonpcallback : 'update'
    });
}
