class ParseError(Exception):
    def __init__(self, reason):
        self.reason = "\r\n==========\r\n%s\r\n=========="%reason

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        print self.reason
