from .ArenaPanel import ArenaPanel
from collections import deque
from datetime import datetime
from os import path, makedirs
from tkinter import *

"""/*
        Class: LogPanel
        <Panel> for displaying the server logs

        Subclass of <ArenaPanel>

        Inherited Methods:
            - <ArenaPanel._initialiseVariables>
            - <ArenaPanel._initialiseChildren>
            - <ArenaPanel.close>
*/"""
class LogPanel(ArenaPanel):

    def _initialiseVariables(self, *args, **kwargs):
        """/*
            Group: Variables
        */"""

        """/*
            var: _log
            <StringVar> for managing the log display
        */"""
        self._log = StringVar()
        self._log.set("")

        """/*
            var: _messages
            An array for holding the amount of messages that can be displayed
            in the panel at one time
        */"""
        self._messages = deque()

        """/*
            var: _numMessages
            The number of messages currently on display
        */"""
        self._numMessages = 0

        """/*
            var: _maxMessages
            The maximum number of messages that can be displayed at one time
        */"""
        self._maxMessages = 42

        # Ensure a logs directory exists
        try:
            if not path.exists('./logs'):
                makedirs('./logs')

            """/*
                var: _logfile
                The file that all log messages will be written out to.

                This is used to store a complete log of everything that happened
            */"""
            self._logfile = open(
                './logs/arena_' + datetime.now().strftime(
                    '%d%m%Y%H%M%S') + '.log',
                'w', 1)
        except IOError:
            print("Error when attempting to open logfile")
            self._logfile = None

    def _initialiseChildren(self):
        logLabel = Label(
            self, textvariable=self._log, anchor="sw", justify=LEFT)
        logLabel.pack(fill=BOTH, expand=1)

    def close(self):
        self._logfile.close()
        return True

    """/*
        Group: Public Methods
    */"""

    """/*
        Function: logMessage
        Take in a message and display it in the log.

        Also write the message to a complete log file.
    */"""
    def logMessage(self, message):
        # Takes in a message from an external source and adds it to the server
        # log with a time stamp
        if self._logfile is not None:
            self._logfile.write(message + '\n')
            if 'JSON' in message:
                message = 'JSON error - Check log file for full details'
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_message = '[%s] - %s' % (timestamp, message)
            self._messages.append(log_message)
            self._numMessages += 1
            if self._numMessages > self._maxMessages:
                self._messages.popleft()
                self._numMessages -= 1

            self._log.set('\n'.join(self._messages))
