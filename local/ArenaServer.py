from base64 import b64encode
from datetime import datetime
from hashlib import sha256, sha1
from json import dumps, loads
import os
from random import choice
from select import select
from socket import *
from threading import Thread, Timer

"""/*
    Class: ArenaServer
    A custom server written in Python3.4 for use as the backend for this game.

    Multithreaded for increased speed, especially during the actual game.

    Uses a simple protocol for messages to / from the server.

    Protocol:
        _While the server is in the lobby state (game hasn't started)_

        (start table)
        join=[name] - Adds a new player to the lobby with the name *name*.
                      Handled by <_lobbyJoin>

        query=[player_num] - Retrieve the current status of the lobby,
                             refreshing the timeout for player
                             *player_num* in the process.
                             Handled by <_lobbyQuery>

        token=[player_num] - Retrieve the token for player *player_num*,
                             if pre-existing arena cookies are discovered
                             on the browser.
                             Handled by <_lobbyGetToken>

        quit=[player_num]  - Remove the player *player_num* from the lobby
                             when they leave the page.
                             Handled by <_lobbyQuit>

        start=[player_num] - Starts the game, moving the server to the
                             game loop. Checks that player *player_num* is
                             the host first.
                             Handled by <_lobbyStart>
        (end table)

        _While the server is in the game state (game has started)_

        (start table)
        startUp=[player_num] - Retrieve the player data to convert it into
                                <Player> objects in the JavaScript.
                                Handled by <_gameStartUp>

        update=[player_num] - Send in the local player's data, and retrieve
                              data on all players from the server.
                              Handled by <_gameUpdate>

        gameOver - Report to the server that the game is over.
                   Handled by <_gameOver>

        quit=[player_num] - Report that player *player_num* has left the
                            game. Set their health to 0 and allow the other
                            clients to update themselves.
                            Handled by <_gameQuit>
        (end table)
*/"""
class ArenaServer:

    """/*
        Group: Class Constants
        Constant values required for this class
    */"""

    """/*
        var: WSGUID
        The GUID required for WebSocket handshakes
    */"""
    WSGUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    """/*
        var: WSHEADERS
        The headers to be sent back to a handshaking WebSocket, with a hole for the auth key
    */"""
    WSHEADERS = ("HTTP/1.1 101 Switching Protocols\r\n"
                 "Upgrade: websocket\r\nConnection: upgrade\r\n"
                 "Sec-WebSocket-Accept: %s\r\n"
                 "Sec-WebSocket-Protocol: exvo-arena\r\n\r\n")

    """/*
        Group: Constructors
    */"""

    """/*
        Constructor: __init__
        Initialises the server and binds it to the host and port specified

        Parameters:
            int port - The port that the server will listen on
            func log - A function to log messages into the <LogPanel>
            func callback - A function to be called when the server closes
            str password - A password for the server. Defaults to None
    */"""
    def __init__(self, port=44444, log=print, callback=lambda x: x, password=None):
        """/*
            Group: Server Socket Variables
                Variables maintaining the state of the socket the server
                listens on
        */"""

        """/*
            var: host
            The address of the host.
        */"""
        self.host = 'localhost'

        """/*
            var: port
            The port number the socket will bind to.
        */"""
        self.port = port

        sock = socket()
        sock.setblocking(0)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind(('', self.port))

        """/*
            var: sock
            The <Socket> the server listens on
        */"""
        self.sock = sock

        """/*
            Group: Server State Variables
                Variables maintaining the state of the server

                These variables are used to control to movement of the server
                from one state to another (excluding <password>)
        */"""

        """/*
            var: password
            Password for the server
        */"""
        self.password = None
        if password:
            self.password = sha256(password.encode()).hexdigest()

        """/*
            var: hostStart
            False until the host clicks the Start Game button.
        */"""
        self.hostStart = False

        """/*
            var: started
            False while the server is still in the lobby, True once game starts
        */"""
        self.started = False

        """/*
            var: gameOver
            Flag for whether the game has ended or not
        */"""
        self.gameOver = False

        """/*
            var: closed
            True iff the server GUI called <ArenaGUI._close>
        */"""
        self.closed = False

        """/*
            var: closing
            True when the <close> method is called.
        */"""
        self.closing = False

        """/*
            var: canStartUp
            Dict of player's usernames to a flag stating whether they can
            run the start up method. This will be true until the player runs
            the update method
        */"""
        self.canStartUp = {}

        """/*
            Group: Stats Variables
                Variables for maintaining data used by <_generateStatsFile>
                once the game is over
        */"""

        """/*
            var: startTime
            The time at which the game starts
        */"""
        self.startTime = 0

        """/*
            var: playerStats
            An ordered array of the players who died, in order
        */"""
        self.playerStats = []

        """/*
            Group: Lobby Variables
                Variables for maintaining lobby state
        */"""

        """/*
            var: lobbySize
            The amount of players currently in the lobby
        */"""
        self.lobbySize = 0

        """/*
            var: players
            Array of player JSON objects in the lobby
        */"""
        self.players = [None, None, None, None]

        """/*
            var: tokens
            Dict of usernames against their tokens
        */"""
        self.tokens = {}

        """/*
            var: playerStatus
            Dict of indices against a flag indicating whether the player is
            still in game.
            The flags will be set to True in the gameUpdate and lobbyQuery
            functions, and set to false in the checkTimeout function

            Note:
                Uses the indices in self.players, meaning the indices in
                self.playerObjects may not work
        */"""
        self.playerStatus = {}

        width = height = 650

        """/*
            var: coords
            Array of (x, y) coordinate pairs players can spawn in
        */"""
        self.coords = [
            (width / 4, height / 4),
            ((3 * width) / 4, height / 4),
            (width / 4, (3 * height) / 4),
            ((3 * width) / 4, (3 * height) / 4)
        ]

        """/*
            Group: Game Variables
                Variables for maintaining game state
        */"""

        """/*
            var: playerObjects
            Array of the <Player> objects created in Javascript for all
            players in the game

            Note:
                They are <Player> objects in JavaScript, but Python stores them
                as dicts
        */"""
        self.playerObjects = [None, None, None, None]

        """/*
            var: playerSockets
            Map of socket objects related to the clients currently connected to the game mapped to the id of the player
            that the socket is used by
        */"""
        self.playerSockets = {}

        """/*
            var: damages
            Dict of player indices to damage objects they have received since
            they last updated
        */"""
        self.damages = {}

        """/*
            Group: External Methods
                Methods passed into the constructor from the GUI elements
        */"""

        """/*
            var: log
            Callable passed from the GUI to handle message outputs
        */"""
        self.log = log

        """/*
            var: callback
            Callback method to be run when a service closes down
        */"""
        self.callback = callback

        """/*
            var: timeoutTimer
            Pointer to a Timer object that controls the periodic timeout
            checking
        */"""
        self.timeoutTimer = Timer(5, self._checkTimeouts)

    """/*
        Group: Static Helper Methods
        Helper methods for the server that do not rely on any instance data
    */"""

    """/*
        Function: _generateColour
        Generate a random colour for a player

        Returns:
            string colour - Random 6-digit hexadecimal string representing a
                            colour value
    */"""
    def _generateColour():
        return ''.join([choice('0123456789ABCDEF') for _ in range(6)])

    """/*
        Group: WebSocket Handler Methods
        Methods that control the handling of WebSockets
    */"""

    """/*
        Function: _wsHandshake
        Performs the handshaking operation with the passed socket

        Parameters:
            socket client - The socket object from which the handshaking request was received
    */"""
    def _wsHandshake(self, client):
        clientHand = client.recv(4096).decode()
        try:
            protocol, playerNum = clientHand.split("Sec-WebSocket-Protocol: ")[-1].split('\r\n')[0].split(', ')
            playerNum = int(playerNum)
            if protocol == 'exvo-arena' and self.players[playerNum] is not None:
                print('Handshake request from player', playerNum)
                auth_key = clientHand.split("Sec-WebSocket-Key: ")[-1].split('\r\n')[0]
                auth_key += ArenaServer.WSGUID
                auth_key = b64encode(sha1(auth_key.encode()).digest()).decode()
                hand_of_python = ArenaServer.WSHEADERS % (auth_key,)
                client.sendall(hand_of_python.encode())
                self.playerSockets[client] = playerNum
            else:
                raise ValueError("Invalid Protocol from websocket")
        except ValueError:
            self.log("Invalid WebSocket connection received")
    """/*
        Function: _wsEncode
        Encodes the passed string into a WebSocket frame and returns the byte string generated
        Static Method

        Parameters:
            string payload - The string to be sent to the client

        Returns:
            bytes frame - The WebSocket Frame to be sent to the client
    */"""
    def _wsEncode(payload):
        frame = bytearray([129])
        dataLength = len(payload)

        if dataLength <= 125:
            frame.append(dataLength)
        elif 126 <= dataLength <= 65535:
            frame.extend([
                126,
                (dataLength >> 8) & 255,
                dataLength & 255
            ])
        else:
            frame.extend([
                127,
                (dataLength >> 56) & 255,
                (dataLength >> 48) & 255,
                (dataLength >> 40) & 255,
                (dataLength >> 32) & 255,
                (dataLength >> 24) & 255,
                (dataLength >> 16) & 255,
                (dataLength >> 8) & 255,
                dataLength & 255
            ])
        frame.extend(payload.encode())
        return bytes(frame)

    """/*
        Function: _wsDecode
        Decodes the passed websocket and returns the decoded payload
        Static Method

        Parameters:
            bytes frame - The websocket frame to be decoded

        Returns:
            string payload - The payload contained within the frame
    */"""
    def _wsDecode(frame):
        frame = bytearray(frame)
        length = frame[1] & 127
        maskStart = 2
        if length == 126:
            maskStart = 4
        elif length == 127:
            maskStart = 10
        dataStart = maskStart + 4
        mask = frame[maskStart:dataStart]
        i = dataStart
        j = 0
        payload = []
        while i < len(frame):
            payload.append(frame[i] ^ mask[j % 4])
            i += 1
            j += 1
        return "".join(chr(byte) for byte in payload)

    """/*
        Group: Server Handler Methods
        Handlers for running and closing of the server
    */"""

    """/*
        Function: close
        Closes the server and releases the socket.
        Should only be able to be called while the server is in the lobby state
    */"""
    def close(self):
        self.log('Server Closing')
        self._endBroadcast()
        self.closed = True
        self.closing = True
        self.started = True
        self.sock.close()

    """/*
        Function: inGame
        Reports whether or not the game this server manages has started

        Returns:
            boolean started - True if the host has started this game
    */"""
    def inGame(self):
        return self.started and not self.gameOver

    """/*
        Function: listen
        Listen for incoming connections and pass them off to the handler methods
        in a new thread
    */"""
    def listen(self):
        self.log(
            'Server starting up at %s on port %s' % (self.host, self.port))
        self.log('Password Protected: ' + str(self.password is not None))
        self.sock.listen()
        self.log('Lobby Open')

        # Run the broadcast
        self._broadcast()

        # Start the timeout checking
        self.timeoutTimer.start()
        # Lobby loop
        try:
            while not self.started:
                connections, wlist, xlist = select([self.sock], [], [], 0.05)

                for connection in connections:
                    client, address = connection.accept()
                    client.settimeout(5)
                    Thread(
                        target=self._handleLobbyConnection,
                        args=(client, address)
                    ).start()

            # End the broadcast as it's not needed
            self._endBroadcast()

            # Cancel the timer
            self.timeoutTimer.cancel()

            if not self.closed:
                # Handshake phase
                self.log("Awaiting handshakes from all players")
                playersInGame = len(list(filter(None, self.players)))
                iterations = 0
                print("Waiting for %i players" % playersInGame)
                while len(self.playerSockets) < playersInGame and iterations < 10:
                    connections, wlist, xlist = select([self.sock], [], [], 1)

                    print(connections)
                    for connection in connections:
                        client, address = connection.accept()
                        Thread(
                            target=self._wsHandshake,
                            args=(client,)
                        ).start()
                    iterations += 1

                self.log('Informing players of game starting')
                self.startTime = datetime.now()
                # Run gameStart for each socket
                for sock, playerNum in self.playerSockets.items():
                    Thread(
                        target=self._gameStartUp,
                        args=(sock, playerNum)
                    ).start()

                # Start a new timer
                self.timeoutTimer = Timer(5, self._checkTimeouts)
                self.timeoutTimer.start()
                self.log('Beginning Game Loop')
                while not self.gameOver:
                    clients, wlist, xlist = select(
                        self.playerSockets, [], [], 0.05)

                    for client in clients:
                        Thread(
                            target=self._handleGameConnection,
                            args=(client,)
                        ).start()
                # Build the stats file. Name of the file will just be constant,
                # server remembers only the latest game for now
                self._generateStatsFile(datetime.now())
            self.timeoutTimer.cancel()
        except Exception as e:
            self.log(str(e))
        finally:
            self.callback("game")

    """/*
        Group: Broadcast Handling Methods
        Handlers for the broadcast service
    */"""

    """/*
        Function: _broadcast
        Begins listening for broadcasts on a separate Thread
    */"""
    def _broadcast(self):
        self.closing = False
        thread = Thread(target=self._handleBroadcast)
        thread.daemon = True
        thread.start()

    """/*
        Function: _endBroadcast
        Ends the current broadcast session
    */"""
    def _endBroadcast(self):
        self.closing = True

    """/*
        Function: _handleBroadcast
        Handles broadcast requests from a client, and responds with
        the data of this server
    */"""
    def _handleBroadcast(self):
        broadcastSock = socket(AF_INET, SOCK_DGRAM)
        broadcastSock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        broadcastSock.bind(('', 44445))
        # Only wait 1 second before giving up and re-running the loop
        broadcastSock.settimeout(1)
        self.log('Starting up broadcast service')
        # Only run this thread while the game hasn't started
        while not self.closing and not self.started:
            try:
                data, address = broadcastSock.recvfrom(1024)
                data = data.decode()
                # Send back server data
                # Only send response if data matches protocol, JIC
                if data == 'arena_broadcast_req':
                    data = {
                        'players': self.players,
                        # Only need to say if there is a password or not
                        'password': self.password is not None
                    }
                    serverState = {
                        'port': self.port,
                        'data': data
                    }
                    broadcastSock.sendto(dumps(serverState).encode(), address)
            except timeout:
                pass
        self.log('Broadcast service closing')
        self.callback("broadcast")

    """/*
        Group: Lobby Handling Methods
        Handlers for connections received while the server is in the lobby loop
    */"""

    """/*
        Function: _handleLobbyConnection
        Method run in a separate thread to handle requests while the game is
        still in the lobby state

        Parameters:
            Socket client - The <Socket> to send response through
            Tuple[string, int] address - <Tuple> containing address and port
                                         of the client

        Returns:
            The results of <_lobbyJoin>, <_lobbyQuery>, or <_lobbyStart>,
            depending on the message from the client
    */"""
    def _handleLobbyConnection(self, client, address):
        # Callback on client connection, pass off to correct function
        msg = client.recv(256).decode()
        callback = None
        try:
            if 'join' in msg:
                callback = self._lobbyJoin
            elif 'query' in msg:
                callback = self._lobbyQuery
            elif 'token' in msg:
                callback = self._lobbyGetToken
            elif 'quit' in msg:
                callback = self._lobbyQuit
            elif 'start' in msg:
                callback = self._lobbyStart

            if callback:
                callback(client, address, msg)
        except timeout:
            self.log('Timeout during', msg)
            # Check if the request was involving a player already in the lobby
            # if so, run the (playerLeft) method from Greg's issue
        finally:
            client.close()

    """/*
        Function: _lobbyJoin
        Handler for player joining the lobby

        Parameters:
            Socket client - The <Socket> to send response through
            Tuple[string, int] address - <Tuple> containing address and port
                                         of the client
            string msg - The msg that was sent by the client
                         Includes the username that the player has chosen

        Returns:
            string response - Either 'lobby full' if the lobby is full, or
                              'joined=' + the index of the player in the array
                              <players>
    */"""
    def _lobbyJoin(self, client, address, msg):
        # Handles players joining the lobby
        if self.lobbySize < 4 and not self.started:
            data = msg.split('=')[1]
            username, password = data.split(';')
            # Check the passwords against eachother
            if ((password == 'None' and not self.password) or
                    sha256(password.encode()).hexdigest() == self.password):
                # Add the player to the lobby
                player_index = self._lobbyAddPlayer(username)
                # Generate the token
                token = sha256(
                    str(datetime.now()).encode()).hexdigest()
                self.tokens[username] = token
                msg = 'joined=' + str(player_index) + ';' + token
                client.sendall(msg.encode())
            else:
                client.sendall('incorrect'.encode())
        else:
            client.sendall('lobby full'.encode())

    """/*
        Function: _lobbyAddPlayer
        Adds a new player to the lobby

        Parameters:
            string username - The username of the player that has joined

        Returns:
            int player_index - The index of the player in the array of players
    */"""
    def _lobbyAddPlayer(self, username):
        # Find the index for the player
        player_index = -1
        index_assigned = False
        username_count = 0
        for i in range(len(self.players)):
            player = self.players[i]
            if player is None and not index_assigned:
                player_index = i
                index_assigned = True
            elif player is not None:
                data = player['userName'].split(' (')
                if len(data) <= 2:
                    userNameToTest = data[0]
                else:
                    userNameToTest = ''.join(data[:-1])
                if userNameToTest == username:
                    username_count += 1
        if username_count > 0:
            username += ' (%i)' % (username_count)
        self.log(username + ' has joined the lobby!')
        # Get the player coords
        player_coords_index = choice(range(len(self.coords)))
        player_coords = self.coords[player_coords_index]
        self.coords.remove(player_coords)
        # Create the player lobby object
        player = {
            'x': player_coords[0],
            'y': player_coords[1],
            'userName': username,
            'colour': '#%s' % (ArenaServer._generateColour()),
            'local': False,
            'ready': False,
            'host': self.lobbySize == 0
        }
        self.lobbySize += 1
        self.players[player_index] = player
        self.playerStatus[player_index] = True
        self.canStartUp[username] = True
        return player_index

    """/*
        Function: _lobbyQuery
        Handler for AJAX querying the players in the lobby

        Parameters:
            Socket client - The <Socket> to send response through
            Tuple[string, int] address - <Tuple> containing address and port
                                         of the client
            string msg - The msg that was sent by the client
                         Includes the index of the player in the list of
                         players

        Returns:
            List players - <List> of player objects currently in the lobby

            boolean started - False if the game hasn't started, True otherwise
    */"""
    def _lobbyQuery(self, client, address, msg):
        # Handles queries against lobby
        player_num = int(msg.split('=')[1])
        if self.players[player_num] is not None:
            self.playerStatus[player_num] = True
            client.sendall(dumps(
                {'players': self.players,
                 'started': self.hostStart}).encode())

    """/*
        Function: _lobbyGetToken
        If the <Join Game> script detects a pre-existing cookie on the browser,
        it will query the server to check its token to tell if this player
        already left the lobby and want to rejoin if the lobby has space

        Parameters:
            Socket client - The <Socket> to send response through
            Tuple[string, int] address - <Tuple> containing address and port
                                         of the client
            string msg - The msg that was sent by the client
                         Includes the index of the player in the list of
                         players

        Returns:
            string token - The token of the player who sent the request
    */"""
    def _lobbyGetToken(self, client, address, msg):
        player_num = int(msg.split('=')[1])
        player = self.players[player_num]
        if player:
            username = player['userName']
            token = self.tokens[username]
            client.sendall(token.encode())
        else:
            client.sendall('rejoin'.encode())

    """/*
        Function: _lobbyQuit
        When a user leaves the lobby while they are in the server, this method
        will remove their object from <players>

        Parameters:
            Socket client - The <Socket> to send response through
            Tuple[string, int] address - <Tuple> containing address and port
                                         of the client
            string msg - The msg that was sent by the client
                         Includes the index of the player in the list of
                         players
    */"""
    def _lobbyQuit(self, client, address, msg):
        # Handles players leaving the lobby
        playerNum = int(msg.split("=")[1].split()[0])
        if self.players[playerNum] is not None:
            if self.players[playerNum]["host"]:
                for p in self.players:
                    if p and p != self.players[playerNum]:
                        p["host"] = True
                        break
            username = self.players[playerNum]['userName']
            self.log(username + ' has left the game')
            self.lobbySize -= 1
            self.coords.append(
                (self.players[playerNum]['x'], self.players[playerNum]['y']))
            self.tokens.pop(username, None)

            # Remove the entry from the timeouts dict for this key
            self.playerStatus.pop(playerNum, None)

            # Remove the entry from the canStartUp dict
            self.canStartUp.pop(username, None)
            self.players[playerNum] = None

    """/*
        Function: _lobbyStart
        Handler for the host starting the game

        Parameters:
            Socket client - The <Socket> to send response through
            Tuple[string, int] address - <Tuple> containing address and port
                                         of the client
            string msg - The msg that was sent by the client
                         Includes the index of the player in the list of players

        Returns:
            boolean ready - True if all players in the lobby are ready to
                            start, else False
    */"""
    def _lobbyStart(self, client, address, msg):
        player_num = int(msg.split('=')[1])
        self.players[player_num]['ready'] = True
        # If the server says the host has started, we need to move
        self.hostStart = True
        self.started = True
        for player in self.players:
            if player is not None:
                self.started = self.started and player['ready']
        client.sendall(dumps(
            {'ready': self.players[player_num]['ready']}).encode())

    """/*
        Group: Game Handling Methods
        Handlers for connections received while the server is in the game loop
    */"""

    """/*
        Function: _gameStartUp
        Handler for players arriving at the game.html page for syncing up
        player data

        Parameters:
            Socket socket - The client's socket to send data out through
            int playerNum - The number of the player that coincides with the socket
    */"""

    def _gameStartUp(self, sock, playerNum):
        # Send the player objects that exist to the player through the socket
        for i in range(len(self.players)):
            player = self.players[i]
            if player is not None:
                if i == playerNum:
                    player['local'] = True
                else:
                    player['local'] = False

                # Prepare self.damages
                if i not in self.damages:
                    self.damages[i] = []
        # Send the payload containing only the active players
        data = {'players': self.players}
        sock.sendall(ArenaServer._wsEncode(dumps(data)))

    """/*
        Function: _handleGameConnection
        Method run in a separate thread to handle requests while the game is
        running

        Parameters:
            Socket client - The <Socket> to send response through
            Tuple[string, int] address - <Tuple> containing address and port
                                         of the client
            boolean repeat - Due to issues with http sockets, allow one re-run
                             of this handler to ensure message is received

        Returns:
            The results of <_gameStartUp> or <_gameUpdate>, depending on the
            message from the client
    */"""
    def _handleGameConnection(self, client):
        msg = ArenaServer._wsDecode(client.recv(4096))
        callback = None
        try:
            if 'update' in msg:
                callback = self._gameUpdate
            elif 'gameOver' in msg:
                callback = self._gameOver
            elif 'quit' in msg:
                callback = self._gameQuit

            if callback:
                callback(client, msg)
        except timeout:
            self.log('Timeout during ' + msg)
        finally:
            # Update after the client is closed to keep speed
            self._updateStats()

    """/*
        Function: _gameUpdate
        Handler for the AJAX updating player data for all players connected

        Parameters:
            Socket client - The <Socket> to send response through
            string msg - The msg that was sent by the client
                         Includes a JSON string of the local players data,
                         and the damages done by the local player

        Returns:
            array players - The current status of all players in the game
    */"""
    def _gameUpdate(self, client, msg):
        # Handles game updates on the server
        # Set the ability to start up to False to prevent reload respawns
        try:
            data = loads(msg.split('update=')[1])
        except ValueError:
            self.log('JSON error loading ' + msg.split('update=')[1])
        else:
            player = data['player']
            damages = data['damages']
            try:
                self.playerObjects[player['id']] = player
                # Try this here but if it slows down too much pass it to
                # another Thread
                for damage in damages:
                    self.damages[damage['id']].append(damage['damage'])
            except IndexError:
                return  # This shouldn't happen
            data = {'players': self.playerObjects,
                    'damages': self.damages[player['id']]}
            client.sendall(ArenaServer._wsEncode(dumps(data)))
            self.damages[player['id']] = []
            # Set the player's startUp value to False
            self.canStartUp[player['userName']] = False
            # Update the player's status
            # Get the index of this player in the players list
            for i, lobbyPlayer in enumerate(self.players):
                if (lobbyPlayer is not None and
                        player['userName'] == lobbyPlayer['userName']):
                    self.playerStatus[i] = True
                    break

    """/*
        Function: _gameQuit
        When a user leaves the game page while they are in the lobby,
        this method will kill their object in <playerObjects>.

        Parameters:
            Socket client - The <Socket> to send response through
            string msg - The msg that was sent by the client
                         Includes the index of the player in the list of
                         players
    */"""
    def _gameQuit(self, client, msg):
        # Handles players leaving the lobby
        playerNum = int(msg.split("=")[1].split()[0])
        self.log(self.players[playerNum]['userName'] + ' has left the game')
        self.playerObjects[playerNum]["health"] = 0
        self.playerObjects[playerNum]["bullets"] = []
        self.playerObjects[playerNum]["alive"] = False

        # Remove the entry from the timeouts dict for this key
        self.playerStatus.pop(playerNum, None)

        # Close the client for this player
        removed = []
        for c, num in self.playerSockets.items():
            if num == playerNum:
                removed.append(c)
                c.close()
        for sock in removed:
            self.playerSockets.pop(sock, None)

    """/*
        Function: _gameOver
        Handler for when the game ends

        Parameters:
            Socket client - The <Socket> to send response through
            string msg - The msg that was sent by the client
                         States that the game is over
    */"""
    def _gameOver(self, client, msg):
        # Set gameOver to be True, javascript will redirect to game over screen
        # Once game is over server will write to shelve file in the main thread
        # with the data from the game
        self.gameOver = True

    """/*
        Group: Stats Functions
        Functions controlling the updating of game stats and the generating of results files
    */"""

    """/*
        Function: _updateStats
        Updates the stats for the game. Run after every call of <_gameUpdate>
    */"""
    def _updateStats(self):
        for player in self.playerObjects:
            # Check if player died, and append it to the list of players
            if player is not None and player['id'] not in self.playerStats and not player['alive']:
                self.playerStats.append(player['id'])

    """/*
        Function: _generateStatsFile
        Generates a JSON .ast file, which stores the stats from the
        previous game

        Parameters:
            time endTime - The time at which the game ended
    */"""
    def _generateStatsFile(self, endTime):
        # Reverse the list to give the order in which people died
        # The winner won't be in the playerStats so we need to add them
        for player in self.playerObjects:
            if player['id'] not in self.playerStats:
                self.playerStats.append(player['id'])
                break
        self.playerStats.reverse()
        stats = []
        for pId in self.playerStats:
            player = self.playerObjects[pId]
            stats.append({
                'username': player['userName'],
                'colour': player['colour']
            })
        # Get the game time
        seconds = (endTime - self.startTime).seconds
        minutes = seconds // 60
        seconds = seconds % 60
        gameLength = (minutes, seconds)
        self.log('Generating statsfile')
        # Check if the 'stats' folder exists
        if not os.path.exists('./stats'):
            os.makedirs('./stats')
        filename = './stats/' + datetime.now().strftime(
            '%d%m%Y%H%M%S') + '.ast'
        statsfile = open(filename, 'w')
        # Write out the data in JSON format
        data = {'players': stats, 'gameLength': gameLength}
        statsfile.write(dumps(data))
        statsfile.close()
        os.chmod(filename, 0o666)

    """/*
        Group: Timeout Control Methods
        Methods that help in the control of player timeouts in both the lobby
        and the game itself
    */"""

    """/*
        Function: _checkTimeouts
        Loops through the playerStatus dict, checking each flag.
        If the flag is True it is set to False, if it is False that player is
        removed from the game

        Note:
            This function is called every 10 seconds
    */"""
    def _checkTimeouts(self):
        removedPlayers = []
        # There is a chance that because this is threaded people can leave as
        # this method is running so we wrap in a try block.
        # It's unlikely but it's a just in case measure
        try:
            for playerNum in self.playerStatus:
                if self.playerStatus[playerNum]:
                    self.playerStatus[playerNum] = False
                else:
                    # Remove the player from the lobby or game depending on the
                    # state of the server at this time
                    player = self.players[playerNum]
                    if not self.started:
                        # Game is in lobby state
                        self.coords.append((player['x'], player['y']))
                        self.players[playerNum] = None
                        self.lobbySize -= 1
                        self.tokens.pop(player['userName'], None)
                    elif not self.gameOver:
                        # Game is in the game state
                        # Issue of difference in player numbers between states removed
                        # So this should work just by playerNum
                        self.playerObjects[playerNum]["health"] = 0
                        self.playerObjects[playerNum]["bullets"] = []
                        self.playerObjects[playerNum]["alive"] = False

                    # Remove the entry from the timeouts dict for this key
                    removedPlayers.append(playerNum)
        except Exception as e:
            # self.log('Check Timeouts Error: ' + str(e))
            pass
        finally:
            for playerNum in removedPlayers:
                    self.playerStatus.pop(playerNum, None)
            # Re run this method
            self.timeoutTimer = Timer(5, self._checkTimeouts)
            self.timeoutTimer.start()
