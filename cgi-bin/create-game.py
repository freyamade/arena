#!/usr/bin/env python3
from cgitb import enable
enable()
from datetime import datetime
from hashlib import sha256
from shelve import open as shelf
# Create a new game file, and store it in the games folder
# Game wile will be named using sha256 of datetime

filename = sha256(datetime.now().isoformat().encode()).hexdigest()
print('Content-Type: text/plain')
print()
print(filename)
