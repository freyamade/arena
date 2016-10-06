from socket import *
from sys import exit
from select import select
from json import dumps, loads
from random import choice

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
players = [None for _ in range(4)]
players_in_lobby = 0
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
try:
    while not started:
        connections, wlist, xlist = select([sock], [], [], 0.05)

        for connection in connections:
            client, address = connection.accept()
            msg = client.recv(4096).decode()
            print(msg)
            response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nAccess-Control-Allow-Origin: http://cs1.ucc.ie\r\n\r\n'
            response += '<h3>Response</h3>'
            client.sendall(response.encode())
            client.close()
#             if 'join' in msg:
#                 if players_in_lobby < 4 and not started:
#                     username = msg.split('=')[1]
#                     player_coords_index = choice(range(len(coords)))
#                     player_coords = coords[player_coords_index]
#                     coords.remove(player_coords)
#                     player = ({
#                         'x': player_coords[0],
#                         'y': player_coords[1],
#                         'userName': username,
#                         'colour': '#%s' % (''.join([choice('0123456789ABCDEF')
#                                                     for x in range(6)])),
#                         'local': False,
#                         'queryTimeout': 20, # Subtract 1 whenever there is a query
#                         'ready': False
#                     })
#                     players_in_lobby += 1
#                     print(username, 'has joined the lobby!')
#                     # Find the position for this new player
#                     for i in range(len(players)):
#                         if players[i] == None:
#                             break
#                     players[i] = player
#                     msg = 'joined=%i' % i
#                     client.sendall(msg.encode())
#                 else:
#                     client.sendall('lobby full'.encode())
#             elif 'query' in msg:
#                 # Sort out timeouts
#                 player_num = int(msg.split('=')[1])
#                 # print('Query coming from', players[player_num]['userName'])
#                 players[player_num]['queryTimeout'] = 21
#                 for i in range(len(players)):
#                     player = players[i]
#                     if player != None:
#                         player['queryTimeout'] -= 1
#                         if player['queryTimeout'] <= 0:
#                             coords.append((player['x'], player['y']))
#                             players[i] = None
#                             players_in_lobby -= 1
#                 client.sendall(dumps({'players': [player for player in players if player is not None], 'started': host_start}).encode())
#             elif 'start' in msg:
#                 player_num = int(msg.split('=')[1])
#                 # print('Start request from', players[player_num]['userName'])
#                 players[player_num]['ready'] = True
#                 # If the server says the host has started, we need to move
#                 host_start = True
#                 started = True
#                 for player in [player for player in players if player is not None]:
#                     # print(player['userName'], player['ready'])
#                     started = started and player['ready']
#                 client.sendall(dumps({'ready': players[player_num]['ready']}).encode())
#             # elif 'leave' in msg
#             # else forget about it
#             client.close()
except KeyboardInterrupt:
    sock.close()
    exit(0)
# except Exception as e:
#     raise
#     exit(1)

# print('Finalising Setup')
# player_objects = [] # List of the objects in the javascript code
# # Get all the players set up in game in this loop, then have a third loop
# # to handle the actual gameplay
# try:
#     while True:
#         connections, wlist, xlist = select([sock], [], [], 0.05)
#         # Debug
#         if choice(range(10)) == 0:
#             print(player_objects)
#             for connection in connections:
#                 # Check if the message says start_up, send the JSON of the players
#                 # list with no Nones in it and the local flag set accordingly
#                 client, address = connection.accept()
#                 msg = client.recv(256).decode()
#                 if 'start_up' in msg:
#                     # Loop through the list of players, setting flags
#                     player_num = int(msg.split('=')[1])
#                     payload = []
#                     ready = True
#                     for i in range(len(players)):
#                         player = players[i]
#                         if player is not None:
#                             if i == player_num:
#                                 player['local'] = True
#                                 player['ready'] = True
#                             else:
#                                 player['local'] = False
#                             ready = ready and player['ready']
#                             payload.append(player)
#                     # Checked all players and set flags, send the data
#                     data = {'players': payload, 'ready': ready}
#                     client.sendall(dumps(data).encode())
#                 elif 'update' in msg:
#                     # If the id is in the player_objects list, update, else append
#                     player = loads(msg.split('=')[1])
#                     try:
#                         player_objects[player['id']] = player
#                     except IndexError:
#                         player_objects.append(player)
#                     data = {'players': player_objects}
#                     client.sendall(dumps(data).encode())
#                 client.close()
# except KeyboardInterrupt:
#     pass
# except Exception as e:
#     print(e)
#     pass

sock.close()
