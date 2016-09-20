//Tidying up the code and making it look nicer

(function(){
    //Global Variables
    //Game switch
    var ready = false;
    var countdownTimer = 3;
    //HTML Elements
    var canvas;
    var context;
    var height;
    var width;
    var displayRows = [];
    //Bullet Constants
    var bulletSize = 5;
    var bulletSpeed = 25; //Messed up with some of the maths
    var maxBounces = 3;
    var maxDamage = 10;
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
    //Obstacles
    var obstacles = [];
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
            bounces : maxBounces,
            //Maintain data on where this bullet instance will live
            owner : owner,
            number : number,

            //Instance Methods
            getMovementData : function(){
                return {
                    x : this.x,
                    y : this.y,
                    xChange : this.xChange,
                    yChange : this.yChange
                }
            },

            getDamage : function(){
                var damage = maxDamage;
                for(var i = 0; i < (maxBounces - this.bounces); i ++){
                    damage *= 0.8;
                }
                return damage;
            },

            draw : function(){
                //Draw the bullet
                context.fillRect(this.x, this.y, this.size, this.size);
                //Checks
                this.checkWalls();
                this.checkPlayers();
                //Update position for the next frame
                this.x += this.xChange;
                this.y += this.yChange;
            },

            checkWalls : function(){
                //Check if the bullet has hit a wall, and if it has, handle
                //bouncing
                //Will need to change when we add other walls and such
                if(this.x < 0){
                    //Hit left wall
                    this.collision(false, 0);
                }
                else if(this.x + this.size > width){
                    //Hit right wall
                    this.collision(false, width - this.size);
                }
                else if(this.y < 0){
                    //Hit top wall
                    this.collision(true, 0);
                }
                else if(this.y + this.size > height){
                    //Hit bottom wall
                    this.collision(true, height - this.size);
                }

                //Check obstacles here too
                for(var i = 0; i < obstacles.length; i++){
                    //Check for collisions
                    obstacles[i].checkBulletCollision(this);
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

            collision : function(horizontal, pos){
                //Handle a collision against a 'horizontal' wall
                //and reset the correct coordinate to 'pos'
                //Ensure the bullet can bounce again
                if(this.bounces <= 0){
                    this.destroy()
                    return;
                }
                //Get the wall it has collided with, change bullet direction
                //and place it back onto the board
                if(horizontal){
                    this.yChange *= -1;
                    this.y = pos;
                }
                else{
                    this.xChange *= -1;
                    this.x = pos;
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
            health : 100.00,
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

            getMovementData : function(){
                //Public getter for position
                return {
                    x : this.x,
                    y : this.y,
                    xChange : this.xChange,
                    yChange : this.yChange,
                }
            },

            setX : function(x){
                //Public setter for this.x
                this.x = x;
            },

            setY : function(y){
                //Public setter for this.y
                this.y = y;
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
                var damage = bullet.getDamage();
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

    function Obstacle(x1, y1, x2, y2){
        //Create an obstacle which will be drawn as a straight line
        //Allow for only straight lines to begin
        //When creating obstacles, make sure that (x1, y1) is closer to (0, 0)
        return {
            //Handling for these vars -> x1 < x2 || y1 < y2
            x1 : x1,
            y1 : y1,
            x2 : x2,
            y2 : y2,
            //Used for determining bouces
            horizontal : y1 === y2 ? true : false,

            //Instance methods
            draw : function(){
                //Draw the obstacle
                context.beginPath();
                context.moveTo(x1, y1);
                context.lineTo(x2, y2);
                context.stroke();
            },

            checkBulletCollision : function(bullet){
                //Has 'bullet' hit this wall?
                var data = bullet.getMovementData();
                var pos = null;
                if(this.horizontal && data.x >= this.x1 && data.x <= this.x2){
                    //Check the y coords
                    if(data.y >= this.y1 && data.y + data.yChange < this.y1){
                        //Moving up, hit bottom of wall
                        pos = this.y1;
                    }
                    else if(data.y + bulletSize <= this.y1
                        && data.y + bulletSize + data.yChange > this.y1){
                        //Moving down, hit top of wall
                        pos = this.y1 - bulletSize;
                    }
                }
                else if(!this.horizontal && data.y >= this.y1
                    && data.y <= this.y2){
                    //Check the x coords
                    if(data.x >= this.x1 && data.x + data.xChange < this.x1){
                        //Moving left, hit right of wall
                        pos = this.x1;
                    }
                    else if(data.x + bulletSize <= this.x1
                        && data.x + bulletSize + data.xChange > this.x1){
                        //Moving right, hit left of wall
                        pos = this.x1 - bulletSize;
                    }
                }
                if(pos !== null){
                    bullet.collision(this.horizontal, pos);
                }
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
        //Calculate the coordinates of the mouse click with regard to canvas
        var x = e.pageX - canvas.offsetLeft;
        var y = e.pageY - canvas.offsetTop;
        return {
            x : x,
            y : y
        }
    }

    //Running Code / Game Methods
    window.addEventListener('DOMContentLoaded', init, false);

    //Game initialisation
    function init(){
        //Initialise global variables
        canvas = document.querySelector('canvas');
        context = canvas.getContext('2d');
        height = canvas.height;
        width = canvas.width;
        displayRows = $('tbody tr');

        //Create obstacles
        createObstacles();

        //Query for new players every .1s until game is ready
        updateInterval = window.setInterval(readyGame, 100);
    }

    function readyGame(){
        if(ready){
            clearInterval(updateInterval);
            //Set up game
            startGame();
        }
        else{
            //Query for initial player data
            playersSetup();
        }
    }

    function startGame(){
        //Run the ajax update every 16ms, just before the update method
        ajaxInterval = window.setInterval(updatePlayers, 16);
        //Run the countdown and then start the game
        updateInterval = setInterval(countdown, 1000);
    }

    function countdown(){
        //Display the countdown and when the countdown hits 0, start the game
        if(countdownTimer > 0){
            context.clearRect(0, 0, width, height);
            context.font = '50px Verdana';
            context.textAlign = 'center';
            context.fillText(countdownTimer, (width / 2), (height / 2));
            countdownTimer --;
        }
        else{
            //Remove old updateInterval
            clearInterval(updateInterval);
            //Add event listeners
            canvas.addEventListener('click', playerFire, false);
            window.addEventListener('keydown', playerMove, false);
            window.addEventListener('keyup', playerStop, false);
            //We're gonna try and run this game at 60fps (16ms)
            //If the ajax can't keep up, lower to 30fps (33ms)
            updateInterval = window.setInterval(update, 16);
        }
    }

    //Obstacle creation
    function createObstacles(){
        //Later on will be sent by JSON from pre-designed maps
        //For now, hard code and test bouncing

        // context.beginPath();
        // context.moveTo(width/2, height/2);
        // context.lineTo(width/8, height/2);
        // context.stroke();
        obstacles.push(
            new Obstacle(width/8, height/2, width/2, height/2));

        // context.beginPath();
        // context.moveTo(width/2, height/2);
        // context.lineTo((7 * width/8), height/2);
        // context.stroke();
        obstacles.push(
            new Obstacle(width/2, height/2, (7 * width)/8, height/2));

        // context.beginPath();
        // context.moveTo(width/2, 0);
        // context.lineTo(width/2, (3 * height)/8);
        // context.stroke();
        obstacles.push(
            new Obstacle(width/2, 0, width/2, (3 * height)/8));

        // context.beginPath();
        // context.moveTo(width/2, height);
        // context.lineTo(width/2, (5*height)/8);
        // context.stroke();
        obstacles.push(
            new Obstacle(width/2, (5 * height)/8, width/2, height));
    }

    //Player data handlers
    function updatePlayers(){
        //Pull data from the server and put it into the players list
    }

    function playersSetup(){
        //In the MP version, read in POST data and populate players accordingly
        //In SP, just creates players for testing
        $.ajax({
            url: 'cgi-bin/single-player.py',
            dataType : 'json',
            //Only run method if new player has entered the lobby
            ifModified : true,
            data : {
                width : width,
                height : height
            },
            success : function(json){
                //Update the players array with the json data
                json.players.forEach(function(player, index){
                    players[index] = new Player(
                        player.x, player.y, index, player.colour, player.userName);
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
                //Check if the game is ready
                ready = json.ready;
                //Update the displays with health and bullets
                updateDisplays();
            }
        });
    }

    //Game loop methods
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
        obstacles.forEach(function(obstacle, index){
            obstacle.draw();
        });
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

    //Control methods
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

    //Game state methods
    function isGameOver(){
        if(playersAlive === 1){
            gameOver();
        }
    }

    function gameOver(){
        clearInterval(updateInterval);
        context.clearRect(0, 0, width, height);
        clearInterval(ajaxInterval);
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
