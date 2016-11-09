from local import *
from threading import Thread
from tkinter import *

"""/*
    Class: ArenaGUI
    Top level GUI interface for managing the Arena's server
*/"""
class ArenaGUI(Tk):

    # Group: Constructors

    """/*
        Constructor: __init__
        Initialises the main window, and creates the children <Panel>s

        Parameters:
            obj master - The parent of this window
    */"""
    def __init__(self, master):
        # Set up the master window
        super(ArenaGUI, self).__init__(master)
        self.title("Arena Server")
        self.resizable(0, 0)
        self.minsize(width=750, height=650)
        self.protocol("WM_DELETE_WINDOW", self._close)

        # Declare all variables here for doc purposes
        # Remove these for release code

        # Group: Variables

        # obj: _logPanel
        # <Panel> object maintaining any log messages produced by the server
        self._logPanel = None

        # obj: _gameServerPanel
        # <Panel> object providing graphical control for running the game
        # server
        self._gameServerPanel = None

        self._initialiseLogPanel()
        self._initialiseStatusPanel()

    # Group: Private Methods

    """/*
        Function: _initialiseLogPanel
        Creates a <LogPanel> instance, and adds it to the main window
    */"""
    def _initialiseLogPanel(self):
        self._logPanel = LogPanel(self, "Server Log", 400, 650)
        self._logPanel.pack(side=LEFT, fill=BOTH, expand=1)

    """/*
        Function: _initialiseStatusPanel
        Creates the status panel, which contains the <GameServerPanel>, and
        adds it to the main window
    */"""
    def _initialiseStatusPanel(self):
        statusPanel = LabelFrame(self, text="Service Statuses", width=350,
            height=400)
        statusPanel.pack(fill=BOTH, expand=1, side=TOP)

        self._gameServerPanel = GameServerPanel(statusPanel,
            title="Game Server", width=300, height=650,
            logMessage=self._logPanel.logMessage)
        self._gameServerPanel.pack(expand=1, fill=BOTH)
        
    """/*
        Function: _close
        Called when the user clicks the X button.
        Ensures all services are properly shutdown before
        closing the main window.
        If one of the <Panel> children cannot be closed, this method will
        create a popup
    */"""
    def _close(self):
        # Attempt to close every panel before closing the main window
        closing = True
        # Close the log panel last
        closing = closing and self._gameServerPanel.close()
        if not closing:
            self._popup('Game Server')
            return
        closing = closing and self._logPanel.close()
        # Test if the previous panel closed
        if not closing:
            self._popup('Log')
            return
        self.destroy()

    """/*
        Function: _popup
        Creates a popup window to display a message when the main window cannot
        be closed

        Parameters:
            string panel - The name of the <Panel> that failed to close
    */"""
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
