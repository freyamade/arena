from json import dumps, loads
from random import choice
from select import select
from socket import *
from sys import exit
from threading import Thread
from urllib.request import unquote

class ArenaServer:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        self.sock = sock

        # Game var setup
        self.started = False
        self.host_start = False
        self.players = [None for _ in range(4)]
        self.lobby_size = 0
        width = height = 650
        self.coords = [
            (width / 4, height / 4),
            ((3 * width) / 4, height / 4),
            (width / 4, (3 * height) / 4),
            ((3 * width) / 4, (3 * height) / 4)
        ]
        self.player_objects = []

    def close(self):
        print('Server Closing')
        self.sock.close()

    def listen(self):
        self.sock.listen(10)
        print('Lobby Open')
        # Lobby loop
        while not self.started:
            connections, wlist, xlist = select([self.sock], [], [], 0.05)

            for connection in connections:
                client, address = connection.accept()
                client.settimeout(5)
                Thread(
                    target=self._handleLobbyConnection,
                    args=(client, address)).start()
        # TODO - Add the game loop
        print('Game Starting')
        while True:  # TODO - Change to end loop when game is over
            connections, wlist, xlist = select([self.sock], [], [], 0.05)

            for connection in connections:
                client, address = connection.accept()
                client.settimeout(10)
                Thread(
                    target=self._handleGameConnection,
                    args=(client, address)).start()

    """LOBBY METHODS"""
    def _handleLobbyConnection(self, client, address):
        # Callback on client connection, pass off to correct function
        msg = client.recv(256).decode()
        callback = None
        if 'join' in msg:
            callback = self._lobbyJoin
        elif 'query' in msg:
            callback = self._lobbyQuery
        elif 'start' in msg:
            callback = self._lobbyStart

        if callback:
            callback(client, address, msg)
        client.close()
        return

    def _lobbyJoin(self, client, address, msg):
        # Handles players joining the lobby
        if self.lobby_size < 4 and not self.started:
            username = msg.split('=')[1]
            print(username, 'has joined the lobby!')
            # Get the player coords
            player_coords_index = choice(range(len(self.coords)))
            player_coords = self.coords[player_coords_index]
            self.coords.remove(player_coords)
            # Create the player lobby object
            player = {
                'x': player_coords[0],
                'y': player_coords[1],
                'userName': username,
                'colour': '#%s' % (self._generateColour()),
                'local': False,
                'queryTimeout': 20,
                'ready': False
            }
            self.lobby_size += 1
            # Find the index for the player
            for i in range(len(self.players)):
                if self.players[i] == None:
                    break
            self.players[i] = player
            msg = 'joined=' + str(i)
            client.sendall(msg.encode())
        else:
            client.sendall('lobby full'.encode())

    def _lobbyQuery(self, client, address, msg):
        # Handles queries against lobby
        player_num = int(msg.split('=')[1])
        self.players[player_num]['queryTimeout'] = 21
        for i in range(len(self.players)):
            player = self.players[i]
            if player != None:
                player['queryTimeout'] -= 1
                if player['queryTimeout'] <= 0:
                    self.coords.append((player['x'], player['y']))
                    self.players[i] = None
                    self.players_in_lobby -= 1
        client.sendall(dumps(
            {'players':
             [player for player in self.players if player is not None],
             'started': self.host_start}).encode())

    def _lobbyStart(self, client, address, msg):
        player_num = int(msg.split('=')[1])
        self.players[player_num]['ready'] = True
        # If the server says the host has started, we need to move
        self.host_start = True
        self.started = True
        for player in self.players:
            if player is not None:
                self.started = self.started and player['ready']
        client.sendall(dumps(
            {'ready': self.players[player_num]['ready']}).encode())

    """GAME LOOP METHODS"""
    def _handleGameConnection(self, client, address, repeat=True):
        msg = client.recv(4096).decode()
        callback = None
        if 'start_up' in msg:
            callback = self._gameStartUp
        elif 'update' in msg:
            callback = self._gameUpdate

        if callback:
            callback(client, address, msg)
        elif repeat:
            self._handleGameConnection(client, address, False)
        client.close()
        return

    def _gameStartUp(self, client, address, msg):
        # Handles players arriving at the game screen
        # Loop through the list of players, setting flags
        player_num = int(unquote(msg.split('start_up=')[1]))
        payload = []
        ready = True
        for i in range(len(self.players)):
            player = self.players[i]
            if player is not None:
                if i == player_num:
                    player['local'] = True
                    player['ready'] = True
                else:
                    player['local'] = False
                ready = ready and player['ready']
                payload.append(player)
        # Send the payload containing only the active players
        data = {'players': payload, 'ready': ready}
        response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: http://cs1.ucc.ie\r\n\r\n"
        response += dumps(data) + '\r\n'
        client.sendall(response.encode())

    def _gameUpdate(self, client, address, msg):
        # Handles game updates on the server
        # MUST BE AS EFFICIENT AS POSSIBLE
        player = loads(unquote(msg.split('update=')[1]))
        try:
            self.player_objects[player['id']] = player
        except IndexError:
            self.player_objects.append(player)
        data = {'players': self.player_objects}
        response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: http://cs1.ucc.ie\r\n\r\n"
        response += dumps(data)
        client.sendall(response.encode())

    """HELPER METHODS"""
    def _generateColour(self):
        return ''.join([choice('0123456789ABCDEF') for x in range(6)])

if __name__ == '__main__':
    # Set values for localhost
    hostname = gethostname()
    hostip = gethostbyname(hostname)
    port = 44444 # Do not change port if you want to make the server public (Password support coming soon)
    server_address = (hostip, port)
    print('SERVER ADDRESS DETAILS')
    print('PASS THE FOLLOWING TO YOUR FRIENDS')
    print('Address:', hostip)
    print('Port:', port)
    server = ArenaServer(hostip, port)
    try:
        server.listen()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    finally:
        server.close()
