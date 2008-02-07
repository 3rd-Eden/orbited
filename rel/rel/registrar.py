from listener import Event, Timer
import select
try:
    import epoll
except ImportError:
    epoll = None

LISTEN_TIME = .0001

class Registrar(object):
    def __init__(self):
        self.events = {'read':{},'write':{}}
        self.timers = {}
        self.run_dispatch = False

    def read(self,sock,cb,*args):
        tmp = Event('read',sock,cb,*args)
        self.add(tmp)
        return tmp

    def write(self,sock,cb,*args):
        tmp = Event('write',sock,cb,*args)
        self.add(tmp)
        return tmp

    def dispatch(self):
        self.run_dispatch = True
        while self.run_dispatch:
            self.loop()
            self.check_timers()

    def abort(self):
        self.run_dispatch = False

    def timeout(self,delay,cb,*args):
        tmp = Timer(delay,cb,*args)
        self.timers[(delay,cb,args)] = tmp
        return tmp

    def check_timers(self):
        for timer in self.timers:
            self.timers[timer].check()

    def handle_error(self, fd):
        if fd in self.events['read']:
            self.events['read'][fd].ready()
        elif fd in self.events['write']:
            self.events['write'][fd].ready()
        else:
            print 'Registered Event Listener error on socket:',fd

class SelectRegistrar(Registrar):
    def __init__(self):
        Registrar.__init__(self)

    def add(self, event):
        self.events[event.ev_type][event.fd] = event

    def remove(self, event):
        if event.fd in self.events[event.ev_type]:
            del self.events[event.ev_type][event.fd]

    def loop(self):
        rlist = self.events['read'].keys()
        wlist = self.events['write'].keys()
        r,w,e = select.select(rlist,wlist,rlist+wlist,LISTEN_TIME)
        for fd in r:
            self.events['read'][fd].ready()
        for fd in w:
            self.events['write'][fd].ready()
        for fd in e:
            self.handle_error(fd)

class PollRegistrar(Registrar):
    def __init__(self):
        Registrar.__init__(self)
        self.poll = select.poll()

    def add(self, event):
        self.events[event.ev_type][event.fd] = event
        self.register(event.fd)

    def remove(self, event):
        if event.fd not in self.events[event.ev_type]:
            return
        del self.events[event.ev_type][event.fd]
        self.poll.unregister(event.fd)
        self.register(event.fd)

    def loop(self):
        items = self.poll.poll(LISTEN_TIME)
        for fd,etype in items:
            if self.is_registered(etype,select.POLLIN):
                self.events['read'][fd].ready()
            elif self.is_registered(etype,select.POLLOUT):
                self.events['write'][fd].ready()
            elif self.is_registered(etype,select.POLLERR) or self.is_registered(etype,select.POLLHUP):
                self.handle_error(fd)

    def register(self, fd):
        mode = 0
        if fd in self.events['read']:
            mode = mode|select.POLLIN
        if fd in self.events['write']:
            mode = mode|select.POLLOUT
        if mode == 0:
            return False
        self.poll.register(fd, mode)

    def is_registered(self,mode,bit):
        return mode&bit==bit

class EpollRegistrar(PollRegistrar):
    def __init__(self):
        Registrar.__init__(self)
        self.poll = epoll.poll()