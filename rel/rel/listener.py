import time
import signal

EV_PERSIST = 16
EV_READ = 2
EV_SIGNAL = 8
EV_TIMEOUT = 1
EV_WRITE = 4

def contains(mode,bit):
    return mode&bit==bit

class Event(object):
    def __init__(self,registrar,cb,arg,evtype,handle):
        self.registrar = registrar
        self.cb = cb
        self.arg = arg
        if not evtype:
            evtype = EV_TIMEOUT
        self.evtype = evtype
        self.handle = handle
        self.children = []
        self.spawn_children()

    def spawn_children(self):
        persist = False
        if contains(self.evtype,EV_PERSIST):
            persist = True
        if contains(self.evtype,EV_TIMEOUT):
            self.children.append(self.registrar.timeout(0,self.callback))
        if contains(self.evtype,EV_SIGNAL):
            self.children.append(self.registrar.signal(self.handle,self.callback))
        if contains(self.evtype,EV_READ):
            tmp = self.registrar.read(self.handle,self.callback)
            if persist:
                tmp.persistent()
            self.children.append(tmp)
        if contains(self.evtype,EV_WRITE):
            tmp = self.registrar.write(self.handle,self.callback)
            if persist:
                tmp.persistent()
            self.children.append(tmp)

    def add(self, delay=0):
        for child in self.children:
            child.add(delay)

    def delete(self):
        for child in self.children:
            child.delete()

    def pending(self):
        for child in self.children:
            if child.pending():
                return 1
        return 0

    def callback(self):
        self.cb(self,self.handle,self.evtype,self.arg)

class SocketIO(object):
    def __init__(self, registrar, evtype, sock, cb, *args):
        self.registrar = registrar
        self.evtype = evtype
        self.sock = sock
        self.fd = self.sock
        if hasattr(self.fd,'fileno'):
            self.fd = self.fd.fileno()
        self.cb = cb
        self.persist = False
        self.args = args

    def persistent(self):
        self.persist = True

    def ready(self):
        outcome = self.cb(*self.args)
        if not self.persist and outcome is None:
            self.delete()

    def pending(self):
        return 1

    def add(self, delay=0):
        pass

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
        if not self.pending():
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
        if not self.pending():
            return False
        if time.time() >= self.expiration:
            value = self.cb(*self.args)
            self.delete()
            if value:
                self.add()
        return True