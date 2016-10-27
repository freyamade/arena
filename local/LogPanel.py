from tkinter import *

class LogPanel(LabelFrame):

    def __init__(self, master, title, width, height):
        super(LogPanel, self).__init__(master=master, text=title,
            width=width, height=height)
        self._initialiseVariables()
        self._initialiseChildren()

    def _initialiseVariables(self):
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
