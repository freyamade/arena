from collections import deque
from datetime import datetime
from local import *
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
        # self.protocol("WM_DELETE_WINDOW", self._close)

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

        self.gameServer = None
        self.gameThread = None

        self.logMessage("Welcome to the Arena!")

    def _initialiseServerPanel(self):
        self._logPanel = LogPanel(self, "Server Log", 400, 650)
        self._logPanel.pack(side=LEFT, fill=BOTH, expand=1)

    def _initialiseStatusPanel(self):
        statusPanel = LabelFrame(self, text="Service Statuses", width=350,
            height=400)
        statusPanel.pack(fill=BOTH, expand=1, side=TOP)

        self._initialiseGameServerPanel(statusPanel)

    def _initialiseGameServerPanel(self, parent):
        self._gameServerPanel = GameServerPanel(parent, title="Game Server",
            width=300, height=150, logMethod=self.logMessage,
            runHandler=self._runGameServer,
            broadcastHandler=self._runBroadcastServer)
        self._gameServerPanel.pack(expand=1, fill=BOTH)

    def _initialiseLobbyPanel(self):
        lobbyPanel = LabelFrame(self, text="Lobby Status", width=350,
            height=250)
        lobbyPanel.pack(fill=BOTH, expand=1, side=TOP)

    def _runGameServer(self):
        # Wrapper for the game panel toggle method, to allow graceful exception
        try:
            self._gameServerPanel.toggle()
        except PanelException as e:
            self._popup(e.title, e.args)

    def _runBroadcastServer(self):
        # Wrapper for the game panel broadcast method for exception handling
        try:
            self._gameServerPanel.broadcast()
        except PanelException as e:
            self._popup(e.title, e.args)

    def _popup(self, title, message):
        popup = Toplevel(self)
        popup.title(title)

        Label(popup, text=message).pack(fill=BOTH, expand=1)

        Button(popup, command=popup.destroy, text="Close").pack(fill=BOTH,
            expand=1)

    # def _close(self):
    #     # Ensure all services are closed before closing
    #     # Also write out log file
    # Put canClose methods into the panels
    #     if self.gameRunning:
    #         # If the game has started, do not close the game

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

        self._logPanel.setLog('\n'.join(self.messages))

if __name__ == '__main__':
    a = ArenaGUI(None)
    a.mainloop()
