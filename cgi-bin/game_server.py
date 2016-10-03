from socket import *
from sys import exit
from select import select
from json import dumps, loads
from urllib.request import unquote

# Create a TCP server socket
sock = socket(AF_INET, SOCK_STREAM)

# Set values for localhost
hostname = gethostname()
hostip = gethostbyname(hostname)
port = 44444 # Do not change port if you want to make the server public (Password support coming soon)
server_address = (hostip, port)
print('SERVER ADDRESS DETAILS')
print('PASS THE FOLLOWING TO YOUR FRIENDS')
print('Address:', hostip)
print('Port:', port)

# Bind socket to address
sock.bind(server_address)

# Lobby loop
# Set up necessary vars
started = False
host_start = False
players = []
# Remove when map editor implemented
width = height = 650
coords = [
    (width / 4, height / 4),
    ((3 * width) / 4, height / 4),
    (width / 4, (3 * height) / 4),
    ((3 * width) / 4, (3 * height) / 4)
]
# Listen for 8 incoming connections, since 4 players with max 2 each
sock.listen(8)
print('Lobby Open')
# Below is for when the game starts, might have to change some implementation
while not started:
    connections, wlist, xlist = select([sock], [], [], 0.05)

    try:
        for connection in connections:
            client, address = connection.accept()
            msg = client.recv(256).decode()
            if 'join' in msg:
                if len(players) < 4 and not started:
                    username = msg.split('=')[1]
                    from random import choice
                    player_coords_index = choice(range(len(coords)))
                    player_coords = coords[player_coords_index]
                    coords.remove(player_coords)
                    players.append({
                        'x': player_coords[0],
                        'y': player_coords[1],
                        'userName': username,
                        'colour': '#%s' % (''.join([choice('0123456789ABCDEF')
                                                    for x in range(6)])),
                        'local': False,
                        'queryTimeout': 20, # Subtract 1 whenever there is a query
                        'ready': False
                    })
                    print(username, 'has joined the lobby!')
                    msg = 'joined=%i' % (len(players) - 1)
                    client.sendall(msg.encode())
                else:
                    client.sendall('lobby full'.encode())
            elif 'query' in msg:
                # Sort out timeouts
                player_num = int(msg.split('=')[1])
                # print('Query coming from', players[player_num]['userName'])
                players[player_num]['queryTimeout'] = 21
                for player in players:
                    player['queryTimeout'] -= 1
                    if player['queryTimeout'] <= 0:
                        players.remove(player)
                client.sendall(dumps({'players': players, 'started': host_start}).encode())
            elif 'start' in msg:
                player_num = int(msg.split('=')[1])
                # print('Start request from', players[player_num]['userName'])
                players[player_num]['ready'] = True
                # If the server says the host has started, we need to move
                host_start = True
                started = True
                for player in players:
                    # print(player['userName'], player['ready'])
                    started = started and player['ready']
                client.sendall(dumps({'ready': players[player_num]['ready']}).encode())
            # elif 'leave' in msg
            # else forget about it
            client.close()
    except KeyboardInterrupt:
        sock.close()
        exit(0)
    # except Exception as e:
    #     raise
    #     exit(1)

# Listen for 4 incoming connections, since 4 players
num_players = len(players)
sock.listen(num_players)
print('Start Game')
players = [None for _ in range(num_players)]
while True:
    connections, wlist, xlist = select([sock], [], [], 0.05)

    try:
        for connection in connections:
            client, address = connection.accept()
            headers = client.recv(4096)
            data = unquote(client.recv(4096).decode()).split('=')[1]
            print(data)
            data = loads(data)
            try:
               players[data['id']] = data
            except KeyError:
                pass

            # Print out the json of the players list for the client to read in
            client.sendall('HTTP/1.1 200 OK\r\n'.encode())
            client.sendall('Content-Type: application/json\r\n'.encode())
            client.sendall('Access-Control-Allow-Origin: http://cs1.ucc.ie\r\n'.encode())
            client.sendall('\r\n'.encode())
            output = {'players': players}
            client.sendall(dumps(output).encode())
            client.close()
    except KeyboardInterrupt:
        connection.close()
        break
    except Exception as e:
        print('Content-Type: text/plain')
        print()
        print('Error', e)
        break

sock.close()
