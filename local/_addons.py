class PanelException(Exception):
    """An Exception that can be raised by an inner panel class that will
    result in the mainloop creating a popup"""

    def __init__(self, message, title):
        super(PanelException, self).__init__(message=message)
        self.title = title
