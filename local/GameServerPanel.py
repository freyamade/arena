from .ArenaPanel import ArenaPanel
from .ArenaServer import ArenaServer
from socket import gethostname, gethostbyname
from threading import Thread
from tkinter import *


class GameServerPanel(ArenaPanel):
    """/*
        Class: GameServerPanel
        <Panel> for graphically controlling the underlying <ArenaServer>

        Subclass of <ArenaPanel>

        Inherited Methods:
            - <ArenaPanel._initialiseVariables>
            - <ArenaPanel._initialiseChildren>
            - <ArenaPanel.close>
    */"""

    def _initialiseVariables(self, *args, **kwargs):
        """/*
            Group: Variables
        */"""

        defaultPort = 44444
        """/*
            var: _port
            <IntVar> object for managing the port number passed by the user
        */"""
        self._port = IntVar()
        self._port.set(defaultPort)

        """/*
            var: _status
            <StringVar> object for managing the status label text
        */"""
        self._status = StringVar()
        self._status.set("Server Stopped")

        """/*
            var: _buttonLabel
            <StringVar> object for managing the game server button text
        */"""
        self._buttonLabel = StringVar()
        self._buttonLabel.set("Start")

        """/*
            var: _running
            Flag for whether or not the server is already running
        */"""
        self._running = False

        """/*
            var: _server
            The currently running <ArenaServer> instance
        */"""
        self._server = None

        """/*
            var: _logMessage
            A function to be passed into the server to allow for logging into
            the <LogPanel>
        */"""
        self._logMessage = kwargs['logMessage']

        """/*
            var: _password
            <StringVar> object used for maintaining passwords input into the
            GUI
        */"""
        self._password = StringVar()

    def _initialiseChildren(self):
        # Port Panel - Label and an ENABLED Entry
        portPanel = Frame(self)
        Label(portPanel, text="Port Number").pack(side=LEFT, fill=X, expand=1)
        portEntry = Entry(portPanel, textvariable=self._port)
        portEntry.pack(side=LEFT, fill=X, expand=1)
        portPanel.pack(fill=BOTH, expand=1)

        # Password Panel - Label and an ENABLED Entry
        passwordPanel = Frame(self)
        Label(passwordPanel, text="Password").pack(side=LEFT, fill=X, expand=1)
        Entry(passwordPanel, textvariable=self._password).pack(
            side=LEFT, fill=X, expand=1)
        passwordPanel.pack(fill=BOTH, expand=1)

        # Status Panel - Label and a Button to run this server
        runPanel = Frame(self)
        self._statusLabel = Label(
            runPanel, textvariable=self._status, foreground="red")
        self._statusLabel.pack(side=TOP, fill=BOTH, expand=1)
        runButton = Button(
            runPanel, textvariable=self._buttonLabel, command=self._toggle)
        runButton.pack(side=TOP, fill=BOTH, expand=1)
        runPanel.pack(fill=BOTH, expand=1)

        # Display a welcome message
        self._logMessage("Welcome to the Arena!")

    """/*
        Group: Private Methods
    */"""

    """/*
        Function: _toggle
        Toggles the game server on or off.
        Called when the server button is pressed.
    */"""
    def _toggle(self):
        if not self._running:
            # Run the server
            password = self._password.get()
            if not password:
                password = None
            try:
                self._server = ArenaServer(self._port.get(),
                    self._logMessage, self._serviceClose,
                    password)
            except Exception as e:
                self._popup("Error", str(e))
            else:
                # No exceptions
                # Create the thread
                thread = Thread(target=self._server.listen)
                thread.daemon = True
                thread.start()
                # Update the labels
                self._status.set("Server Running")
                self._buttonLabel.set("Stop")
                self._statusLabel.config(foreground="green")
                # Update the switch
                self._running = True
        else:
            # Try and close the server
            if self._canClose():
                # If the broadcast server is running, update the GUI
                # Close the server
                thread = Thread(target=self._server.close)
                thread.daemon = True
                thread.start()
                self._server = None
                self._thread = None
                # Update the labels
                self._status.set("Server Stopped")
                self._buttonLabel.set("Start")
                self._statusLabel.config(foreground="red")
                # Update the switch
                self._running = False
            else:
                self._popup("Cannot Close Server",
                    "The game has started, so the server cannot be closed")

    """/*
        Function: _canClose
        Reports whether this panel can close
    */"""
    def _canClose(self):
        return self._server == None or not self._server.inGame()

    """/*
        Function: _serviceClose
        Handler for when the server itself closes one of its services.
        This callback updates the appropriate display
    */"""
    def _serviceClose(self, service):
        # Handles when the server closes a service to change the display
        if service == 'game' and self._running:
            self._toggle()

    def close(self):
        if self._canClose():
            if self._running:
                self._toggle()
            return True
        else:
            return False
