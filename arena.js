//Tidying up the code and making it look nicer

(function(){
    //Global Variables
    //Game switch
    var ready = false;
    //HTML Elements
    var canvas;
    var context;
    var height;
    var width;
    var displayRows = [];
    //Bullet Constants
    var bulletSize = 5;
    var bulletSpeed = 5;
    //Player Constants
    var playerSize = 20;
    var playerSpeed = 4;
    var maxBullets = 3;
    //Players
    var players = [null, null, null, null];
    //Local Player Handling
    var local; //Index of local player
    var move = {
        up : false,
        down : false,
        left : false,
        right : false
    };
    //Vars for game over
    var updateInterval;
    var ajaxInterval;
    var playersAlive = 4;

    //Classes (might move to seperate file)
    function Bullet(x, y, owner, number){
        //Instantiate a Bullet at pos (x, y).
        //This bullet will be players[owner].bullets[number]
        return {
            //Instance Variables
            size : bulletSize,
            // Ensure center of bullet is at passed (x, y)
            x : x - (bulletSize / 2),
            y : y - (bulletSize / 2),
            speed : bulletSpeed,
            xChange : 0,
            yChange : 0,
            bounces : 3,
            //Maintain data on where this bullet instance will live
            owner : owner,
            number : number,

            //Instance Methods
            draw : function(){
                //Draw the bullet
                context.fillRect(this.x, this.y, this.size, this.size);
                //Checks
                this.checkWalls();
                this.checkPlayers();
                //Update position for the next frame
                this.x += this.speed * this.xChange;
                this.y += this.speed * this.yChange;
            },

            checkWalls : function(){
                //Check if the bullet has hit a wall, and if it has, handle
                //bouncing
                //Will need to change when we add other walls and such
                if(this.x < 0){
                    //Hit left wall
                    this.collision('left');
                }
                else if(this.x + this.size > width){
                    //Hit right wall
                    this.collision('right');
                }
                else if(this.y < 0){
                    //Hit top wall
                    this.collision('top');
                }
                else if(this.y + this.size > height){
                    //Hit bottom wall
                    this.collision('bottom');
                }
            },

            checkPlayers : function(){
                //Check if the bullet has hit a player, and if it has,
                //send a call to that player saying it's been hit
                for(var i = 0; i < players.length; i ++){
                    if(i !== local){
                        var player = players[i];
                        if(player.isAlive() && collisionBetween(this, player)){
                            this.destroy();
                            players[i].hit(this);
                            break;
                        }
                    }
                }
            },

            collision : function(wall){
                //Handle a collision against the 'wall' wall
                //Ensure the bullet can bounce again
                if(this.bounces <= 0){
                    this.destroy()
                    return;
                }
                //Get the wall it has collided with, change bullet direction
                //and place it back onto the board
                switch(wall){
                    case 'left':
                        //Reverse x
                        this.xChange *= -1;
                        this.x = 0;
                        break;
                    case 'right':
                        //Reverse x
                        this.xChange *= -1;
                        this.x = width - this.size;
                        break;
                    case 'top':
                        //Reverse y
                        this.yChange *= -1;
                        this.y = 0;
                        break;
                    case 'bottom':
                        //Reverse y
                        this.yChange *= -1;
                        this.y = height - this.size;
                        break;
                }
                this.speed *= 0.8;
                this.bounces -= 1;
            },

            destroy : function(){
                //Remove this bullet from it's player's list
                players[this.owner].bulletDestroyed(number);
            },

            fire : function(coords){
                //Get the angle of motion for the bullet and set it moving
                var a = this.getAngle(
                    coords.x,
                    coords.y);
                this.xChange = this.speed * Math.cos(a);
                this.yChange = this.speed * Math.sin(a) * -1;
            },

            getAngle : function(destinationX, destinationY){
                //Take in the coordinates of the click and return the angle in
                //radians the bullet needs to travel
                var opposite;
                var adjacent;
                var angle;
                var sourceX = this.x + (this.size / 2);
                var sourceY = this.y + (this.size / 2);
                if(destinationX > sourceX){
                    if(destinationY <= sourceY){
                        opposite = Math.abs(destinationY - sourceY);
                        adjacent = Math.abs(destinationX - sourceX);
                        angle = 0;
                    }
                    else{
                        opposite = Math.abs(destinationX - sourceX);
                        adjacent = Math.abs(destinationY - sourceY);
                        angle = (3 * Math.PI) / 2;
                    }
                }
                else{
                    if(destinationY <= sourceY){
                        opposite = Math.abs(sourceX - destinationX);
                        adjacent = Math.abs(sourceY - destinationY);
                        angle = Math.PI / 2;
                    }
                    else{
                        opposite = Math.abs(sourceY - destinationY);
                        adjacent = Math.abs(sourceX - destinationX);
                        angle = Math.PI;
                    }
                }
                angle += Math.atan2(opposite, adjacent);
                return angle;
            }
        }
    }

    function Player(x, y, index, colour, userName){
        //Instantiate a new player with coordinates (x, y) with colour 'colour'
        //This player will be found in players[index]
        return {
            //Instance variables
            size : playerSize,
            //Ensure player is centered at coordinate params
            x : x - (playerSize / 2),
            y : y - (playerSize / 2),
            xChange : 0,
            yChange : 0,
            health : 100,
            bullets : [null, null, null],
            numBullets : maxBullets,
            id : index,
            colour : colour,
            userName : userName,
            alive : true,

            //Instance Methods
            getHealth : function(){
                //Public getter for health
                return this.health;
            },

            getBullets : function(){
                //Public getter for numBullets
                return this.numBullets;
            },

            getUserName : function(){
                //Public getter for userName
                return this.userName;
            },

            isAlive : function(){
                //Public getter for Alive state
                return this.alive;
            },

            move : function(e){
                //Handles moving of player, called on keydown
                switch(e.keyCode){
                    case 87: // w
                    case 38: // up arrow
                        if(!move.up){
                            this.yChange = playerSpeed * -1;
                            move.up = true;
                            move.down = false;
                        }
                        return;
                    case 65: // a
                    case 37: // left arrow
                        if(!move.left){
                            this.xChange = playerSpeed * -1;
                            move.left = true;
                            move.right = false;
                        }
                        return;
                    case 83: //s
                    case 40: // down arrow
                        if(!move.down){
                            this.yChange = playerSpeed;
                            move.down = true;
                            move.up = false;
                        }
                        return;
                    case 68: //d
                    case 39: //right arrow
                        if(!move.right){
                            this.xChange = playerSpeed;
                            move.right = true;
                            move.left = false;
                        }
                        return;
                }
            },

            stop : function(e){
                //Handles stopping of player, called on keyup
                switch(e.keyCode){
                    case 87: // w
                    case 38: // up arrow
                        if(move.up){
                            this.yChange = 0;
                            move.up = false;
                        }
                        return;
                    case 65: // a
                    case 37: // left arrow
                        if(move.left){
                            this.xChange = 0;
                            move.left = false;
                        }
                        return;
                    case 83: //s
                    case 40: // down arrow
                        if(move.down){
                            this.yChange = 0;
                            move.down = false;
                        }
                        return;
                    case 68: //d
                    case 39: //right arrow
                        if(move.right){
                            this.xChange = 0;
                            move.right = false;
                        }
                        return;
                }
            },

            draw : function(){
                //Draw the player
                context.fillStyle = this.colour;
                context.fillRect(this.x, this.y, this.size, this.size);
                //Test Collisions
                this.wallCollision();
                //Update position for next frame
                this.x += this.xChange;
                this.y += this.yChange;

                //Draw the bullets
                this.bullets.forEach(function(bullet, index){
                    if(bullet !== null){
                        bullet.draw();
                    }
                });
            },

            fireBullet : function(coords){
                //Checks if a new bullet can be fired, and fires one
                if(this.numBullets > 0){
                    var i = 0;
                    for(i; i < maxBullets; i ++){
                        if(this.bullets[i] === null){
                            break;
                        }
                    }
                    this.bullets[i] = new Bullet(
                        this.x + (this.size / 2),
                        this.y + (this.size / 2),
                        this.id,
                        i);
                    this.numBullets -= 1;
                    this.bullets[i].fire(coords);
                }
            },

            bulletDestroyed : function(number){
                //this.bullets[number] has been destroyed
                this.bullets[number] = null;
                this.numBullets += 1;
            },

            wallCollision : function(){
                //Test if the player has hit a wall, if so, stop it from moving
                //out of the board
                if(this.x < 0){
                    this.x = 0;
                }
                else if(this.x + this.size > width){
                    this.x = width - this.size;
                }
                if(this.y < 0){
                    this.y = 0;
                }
                else if(this.y + this.size > height){
                    this.y = height - this.size;
                }
            },

            playerCollision : function(){
                //Test if this player has run into another player, and stop
                //this player from phasing through the other one

                //Not sure if we need it since I'm not sure people will get too
                //close to other players
            },

            hit : function(bullet){
                //Player hit by bullet, subtract health accordingly
                var damage = bullet.speed * 2;
                this.health = (this.health - damage).toFixed(2);
                if(this.health <= 0){
                    this.destroy();
                }
            },

            destroy : function(){
                this.alive = false;
                playersAlive -= 1;
            }
        }
    }

    //Helper methods
    function collisionBetween(obj1, obj2){
        //Check if obj1 and obj2 have collided
        if((obj1.x + obj1.size) < obj2.x || obj1.x > (obj2.x + obj2.size)
            || (obj1.y + obj1.size) < obj2.y || obj1.y > (obj2.y + obj2.size)){
            return false;
        }
        return true;
    }

    function getMouseCoords(e){
        var x;
        var y;
        x = e.pageX - canvas.offsetLeft;
        y = e.pageY - canvas.offsetTop;
        return {
            x : x,
            y : y
        }
    }

    //Running Code / Game Methods
    window.addEventListener('DOMContentLoaded', init, false);

    function init(){
        //Initialise global variables
        canvas = document.querySelector('canvas');
        context = canvas.getContext('2d');
        height = canvas.height;
        width = canvas.width;
        displayRows = $('tbody tr');

        canvas.addEventListener('click', playerFire, false);
        window.addEventListener('keydown', playerMove, false);
        window.addEventListener('keyup', playerStop, false);

        //Setup Players
        playersSetup();

        //Run the ajax update every 16ms, just before the update method
        //ajaxInterval = window.setInterval(getData, 16);

        //We're gonna try and run this game at 60fps (16ms)
        //If the ajax can't keep up, lower to 30fps (33ms)
        updateInterval = window.setInterval(readyGame, 100);
    }

    function readyGame(){
        if(ready){
            clearInterval(updateInterval);
            updateInterval = window.setInterval(update, 16);
        }
    }

    function playersSetup(){
        //In the MP version, read in POST data and populate players accordingly
        //In SP, just creates players for testing
        var sectorMap = [
            //x        y
            [width / 4, height / 4],
            [(3 * width) / 4, height / 4],
            [width / 4, (3 * height) / 4],
            [(3 * width) / 4, (3 * height) / 4]
        ]
        $.ajax({
            url: 'cgi-bin/single-player.py',
            dataType : 'json',
            success : function(json){
                json.players.forEach(function(player, index){
                    var coords = sectorMap[player.sector - 1];
                    players[index] = new Player(
                        coords[0], coords[1], index, player.colour, player.userName);
                    if(player.local){
                        local = index;
                    }
                });
                //Draw the names of players into the table
                players.forEach(function(player, index){
                    if(player.isAlive()){
                        var row = $(displayRows[player.id]);
                        row.css({'color': player.colour});
                        row.find('.name-container').html(player.getUserName());
                    }
                });
                ready = true;
            }
        });
    }

    function update(){
        //Main Game Loop
        //Check if game is over
        isGameOver();
        //If it's not, update the field
        updateDisplays();
        draw();
    }

    function draw(){
        context.clearRect(0, 0, width, height);
        //Draw the walls
        context.beginPath();
        context.moveTo(0, height/2);
        context.lineTo((3 * width/8), height/2);
        context.stroke();
        context.beginPath();
        context.moveTo(width, height/2);
        context.lineTo((5 * width/8), height/2);
        context.stroke();
        context.beginPath();
        context.moveTo(width/2, 0);
        context.lineTo(width/2, (3 * height)/8);
        context.stroke();
        context.beginPath();
        context.moveTo(width/2, height);
        context.lineTo(width/2, (5*height)/8);
        context.stroke();
        //Draw the players, which draw their own bullets
        players.forEach(function(player, index){
            if(player.isAlive()){
                player.draw();
            }
        });
    }

    function updateDisplays(){
        //Ensure the displays are up to date
        players.forEach(function(player, index){
            var health = player.isAlive() ? player.getHealth() : 0;
            var row = $(displayRows[player.id]);
            row.find('.health-container').html(health);
            row.find('.bullets-container').html(player.getBullets());
        });
    }

    function playerFire(e){
        //Wrapper for player.fireBullet
        var coords = getMouseCoords(e);
        players[local].fireBullet(coords);
    }

    function playerMove(e){
        //Wrapper for player.move
        players[local].move(e);
    }

    function playerStop(e){
        //Wrapper for player.stop
        players[local].stop(e);
    }

    function isGameOver(){
        if(playersAlive === 1){
            gameOver();
        }
    }

    function gameOver(){
        context.clearRect(0, 0, width, height);
        clearInterval(updateInterval);
        // clearInterval(ajaxInterval);
        //Get the remaining player
        var player;
        for(var i = 0; i < players.length; i ++){
            if(players[i].isAlive()){
                player = players[i];
            }
        }
        window.alert('Game Over! Winner: ' + player.getUserName());
    }

}());
