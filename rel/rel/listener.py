import time

class Event(object):
    def __init__(self, ev_type, sock, cb, *args):
        self.ev_type = ev_type
        self.sock = sock
        self.fd = self.sock.fileno()
        self.cb = cb
        self.args = args

    def ready(self):
        outcome = self.cb(*self.args)
        if outcome is None:
            self.delete()

    def delete(self):
        registrar.remove(self)

class Timer(object):
    def __init__(self, delay, cb, *args):
        self.cb = cb
        self.args = args
        self.add(delay)

    def add(self, delay):
        self.expiration = time.time()+delay

    def delete(self):
        self.expiration = None

    def pending(self):
        if self.expiration:
            return 1
        return 0

    def check(self):
        if self.expiration and time.time() >= self.expiration:
            self.delete()
            self.cb(*self.args)