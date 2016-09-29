#!/usr/bin/env python3
# File containing the function to make the user join a game
from http.cookies import SimpleCookie
from os import environ, path, getcwd
from shelve import open as shelf

def join(filename):
    # Filename will be null if the call is from list rather than create
    cookie = SimpleCookie()
    if 'HTTP_COOKIE' in environ:
        cookie.load(environ['HTTP_COOKIE'])
    cookie['filename'] = filename

    # May change when map creation implemented
    width = 650
    height = 650

    # Now add this player to the game file
    gamefile = shelf('../games/' + filename, writeback=True)
    if 'players' not in gamefile:
        # We are creating a new game
        coords = [
            (width / 4, height / 4),
            ((3 * width) / 4, height / 4),
            (width / 4, (3 * height) / 4),
            ((3 * width) / 4, (3 * height) / 4)
        ]
        players = []
        joinable = True
    else:
        coords = gamefile['coords']
        players = gamefile['players']
        joinable = gamefile['joinable']

    if joinable:
        # Now set up a dict for the new player
        # Colours will be profile specific, but random until auth implemented
        from random import choice
        player_coords_index = choice(range(len(coords)))
        player_coords = coords[player_coords_index]
        coords.remove(player_coords)
        # Store the initialistion json in file until game starts, then replace with
        # player objects from javascript after creation
        players.append({
            'x': player_coords[0],
            'y': player_coords[1],
            'userName': 'Player %i' % (len(players) + 1),
            'colour': '#%s' % (''.join([choice('0123456789ABCDEF')
                                        for x in range(6)]))
            # Local will be handled in another file
        })
        gamefile['players'] = players
        gamefile['coords'] = coords
        gamefile['joinable'] = len(players) < 4
        cookie['player_num'] = len(players) - 1
        print(cookie)
        gamefile.close()

        print('Content-Type: text/plain')
        print('Status: 303')
        print('Location: lobby.py')
        print()

    else:
        print('Content-Type: text/html')
        print()
        print('<p>Whoops! The lobby seems to be full now, sorry<p><br /><p>Go <a href="list-games.py">back</a>?</p>')

if __name__ == '__main__':
    # Get the filename from the cookie and run the method
    from cgitb import enable
    enable()
    from cgi import FieldStorage
    data = FieldStorage()
    filename = data.getfirst('filename', '')
    if not filename or not path.abspath(filename) != getcwd():
        print('Content-Type: text/plain')
        print()
        print(path.abspath(filename))
        print(getcwd())
    else:
        # Valid path name
        join(filename)
