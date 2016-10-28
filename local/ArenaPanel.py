from tkinter import *

class ArenaPanel(LabelFrame):

    def __init__(self, master, title, width, height, *args, **kwargs):
        super(ArenaPanel, self).__init__(master, text=title,
            width=width, height=height)
        self._master = master
        self._initialiseVariables(*args, **kwargs)
        self._initialiseChildren()

    def _initialiseVariables(self, *args, **kwargs):
        raise NotImplemented("This method must be overrided")

    def _initialiseChildren(self):
        raise NotImplemented("This method must be overrided")

    def close(self):
        raise NotImplemented("This method must be overrided")

    def _popup(self, title, message):
        popup = Toplevel(self._master)
        popup.title(title)

        Label(popup, text=message).pack(fill=BOTH, expand=1)

        Button(popup, command=popup.destroy, text="Close").pack(fill=BOTH,
            expand=1)
