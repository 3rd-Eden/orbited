from listener import Event, SocketIO, Timer, Signal, contains
import select, signal
try:
    import epoll
except ImportError:
    epoll = None

LISTEN_TIME = .0001

class Registrar(object):
    def __init__(self):
        self.events = {'read':{},'write':{}}
        self.timers = []
        self.signals = {}
        self.run_dispatch = False
        self.error_check = False

    def signal_add(self, sig):
        self.signals[sig.sig] = sig

    def signal_remove(self, sig):
        if sig in self.signals:
            del self.signals[sig]

    def init(self):
        for sig in self.signals:
            self.signals[sig].reset()
        self.__init__()

    def event(self,callback,arg,evtype,handle):
        return Event(self,callback,arg,evtype,handle)

    def read(self,sock,cb,*args):
        tmp = SocketIO(self,'read',sock,cb,*args)
        self.add(tmp)
        return tmp

    def write(self,sock,cb,*args):
        tmp = SocketIO(self,'write',sock,cb,*args)
        self.add(tmp)
        return tmp

    def dispatch(self):
        self.run_dispatch = True
        while self.run_dispatch:
            if not self.loop():
                self.run_dispatch = False

    def loop(self):
        e = self.check_events()
        t = self.check_timers()
        return e or t or self.signals

    def abort(self):
        self.run_dispatch = False

    def signal(self,sig,cb,*args):
        return Signal(self,sig,cb,*args)

    def timeout(self,delay,cb,*args):
        tmp = Timer(delay,cb,*args)
        self.timers = [tmp]+self.timers
        return tmp

    def check_timers(self):
        active = False
        for timer in self.timers:
            if not timer.check():
                self.timers.remove(timer)
                self.timers.append(timer)
                break
            active = True
        return active

    def handle_error(self, fd):
        if fd in self.events['read']:
            self.events['read'][fd].callback()
        if fd in self.events['write']:
            self.events['write'][fd].callback()

class SelectRegistrar(Registrar):
    def __init__(self):
        Registrar.__init__(self)

    def add(self, event):
        self.events[event.evtype][event.fd] = event

    def remove(self, event):
        if event.fd in self.events[event.evtype]:
            del self.events[event.evtype][event.fd]

    def check_events(self):
        if self.events['read'] or self.events['write']:
            rlist = self.events['read'].keys()
            wlist = self.events['write'].keys()
            try:
                r,w,e = select.select(rlist,wlist,rlist+wlist,LISTEN_TIME)
            except select.error:
                if signal.SIGINT in self.signals:
                    return True
                raise KeyboardInterrupt
            for fd in r:
                self.events['read'][fd].callback()
            for fd in w:
                self.events['write'][fd].callback()
            for fd in e:
                self.handle_error(fd)
            return True
        return False

class PollRegistrar(Registrar):
    def __init__(self):
        Registrar.__init__(self)
        self.poll = select.poll()

    def add(self, event):
        self.events[event.evtype][event.fd] = event
        self.register(event.fd)

    def remove(self, event):
        if event.fd in self.events[event.evtype]:
            del self.events[event.evtype][event.fd]
            self.poll.unregister(event.fd)
            self.register(event.fd)

    def check_events(self):
        if self.events['read'] or self.events['write']:
            try:
                items = self.poll.poll(LISTEN_TIME)
            except select.error:
                if signal.SIGINT in self.signals:
                    return True
                raise KeyboardInterrupt
            for fd,etype in items:
                if contains(etype,select.POLLIN):
                    self.events['read'][fd].callback()
                if contains(etype,select.POLLOUT):
                    self.events['write'][fd].callback()
                if contains(etype,select.POLLERR) or contains(etype,select.POLLHUP):
                    self.handle_error(fd)
            return True
        return False

    def register(self, fd):
        mode = 0
        if fd in self.events['read']:
            mode = mode|select.POLLIN
        if fd in self.events['write']:
            mode = mode|select.POLLOUT
        if mode:
            self.poll.register(fd, mode)

class EpollRegistrar(PollRegistrar):
    def __init__(self):
        Registrar.__init__(self)
        self.poll = epoll.poll()