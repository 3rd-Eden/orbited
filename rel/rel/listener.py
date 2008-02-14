import time
import signal

class SocketIO(object):
    def __init__(self, registrar, evtype, sock, cb, *args):
        self.registrar = registrar
        self.evtype = evtype
        self.sock = sock
        self.fd = self.sock.fileno()
        self.cb = cb
        self.args = args

    def ready(self):
        outcome = self.cb(*self.args)
        if outcome is None:
            self.delete()

    def delete(self):
        self.registrar.remove(self)

class Signal(object):
    def __init__(self, sig, cb, *args):
        self.sig = sig
        self.default = signal.getsignal(self.sig)
        self.cb = cb
        self.args = args
        self.add()

    def add(self, delay=0):
        self.expiration = None
        if delay:
            self.expiration = time.time()+delay
        signal.signal(self.sig,self.callback)
        self.active = True

    def delete(self):
        signal.signal(self.sig,self.default)
        self.active = False

    def pending(self):
        if self.active:
            return 1
        return 0

    def check(self):
        if not self.active:
            return False
        elif self.expiration and time.time() >= self.expiration:
            self.callback()
            self.delete()
        return True

    def callback(self,*args):
        self.cb(*self.args)

class Timer(object):
    def __init__(self, delay, cb, *args):
        self.cb = cb
        self.args = args
        self.delay = delay
        self.expiration = None
        self.add()

    def add(self, delay=None):
        self.delay = delay or self.delay
        if self.delay:
            self.expiration = time.time()+self.delay

    def delete(self):
        self.expiration = None

    def pending(self):
        if self.expiration:
            return 1
        return 0

    def check(self):
        if not self.expiration:
            return False
        if time.time() >= self.expiration:
            value = self.cb(*self.args)
            if value:
                self.add()
            else:
                self.delete()
        return True