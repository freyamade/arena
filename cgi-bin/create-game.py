#!/usr/bin/env python3
from cgitb import enable
enable()
from datetime import datetime
from hashlib import sha256
from shelve import open as shelf
from os import environ
# Create a new game file, and store it in the games folder
# Game wile will be named using sha256 of datetime

filename = sha256(datetime.now().isoformat().encode()).hexdigest()

# Now create a file and then post to join-game.py to join the game
shelf('../games/' + filename).close()

from join_game import join
join(filename)
