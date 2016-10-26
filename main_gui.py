from tkinter import *
from server import ArenaServer

class ArenaGUI(Tk):

    def __init__(self, master):
        super(ArenaGUI, self).__init__(master)
        self.title("Arena Server")
        self.resizable(0, 0)
        self.minsize(width=700, height=650)
        self._initialiseServerPanel()
        self._initialiseStatusPanel()
        self._initialiseLobbyPanel()

    def _initialiseServerPanel(self):
        serverPanel = LabelFrame(self, text="Server Log", width=350,
            height=650)
        serverPanel.grid(row=0, column=0, rowspan=2)

        serverLog = Listbox(serverPanel)
        serverLog.grid(row=0, column=0)

    def _initialiseStatusPanel(self):
        statusPanel = LabelFrame(self, text="Service Statuses", width=350,
            height=325)
        statusPanel.grid(row=0, column=1)

    def _initialiseLobbyPanel(self):
        lobbyPanel = LabelFrame(self, text="Lobby Status", width=350,
            height=325)
        lobbyPanel.grid(row=1, column=1)

if __name__ == '__main__':
    a = ArenaGUI(None)
    a.mainloop()
