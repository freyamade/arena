from collections import deque
from datetime import datetime
from server import ArenaServer
from socket import gethostname, gethostbyname
from threading import Thread
from tkinter import *

# TODO - Maybe break every panel into its own class
# TODO - Override the X button and ensure every service is closed
# TODO - Save all messages into a log file once the gui closes
#   File opens during init, writes out every time log message is called
#   and closes during the override of the X button or on a KeyboardInterrupt in console

class ArenaGUI(Tk):

    def __init__(self, master):
        # Set up the master window
        super(ArenaGUI, self).__init__(master)
        self.title("Arena Server")
        self.resizable(0, 0)
        self.minsize(width=750, height=650)
        self.protocol("WM_DELETE_WINDOW", self._close)

        # Set up server vars
        self.host = gethostbyname(gethostname())
        self.messages = deque()
        self.num_messages = 0
        self.max_messages = 44 # Trust me

        self._initialiseServerPanel()
        self._initialiseStatusPanel()
        self._initialiseLobbyPanel()

        self.gameRunning = False
        self.broadcastRunning = False

        # Set up the Arena Server
        self.gameServer = None
        self.gameThread = None
        # Amend to provide printing method


    def _initialiseServerPanel(self):
        serverPanel = LabelFrame(self, text="Server Log", width=400,
            height=650)
        serverPanel.pack(side=LEFT, fill=BOTH, expand=1)

        self.log = StringVar()
        self.log.set("")
        serverLog = Label(serverPanel, textvariable=self.log,
            anchor="sw", justify=LEFT)
        serverLog.pack(fill=BOTH, expand=1, side=TOP)

    def _initialiseStatusPanel(self):
        statusPanel = LabelFrame(self, text="Service Statuses", width=350,
            height=400)
        statusPanel.pack(fill=BOTH, expand=1, side=TOP)

        # Add 2 panels, one for the game server, the other for the broadcast
        self._initialiseGameServerPanel(statusPanel)
        self._initialiseBroadcastPanel(statusPanel)

    def _initialiseBroadcastPanel(self, parent):
        broadcastPanel = LabelFrame(parent, text="Broadcast Server",
            width=300, height=100)
        broadcastPanel.pack(expand=1, fill=BOTH)

        # Add label and button
        runPanel = Frame(broadcastPanel)
        self.broadcastStatus = StringVar()
        self.broadcastStatus.set("Server Stopped")
        self.broadcastStatusLabel = Label(runPanel,
            textvariable=self.broadcastStatus, foreground="red")
        self.broadcastStatusLabel.pack(side=LEFT, fill=BOTH, expand=1)

        self.broadcastButtonLabel = StringVar()
        self.broadcastButtonLabel.set("Start")
        runButton = Button(runPanel, textvariable=self.broadcastButtonLabel,
            command=self._runBroadcastServer)
        runButton.pack(side=LEFT, fill=X, expand=1)

        runPanel.pack(fill=BOTH, expand=1)

    def _initialiseGameServerPanel(self, parent):
        gameServerPanel = LabelFrame(parent, text="Game Server",
            width=300, height=150)
        gameServerPanel.pack(expand=1, fill=BOTH)

        # Add two text entries and a checkbox and a button
        hostPanel = Frame(gameServerPanel)
        # Label for host address
        Label(hostPanel, text="Host Address").pack(side=LEFT, fill=X, expand=1)
        host = Entry(hostPanel)
        host.insert(0, self.host)
        host.config(state=DISABLED)
        host.pack(side=LEFT)
        hostPanel.pack(fill=BOTH, expand=1)

        portPanel = Frame(gameServerPanel)
        Label(portPanel, text="Port Number").pack(side=LEFT, fill=X, expand=1)
        self.port = IntVar()
        self.port.set(44444)
        port = Entry(portPanel, textvariable=self.port)
        port.pack(side=LEFT)
        portPanel.pack(fill=BOTH, expand=1)


        runPanel = Frame(gameServerPanel)
        self.gameStatus = StringVar()
        self.gameStatus.set("Server Stopped")
        self.gameStatusLabel = Label(runPanel,
            textvariable=self.gameStatus, foreground="red")
        self.gameStatusLabel.pack(side=LEFT, fill=BOTH, expand=1)

        self.gameButtonLabel = StringVar()
        self.gameButtonLabel.set("Start")
        runButton = Button(runPanel, textvariable=self.gameButtonLabel,
            command=self._runGameServer)
        runButton.pack(side=LEFT, fill=X, expand=1)

        runPanel.pack(fill=BOTH, expand=1)

    def _initialiseLobbyPanel(self):
        lobbyPanel = LabelFrame(self, text="Lobby Status", width=350,
            height=250)
        lobbyPanel.pack(fill=BOTH, expand=1, side=TOP)

    def _runGameServer(self):
        if not self.gameRunning:
            # Set up arena server
            port = self.port.get()
            try:
                self.gameServer = ArenaServer(self.host, port, self.logMessage)
            except Exception as e:
                self._popup('Error', str(e))
            else:
                self.gameThread = Thread(target=self.gameServer.listen)
                self.gameStatus.set("Server Running")
                self.gameButtonLabel.set("Stop")
                self.gameStatusLabel.config(foreground="green")
                self.gameRunning = True
                self.gameThread.start()
        else:
            # TODO - Ensure server isn't in game before trying to close
            if not self.gameServer.inGame():
                self.gameStatus.set("Server Stopped")
                self.gameButtonLabel.set("Start")
                self.gameStatusLabel.config(foreground="red")
                self.gameRunning = False
                Thread(target=self.gameServer.close).start()
                self.gameServer = None
                self.gameThread = None
            else:
                self._popup('Cannot Close Server',
                    'The game has begun, so the server cannot be closed')

    def _runBroadcastServer(self):
        # TODO - Add server logic here
        if not self.broadcastRunning:
            self.broadcastStatus.set("Server Running")
            self.broadcastButtonLabel.set("Stop")
            self.broadcastStatusLabel.config(foreground="green")
            self.broadcastRunning = True
        else:
            self.broadcastStatus.set("Server Stopped")
            self.broadcastButtonLabel.set("Start")
            self.broadcastStatusLabel.config(foreground="red")
            self.broadcastRunning = False

    def _popup(self, title, message):
        popup = Toplevel(self)
        popup.title(title)

        Message(popup, text=message).pack()

        Button(popup, command=popup.destroy, text="Close").pack()

    def _close(self):
        # Ensure all services are closed before closing
        # Also write out log file
        if self.gameRunning:
            # If the game has started, do not close the game

    def logMessage(self, message):
        # Takes in a message from an external source and adds it to the server
        # log with a time stamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = '[%s] - %s' % (timestamp, message)
        self.messages.append(log_message)
        self.num_messages += 1
        if self.num_messages > self.max_messages:
            self.messages.popleft()
            self.num_messages -= 1
        self.log.set('\n'.join(self.messages))

if __name__ == '__main__':
    a = ArenaGUI(None)
    a.mainloop()
