from local import *
from threading import Thread
from tkinter import *

# TODO - Override the X button and ensure every service is closed
# TODO - Save all messages into a log file once the gui closes
#   File opens during init, writes out every time log message is called
#   and closes during the override of the X button or on a KeyboardInterrupt in console
# TODO - Display that server has closed when the game is over
# TODO - Display that the broadcast service has stopped when the game starts

class ArenaGUI(Tk):

    def __init__(self, master):
        # Set up the master window
        super(ArenaGUI, self).__init__(master)
        self.title("Arena Server")
        self.resizable(0, 0)
        self.minsize(width=750, height=650)
        self.protocol("WM_DELETE_WINDOW", self._close)

        self._initialiseLogPanel()
        self._initialiseStatusPanel()

    def _initialiseLogPanel(self):
        self._logPanel = LogPanel(self, "Server Log", 400, 650)
        self._logPanel.pack(side=LEFT, fill=BOTH, expand=1)

    def _initialiseStatusPanel(self):
        statusPanel = LabelFrame(self, text="Service Statuses", width=350,
            height=400)
        statusPanel.pack(fill=BOTH, expand=1, side=TOP)

        self._gameServerPanel = GameServerPanel(statusPanel,
            title="Game Server", width=300, height=650,
            logMessage=self._logPanel.logMessage)
        self._gameServerPanel.pack(expand=1, fill=BOTH)
        

    def _close(self):
        # Attempt to close every panel before closing the main window
        closing = True
        closing = closing and self._logPanel.close()
        # Test if the previous panel closed
        if not closing:
            self._popup('Log')
            return
        closing = closing and self._gameServerPanel.close()
        if not closing:
            self._popup('Game Server')
            return
        self.destroy()

    def _popup(self, panel):
        popup = Toplevel(self)
        popup.title('Panel failed to close')

        message = '%s failed to close' % (panel)
        Label(popup, text=message).pack(fill=BOTH, expand=1)

        Button(popup, command=popup.destroy, text="Close").pack(fill=BOTH,
            expand=1)

if __name__ == '__main__':
    a = ArenaGUI(None)
    a.mainloop()
