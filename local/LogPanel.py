from ._addons import PanelException
from .ArenaPanel import ArenaPanel
from tkinter import *

class LogPanel(ArenaPanel):

    def _initialiseVariables(self, *args, **kwargs):
        self._log = StringVar()
        self._log.set("")

    def _initialiseChildren(self):
        logLabel = Label(self, textvariable=self._log,
            anchor="sw", justify=LEFT)
        logLabel.pack(fill=BOTH, expand=1)

    def getLog(self):
        return self._log.get()

    def setLog(self, log):
        self._log.set(log)
