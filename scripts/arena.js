/*
Script: Arena
JavaScript client code that runs in browser. Handles drawing of objects and, using AJAX,
handles updating data by sending and receiving from the <Server>
*/
(function(){
    //Section: Global Variables

    //Group: Game Set Up Variables

    //boolean: ready
    //False until all players are ready
    var ready = false;

    //int: countdownTimer
    //Number of seconds between game ready and game start
    var countdownTimer = 3;
    
    //Group: HTML Element Variables

    //obj: canvas
    //HTML5 canvas for drawing the game on
    var canvas;

    //obj: context
    //Context object used for drawing on the canvas
    var context;

    //int: height
    //Height of the canvas; used for drawing
    var height;

    //int: width
    //Width of the canvas; used for drawing
    var width;

    //array: displayRows
    //An array of table rows in the scoreboard table; used for updating displays
    var displayRows = [];

    //Group: Bullet Constant Variables

    //int: bulletSize
    //Size of a <Bullet> in pixels
    var bulletSize = 5;

    //int: bulletSpeed
    //The number of pixels a <Bullet> moves per frame
    var bulletSpeed = 25;

    //int: maxBounces
    //The maximum number of times a <Bullet> may bounce off of walls / <Obstacle>s
    var maxBounces = 3;

    //int: maxDamage
    //The maximum number of damage a <Bullet> can deal to a <Player>
    var maxDamage = 10;

    //Group: Player Constant Variables

    //int: playerSize
    //Size of the <Player>s in pixels
    var playerSize = 20;

    //int: playerSpeed
    //The number of pixels a <Player> will move in a direction per frame
    var playerSpeed = 4;

    //int: maxBullets
    //The maximum number of bullets a <Player> is allowed to have
    var maxBullets = 3;

    //Group: Player Management Variables

    //array: players
    //Array of all the <Player>s in the game
    var players = [null, null, null, null];

    //int: local
    //The index of the local <Player> in the list; used for updating the local player's data
    var local;

    //obj: move
    //A JavaScript object used for maintaining information on which way(s) the local <Player> is trying to move
    var move = {
        up : false,
        down : false,
        left : false,
        right : false
    };

    //Group: Obstacle Management Variables

    //array: obstacles
    //An array of all <Obstacle> objects on the map
    var obstacles = [];

    //Group: Game Control Variables

    //string: server
    //URL of the server
    var server;

    //int: updateInterval
    //The id of the <Interval>(s) used for running methods updating the canvas / game state
    var updateInterval;

    //int: ajaxInterval
    //The id of the <Interval>(s) used for making periodic ajax requests to the server
    var ajaxInterval;

    //int: playersAlive
    //The number of <Player>s who remain alive
    var playersAlive = 4;

    /*
        Class: Bullet
        A Bullet is fired by a <Player>, bounces off walls and damages Players other than the one who fired it

        Group: Constructors

        Constructor: Bullet
        Constructs a new Bullet instance

        Parameters:
            int x - The x coordinate of the bullet upon creation
            int y - The y coordinate of the bullet upon creation
            int owner - The index of the <Player> who fired the bullet in <players>
            int number - The index of the bullet inside its owner's <Player.bullets> array
    */
    function Bullet(x, y, owner, number){
        return {
            //Group: Variables

            //int: size
            //Size of this Bullet (should deprecate)
            size : bulletSize,

            //int: x
            //x coordinate of the top-left corner of this Bullet
            x : x - (bulletSize / 2),

            //int: y
            //y coordinate of the top-left corner of this Bullet
            y : y - (bulletSize / 2),

            //int: speed
            //Number of pixels this Bullet moves per frame
            speed : bulletSpeed,

            //int: xChange
            //Number of pixels this Bullet will move in the x-axis in the next frame
            xChange : 0,

            //int: yChange
            //Number of pixels this Bullet will move in the y-axis in the next frame
            yChange : 0,

            //int: bounces
            //The number of bounces this Bullet has remaining
            bounces : maxBounces,

            //int: owner
            //The index of the <Player> who fired this bullet in <players>
            owner : owner,

            //int: number
            //The index of this Bullet inside the owner's <Player.bullets> array
            number : number,

            //Group: Methods
            /*
                Function: getMovementData
                Getter for all movement data for this Bullet

                Returns:
                    obj data - Javascript object containing this Bullet's <x>, <y>, <xChange> and <yChange> values
            */
            getMovementData : function(){
                return {
                    x : this.x,
                    y : this.y,
                    xChange : this.xChange,
                    yChange : this.yChange
                }
            },

            /*
                Function: getDamage
                Getter for the damage dealt by this Bullet

                Returns:
                    int damage - Damage dealt by this Bullet on collision with a player
            */
            getDamage : function(){
                var damage = maxDamage;
                for(var i = 0; i < (maxBounces - this.bounces); i ++){
                    damage *= 0.8;
                }
                return damage;
            },

            /*
                Function: draw
                Draw this Bullet, check collisions, and update positions
            */
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

            /*
                Function: checkWalls
                Checks if this Bullet has collided with a wall or obstacle
            */
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

            /*
                Function: checkPlayers
                Checks if the Bullet has collided with a Player other than its owner
            */
            checkPlayers : function(){
                //Check if the bullet has hit a player, and if it has,
                //send a call to that player saying it's been hit
                for(var i = 0; i < players.length; i ++){
                    if(i !== local){
                        var player = players[i];
                        if(player !== null && player.isAlive() && collisionBetween(this, player)){
                            this.destroy(i);
                            break;
                        }
                    }
                }
            },

            /*
                Function: collision
                Handles bouncing of this Bullet

                Parameters:
                    boolean horizontal - Is the wall the Bullet hit horizontal or vertical
                    int pos - the value that the coordinate that should be changed should be changed to
            */
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

            /*
                Function: destroy
                Handles destruction of a Bullet, when it hits a player or bounces too many times

                Parameters:
                    int hitPlayer - index of the <Player> that was hit by this Bullet in <players>
            */
            destroy : function(hitPlayer){
                //Remove this bullet from it's player's list
                //Specify the player that it hit, let the update method
                //remove it afterwards
                var bullet = this;
                players[this.owner].bullets[this.number] = {
                    owner : bullet.owner,
                    number : bullet.number,
                    hitPlayer : hitPlayer,
                    damage : bullet.getDamage()
                }
                //This will be used to update the players when they get hit
            },

            /*
                Function: fire
                Set this Bullet's <xChange> and <yChange> when it is fired

                Parameters:
                    obj coords - JavaScript object containing the x and y coordinates of the mouse click
            */
            fire : function(coords){
                //Get the angle of motion for the bullet and set it moving
                var a = this.getAngle(
                    coords.x,
                    coords.y);
                this.xChange = this.speed * Math.cos(a);
                this.yChange = this.speed * Math.sin(a) * -1;
            },

            /*
                Function: getAngle
                Calculate the angle of travel for the Bullet

                Parameters:
                    int destinationX - x coordinate of mouse click
                    int destinationY - y coordinate of mouse click

                Returns:
                    int angle - The angle in radians this Bullet should travel
            */
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

    /*
        Class: Player
        Objects representing the player controlled entity in the game

        Group: Constructors
            
        Constructor: Player
        Construct a new Player instance

        Parameters:
            int x - x coordinate of the top left corner of this Player
            int y - y coordinate of the top left corner of this Player
            int index - Index of this Player in <players>
            string colour - A hex code string representing the colour of this Player
            string userName - The user name of the player controlling this Player
    */
    function Player(x, y, index, colour, userName){
        return {
            //Group: Variables

            //int: size
            //Size of this Player in pixels (should deprecate)
            size : playerSize,
            
            //int: x
            //x coordinate of the top left corner of this Player
            x : x - (playerSize / 2),

            //int: y
            //y coordinate of the top left corner of this Player
            y : y - (playerSize / 2),

            //int: xChange
            //The amount of pixels this Player will move in the x axis in the next frame
            xChange : 0,

            //int: yChange
            //The amount of pixels this Player will move in the y axis in the next frame
            yChange : 0,

            //float: health
            //The current health of this Player
            health : 100.00,

            //array: bullets
            //An array maintaining the <Bullet> objects this Player has fired that are still alive
            bullets : [null, null, null],

            //int: numBullets
            //The number of bullets this Player can still fire
            numBullets : maxBullets,

            //int: id
            //The index of this Player in <players>
            id : index,

            //string: colour
            //The colour of this Player
            colour : colour,

            //string: userName
            //The username of the player controlling this Player
            userName : userName,

            //boolean: alive
            //True as long as this Player's health is above 0
            alive : true,

            //int: damage
            //The damage this Player still needs to take; to be used for passing damage data through the network
            damage : null,

            //Group: Methods
            /*
                Function: getHealth
                Getter for this Player's current <health>

                Returns:
                    int health - This Player's current <health>
            */
            getHealth : function(){
                //Public getter for health
                return this.health;
            },

            /*
                Function: getBullets
                Getter for this Player's current <numBullets>

                Returns:
                    int bullets - This Player's current <numBullets>
            */
            getBullets : function(){
                //Public getter for numBullets
                return this.numBullets;
            },

            /*
                Function: getUserName
                Getter for this Player's <userName>

                Returns:
                    string userName - This Player's <userName>
            */
            getUserName : function(){
                //Public getter for userName
                return this.userName;
            },

            /*
                Function: getHealth
                Getter for whether or not this Player is still alive

                Returns:
                    boolean alive - True if this Player is still alive
            */
            isAlive : function(){
                //Public getter for Alive state
                return this.alive;
            },

            /*
                Function: getMovementData
                Getter for this Player's current movement data

                Returns:
                    obj data - Javascript object containing this Players's <x>, <y>, <xChange> and <yChange> values
            */
            getMovementData : function(){
                //Public getter for position
                return {
                    x : this.x,
                    y : this.y,
                    xChange : this.xChange,
                    yChange : this.yChange,
                }
            },

            /*
                Function: setX
                Setter for this Player's <x> coordinate

                Parameters:
                    int x - The new value of this Player's <x> coordinate
            */
            setX : function(x){
                //Public setter for this.x
                this.x = x;
            },

            /*
                Function: setY
                Setter for this Player's <y> coordinate

                Parameters:
                    int y - The new value of this Player's <y> coordinate
            */
            setY : function(y){
                //Public setter for this.y
                this.y = y;
            },

            /*
                Function: move
                Handler for the movement of this Player

                Parameters:
                    KeyboardEvent e - The <KeyboardEvent> passed to this function from <Game Code.playerMove>
            */
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

            /*
                Function: stop
                Handler for stopping the movement of this Player

                Parameters:
                    KeyboardEvent e - The <KeyboardEvent> passed to this function from <Game Code.playerStop>
            */
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

            /*
                Function: draw
                Draw this Player, handle collisions, update this Player's position, and draw each of this Player's <Bullet>s
            */
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
                var player = this;
                this.bullets.forEach(function(bullet, index){
                    if(bullet !== null){
                        if(bullet.hasOwnProperty('hitPlayer')){
                            player.bulletDestroyed(bullet.number);
                        }
                        else{
                            bullet.draw();
                        }
                    }
                });
                //Now test for bullet collisions
                this.updateHealth();
            },

            /*
                Function: fireBullet
                Handles firing of a new <Bullet>

                Parameters:
                    obj coords - JavaScript object containing the coords of the mouse click
            */
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

            /*
                Function: bulletDestroyed
                Handler for removing a <Bullet> from this Player's <bullets> array

                Parameters:
                    int number - Index of the <Bullet> to be removed
            */
            bulletDestroyed : function(number){
                //this.bullets[number] has been destroyed
                console.log(this.bullets[number]);
                this.bullets[number] = null;
                this.numBullets += 1;
                //Error checking
                if(this.numBullets > 3){
                    this.numBullets = 3;
                }
            },

            /*
                Function: wallCollision
                Checks if this Player has hit a wall and prevent it from moving off the board if so
            */
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

            /*
                Function: hit
                Handler for when this Player gets hit by another Player's <Bullet>

                Parameters:
                    Bullet bullet - The <Bullet> object that hit this Player
            */
            hit : function(bullet){
                //Player hit by bullet, subtract health accordingly
                var damage = bullet.damage;
                this.damage = damage;
            },

            /*
                Function: updateHealth
                Handles updating of this Player's <health> using this Player's <damage> variable
            */
            updateHealth : function(){
                //Handles health management
                if(this.damage !== null){
                    this.health = (this.health - this.damage).toFixed(2);
                    if(this.health <= 0){
                        this.destroy();
                    }
                    this.damage = null;
                }
            },

            /*
                Function: destroy
                Handler for the death of this Player object
            */
            destroy : function(){
                this.alive = false;
                playersAlive -= 1;
            },

            /*
                Function: update
                Update this Player with the data received from the server

                Parameters:
                    obj data - JavaScript object containing all of this Player's updated variables from the server
            */
            update : function(data){
                //Update this player with the data that was sent
                var oldHealth = this.health;
                $.extend(this, data);
                if(oldHealth < this.health){
                    this.health = oldHealth;
                }
                //Update bullets for this player
                var player = this;
                data.bullets.forEach(function(bullet, index){
                    if(bullet !== null){
                        if(bullet.hasOwnProperty('hitPlayer')){
                            players[bullet.hitPlayer].hit(bullet);
                            players[bullet.owner].bulletDestroyed(bullet.number);
                        }
                        else{
                            var newBullet = new Bullet(
                                bullet.x, bullet.y, player.id, index);
                            newBullet.xChange = bullet.xChange;
                            newBullet.yChange = bullet.yChange;
                            player.bullets[index] = newBullet;
                        }
                    }
                });
            },

            /*
                Function: updateLocal
                Updates the local Player with data from the server

                Parameters:
                    obj data - JavaScript object containing all of the local Player's updated variables from the server
            */
            updateLocal : function(data) {
                //Update health and stuff
                if(this.health > data.health){
                    this.health = data.health;
                }
            }
        }
    }

    /*
        Class: Obstacle
        Objects representing the walls in the map, that <Bullet>s bounce off of and <Player>s pass through.

        Group: Constructors

        Constructor: Obstacle
        Construct a new Obstacle instance

        Parameters:
            int x1 - x coordinate of the start of this Obstacle
            int y1 - y coordinate of the start of this Obstacle
            int x2 - x coordinate of the end of this Obstacle
            int y2 - y coordinate of the end of this Obstacle

        Notes:
            (x1, y1) should be closer to (0, 0) than (x2, y2)

            As of v1.0a, Obstacles are only straight lines, meaning x1 == x2 || y1 == y2
    */
    function Obstacle(x1, y1, x2, y2){
        //Create an obstacle which will be drawn as a straight line
        //Allow for only straight lines to begin
        //When creating obstacles, make sure that (x1, y1) is closer to (0, 0)
        return {
            //Group: Variables

            //int: x1
            //x coordinate of the start of this Obstacle
            x1 : x1,

            //int: y1
            //y coordinate of the start of this Obstacle
            y1 : y1,

            //int: x2
            //x coordinate of the end of this Obstacle
            x2 : x2,

            //int: y2
            //y coordinate of the end of this Obstacle
            y2 : y2,
            
            //boolean: horizontal
            //True if <y1> == <y2>; used for determining <Bullet> bounces
            horizontal : y1 === y2 ? true : false,

            //Group: Methods

            /*
                Function: draw
                Draw this Obstacle
            */
            draw : function(){
                //Draw the obstacle
                context.beginPath();
                context.moveTo(x1, y1);
                context.lineTo(x2, y2);
                context.stroke();
            },

            /*
                Function: checkBulletCollision
                Check if this Obstacle has been hit by a <Bullet> object

                Parameters:
                    Bullet bullet - The <Bullet> to be checked against this Obstacle
            */
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

    //Section: Helper Functions

    /*
        Function: collisionBetween
        Checks for a collision between two objects

        Parameters:
            obj obj1 - First object to be checked
            obj obj2 - Second object to be checked

        Returns:
            True if obj1 and obj2 have collided, otherwise False
    */
    function collisionBetween(obj1, obj2){
        //Check if obj1 and obj2 have collided
        if((obj1.x + obj1.size) < obj2.x || obj1.x > (obj2.x + obj2.size)
            || (obj1.y + obj1.size) < obj2.y || obj1.y > (obj2.y + obj2.size)){
            return false;
        }
        return true;
    }

    /*
        Function: getMouseCoords
        Get the coordinates inside the canvas of a mouse click on the canvas

        Parameters:
            MouseEvent e - The <MouseEvent> passed to this function from the mouse

        Returns:
            obj coords - JavaScript object containing the x and y coordinates of the click
    */
    function getMouseCoords(e){
        //Calculate the coordinates of the mouse click with regard to canvas
        var x = e.pageX - canvas.offsetLeft;
        var y = e.pageY - canvas.offsetTop;
        return {
            x : x,
            y : y
        }
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

    //Section: Game Code
    window.addEventListener('DOMContentLoaded', init, false);

    /*
        Function: init
        Initialise all the global variables.

        Called on _'DOMContentLoaded'_ event
    */
    function init(){
        //Initialise global variables
        canvas = document.querySelector('canvas');
        context = canvas.getContext('2d');
        height = canvas.height;
        width = canvas.width;
        displayRows = $('tbody tr');
        server = 'http://' + getCookie('game_address');

        //Create obstacles
        createObstacles();

        //Query for new players every .1s until game is ready
        updateInterval = window.setInterval(readyGame, 100);
    }

    /*
        Function: readyGame
        Checks if the game is ready to be played.

        If so, starts the game. Else, queries the server again
    */
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

    /*
        Function: startGame
        Starts the running of the game.

        Calls <updatePlayers>, and initialises an <Interval> to call <countdown> every second
    */
    function startGame(){
        //Run the ajax update every 16ms, just before the update method
        // ajaxInterval = window.setInterval(updatePlayers, 16);
        updatePlayers(); //Will call itself after success, or after 1 second on failure
        //Run the countdown and then start the game
        updateInterval = setInterval(countdown, 1000);
    }

    /*
        Function: countdown
        Displays a countdown on the canvas for <countdownTimer> seconds before starting the game.

        To start the game, an <Interval> is set to call <update> every 16 milliseconds, and the Interval calling countdown is removed
    */
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

    /*
        Function: createObstacles
        Create some <Obstacle>s for the default map
    */
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

    /*
        Function: updatePlayers
        Sends the local <Player> data to the server, receives the updated data for all Players and updates each Player accordingly
    */
    function updatePlayers(){
        //Pull data from the server and put it into the players list
        $.ajax({
            url: server,
            dataType: 'json',
            type: 'POST',
            data: {
                update: JSON.stringify(players[local])
            },
            ifModified : 'true',
            success: function(json){
                // TODO - Update the players list
                json.players.forEach(function(player){
                    var index = player.id;
                    if(index !== local){
                        players[index].update(player);
                    }
                    else{
                        players[index].updateLocal(player);
                    }
                });
                updatePlayers();
            },
            error: function(req, text){
                console.log('update ' + req.responseText);
                console.log('update ' + text);
                window.setTimeout(updatePlayers, 1000);
            }
        });
    }

    /*
        Function: playersSetup
        Get the lobby data from the server for all the players in the game, create new <Player> objects using that data and populate <players> with these objects
    */
    function playersSetup(){
        //In the MP version, read in POST data and populate players accordingly
        //In SP, just creates players for testing
        $.ajax({
            url: server,
            dataType : 'json',
            type: 'POST',
            data : {
                start_up : getCookie('player_num')
            },
            ifModified: 'true',
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
                    if(player !== null && player.isAlive()){
                        var row = $(displayRows[player.id]);
                        row.css({'color': player.colour});
                        row.find('.name-container').html(player.getUserName());
                    }
                });
                //Check if the game is ready
                ready = json.ready;
                //Update the displays with health and bullets
                updateDisplays();
            },
            error: function(req, text){
                console.log('setup ' + req.responseText);
                console.log('setup ' + text);
            }
        });
    }

    //Game loop methods

    /*
        Function: update
        The main game loop.

        First checks if the game is over using <isGameOver>.

        If not, it updates the scoreboard with <updateDisplays>, and draws all the objects on
        screen with <draw>
    */
    function update(){
        //Main Game Loop
        //Check if game is over
        isGameOver();
        //If it's not, update the field
        updateDisplays();
        draw();
    }

    /*
        Function: draw
        Clears the canvas, the sends calls to each <Obstacle> and <Player> object in 
        <obstacles> and <players> respectively, asking them to draw themselves.

        As we see in <Player.draw>, each Player handles the drawing of their <Bullet>s
    */
    function draw(){
        context.clearRect(0, 0, width, height);
        //Draw the walls
    	context.strokeStyle = 'blue';
        obstacles.forEach(function(obstacle, index){
            obstacle.draw();
        });
        //Draw the players, which draw their own bullets
        players.forEach(function(player, index){
            if(player !== null && player.isAlive()){
                player.draw();
            }
        });
    }

    /*
        Function: updateDisplays
        Updates the scoreboard with <Player>'s health and bullet counts
    */
    function updateDisplays(){
        //Ensure the displays are up to date
        players.forEach(function(player, index){
            if(player !== null){
                var health = player.isAlive() ? player.getHealth() : 0;
                var row = $(displayRows[player.id]);
                row.find('.health-container').html(health);
                row.find('.bullets-container').html(player.getBullets());
            }
        });
    }

    //Control methods

    /*
        Function: playerFire
        Extracts the coordinates of the mouse click and passes them to <Player.fireBullet>

        Parameters:
            MouseEvent e - The <MouseEvent> passed to this function from the mouse

        Note:
            Called by a _'click'_ event.
    */
    function playerFire(e){
        //Wrapper for player.fireBullet
        var coords = getMouseCoords(e);
        players[local].fireBullet(coords);
    }

    /*
        Function: playerMove
        Wrapper for <Player.move>

        Parameters:
            KeyboardEvent e - The <KeyboardEvent> passed to this function from the keyboard

        Note:
            Called by a _'keydown'_ event.
    */
    function playerMove(e){
        //Wrapper for player.move
        players[local].move(e);
    }

    /*
        Function: playerStop
        Wrapper for <Player.stop>

        Parameters:
            KeyboardEvent e - the <KeyboardEvent> passed to this function from the keyboard

        Note:
            Called by a _'keyup'_ event.
    */
    function playerStop(e){
        //Wrapper for player.stop
        players[local].stop(e);
    }

    //Game state methods

    /*
        Function: isGameOver
        Checks to see if only one <Player> is alive. If so, runs <gameOver>
    */
    function isGameOver(){
        if(playersAlive === 1){
            gameOver();
        }
    }

    /*
        Function: gameOver
        Clears all <Interval>s in use, and alerts all players of the winner
    */
    function gameOver(){
        clearInterval(updateInterval);
        context.clearRect(0, 0, width, height);
        clearInterval(ajaxInterval);
        //Get the remaining player
        var player;
        for(var i = 0; i < players.length; i ++){
            if(players[i] !== null && players[i].isAlive()){
                player = players[i];
            }
        }
        window.alert('Game Over! Winner: ' + player.getUserName());
    }

}());
