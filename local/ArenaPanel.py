from tkinter import *

class ArenaPanel(LabelFrame):

    def __init__(self, master, title, width, height, *args, **kwargs):
        super(ArenaPanel, self).__init__(master, text=title,
            width=width, height=height)
        self._initialiseVariables(*args, **kwargs)
        self._initialiseChildren()

    def _initialiseVariables(self, *args, **kwargs):
        raise NotImplemented("This method must be overrided")

    def _initialiseChildren(self):
        raise NotImplemented("This method must be overrided")
