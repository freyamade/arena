from .ArenaPanel import ArenaPanel
from .ArenaServer import ArenaServer
from socket import gethostname, gethostbyname
from threading import Thread
from tkinter import *

class GameServerPanel(ArenaPanel):

    def _initialiseVariables(self, *args, **kwargs):
        self._host = gethostbyname(gethostname())

        default_port = 44444
        self._port = IntVar()
        self._port.set(default_port)

        self._status = StringVar()
        self._status.set("Server Stopped")

        self._buttonLabel = StringVar()
        self._buttonLabel.set("Start")

        self._broadcastStatus = StringVar()
        self._broadcastStatus.set("Not Broadcasting")

        self._broadcastButtonLabel = StringVar()
        self._broadcastButtonLabel.set("Start Broadcasting")

        self._running = False

        self._server = None

        self._broadcasting = False

        self._logMessage = kwargs['logMessage']

    def _initialiseChildren(self):
        # Host Panel - Label and a DISABLED Entry
        hostPanel = Frame(self)
        Label(hostPanel, text="Host Address").pack(side=LEFT, fill=X, expand=1)
        hostEntry = Entry(hostPanel)
        hostEntry.insert(0, self._host)
        hostEntry.config(state=DISABLED)
        hostEntry.pack(side=LEFT, fill=X, expand=1)
        hostPanel.pack(fill=BOTH, expand=1)

        # Port Panel - Label and an ENABLED Entry
        portPanel = Frame(self)
        Label(portPanel, text="Port Number").pack(side=LEFT, fill=X, expand=1)
        portEntry = Entry(portPanel, textvariable=self._port)
        portEntry.pack(side=LEFT, fill=X, expand=1)
        portPanel.pack(fill=BOTH, expand=1)

        # Status Panel - Label and a Button to run this server
        runPanel = Frame(self)
        self._statusLabel = Label(runPanel, textvariable=self._status,
            foreground="red")
        self._statusLabel.pack(side=LEFT, fill=BOTH, expand=1)
        runButton = Button(runPanel, textvariable=self._buttonLabel,
            command=self._toggle)
        runButton.pack(side=LEFT, fill=BOTH, expand=1)
        runPanel.pack(fill=BOTH, expand=1)

        # Broadcast Panel - Second status panel for control over broadcasting
        broadcastPanel = Frame(self)
        self._broadcastStatusLabel = Label(broadcastPanel,
            textvariable=self._broadcastStatus, foreground="red")
        self._broadcastStatusLabel.pack(side=LEFT, fill=BOTH, expand=1)
        broadcastButton = Button(broadcastPanel,
            textvariable=self._broadcastButtonLabel,
            command=self._broadcast)
        broadcastButton.pack(side=LEFT, fill=BOTH, expand=1)
        broadcastPanel.pack(fill=BOTH, expand=1)

        # Display a welcome message
        self._logMessage("Welcome to the Arena!")

    def _toggle(self):
        if not self._running:
            # Run the server
            port_num = self._port.get()
            try:
                self._server = ArenaServer(self._host, port_num,
                    self._logMessage, self._serviceClose)
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
                if self._broadcasting:
                    self.broadcast()
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

    def _broadcast(self):
        # Handle broadcasting of the server
        if not self._broadcasting:
            if not self._server:
                self._popup("Cannot Broadcast",
                    "The server must first be running before it can broadcast")
            elif self._server.inGame():
                self._popup("Cannot Broadcast",
                    "The game is running. There's no point in broadcasting")
            else:
                # We can broadcast
                Thread(target=self._server.broadcast).start()
                # Update the labels
                self._broadcastStatus.set("Broadcasting")
                self._broadcastStatusLabel.config(foreground="green")
                self._broadcastButtonLabel.set("Stop Broadcasting")
                # Update the switch
                self._broadcasting = True
        else:
            # Stop broadcasting
            Thread(target=self._server.endBroadcast).start()
            # Update the labels
            self._broadcastStatus.set("Not Broadcasting")
            self._broadcastButtonLabel.set("Start Broadcasting")
            self._broadcastStatusLabel.config(foreground="red")
            # Update the switch
            self._broadcasting = False

    def _canClose(self):
        return self._server == None or not self._server.inGame()

    def close(self):
        if self._canClose():
            if self._running:
                self._toggle()
            return True
        else:
            return False

    def _serviceClose(self, service):
        # Handles when the server closes a service to change the display
        if service == 'broadcast' and self._broadcasting:
            self._broadcast()
        elif service == 'game' and self._running:
            self._toggle()
