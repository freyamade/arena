from .ArenaPanel import ArenaPanel
from collections import deque
from datetime import datetime
from tkinter import *

class LogPanel(ArenaPanel):

    def _initialiseVariables(self, *args, **kwargs):
        self._log = StringVar()
        self._log.set("")

        self._messages = deque()

        self._num_messages = 0

        self._max_messages = 42

    def _initialiseChildren(self):
        logLabel = Label(self, textvariable=self._log,
            anchor="sw", justify=LEFT)
        logLabel.pack(fill=BOTH, expand=1)

    def close(self):
        # TODO - Write out to the log file
        return True

    def logMessage(self, message):
        # Takes in a message from an external source and adds it to the server
        # log with a time stamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = '[%s] - %s' % (timestamp, message)
        self._messages.append(log_message)
        self._num_messages += 1
        if self._num_messages > self._max_messages:
            self._messages.popleft()
            self._num_messages -= 1

        self._log.set('\n'.join(self._messages))
