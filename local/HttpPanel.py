from http.server import CGIHTTPRequestHandler, HTTPServer

from .ArenaPanel import ArenaPanel
from tkinter import *

"""/*
    Class: HttpPanel
    Panel for providing control over the built-in Http Server

    Subclass of ArenaPanel
*/"""
class HttpPanel(ArenaPanel):

    def _initialiseVariables(self, *args, **kwargs):
        """/*
            Group: Variables
        */"""

        """/*
            var: _status
            StringVar object containing the status message for the server
        */"""
        self._status = StringVar()
        self._status.set("Server Stopped")

        """/*
            var: _buttonLabel
            StringVar object containing the label for the button
        */"""
        self._buttonLabel = StringVar()
        self._buttonLabel.set("Start")

        """/*
            var: _running
            Flag to determine whether the server is currently running
        */"""
        self._running = False

        """/*
            var: _server
            The server object that will be run
        */"""
        self.server = HTTPServer(('', 8000), CGIHTTPRequestHandler)

        """/*
            var: _statusLabel
            Label displaying the status of the server.
            Stored to allow for the changing of the colour of the text
        */"""
        self._statusLabel = None

    def _initialiseChildren(self):
        # Just need to add a label and button
        self._statusLabel = Label(self, textvariable=self._status, foreground="red")
        self._statusLabel.pack(side=TOP, fill=BOTH, expand=1)
        Button(self, textvariable=self._buttonLabel, command=self._run).pack(
            side=TOP, fill=BOTH, expand=1)

    """/*
        Group: Private Methods
    */"""

    """/*
        Function: _run
        Handler for the running of the underlying HTTPServer
    */"""
    def _run(self):
        if not self._running:
            self._status.set("Server Started")
            self._buttonLabel.set("Stop")
            self._statusLabel.config(foreground="green")
            self._running = True
        else:
            self._status.set("Server Stopped")
            self._buttonLabel.set("Start")
            self._statusLabel.config(foreground="red")
            self._running = False

    def close(self):
        if self._running:
            self._run()
        return True

