class PanelException(Exception):
    """An Exception that can be raised by an inner panel class that will
    result in the mainloop creating a popup"""

    def __init__(self, title, message):
        super(PanelException, self).__init__(message)
        self.title = title
