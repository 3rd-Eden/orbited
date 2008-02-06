"""
R.E.L.
Registed Event Listener
module that uses various methods to emulate event-like behavior
functions:
    read(socket, callback, *args)
    write(socket, callback, *args)
    timeout(delay, callback, *args)
    dispatch()
"""
import time
import select
try:
    import epoll
except ImportError:
    epoll = None
try:
    import event as pyevent
except:
    pyevent = None

LISTEN_TIME = .0001

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
    def __init__(self, expiration, cb, *args):
        self.cb = cb
        self.args = args
        self.add(expiration)

    def add(self, expiration):
        self.expiration = expiration

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

class Registrar(object):
    def __init__(self):
        self.events = {'read':{},'write':{}}
        self.timers = {}

    def read(self,sock,cb,*args):
        tmp = Event('read',sock,cb,*args)
        self.add(tmp)
        return tmp

    def write(self,sock,cb,*args):
        tmp = Event('write',sock,cb,*args)
        self.add(tmp)
        return tmp

    def dispatch(self):
        while True:
            self.loop()
            self.check_timers()

    def timeout(self,delay,cb,*args):
        t = time.time()
        tmp = Timer(t+delay,cb,*args)
        self.timers[(t,delay,cb)] = tmp
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

class EPollRegistrar(PollRegistrar):
    def __init__(self):
        Registrar.__init__(self)
        self.poll = epoll.poll()

mapping = {
    'select': SelectRegistrar,
    'epoll': EPollRegistrar,
    'poll': PollRegistrar,
}

def get_registrar(method):
    if method == 'pyevent':
        if not pyevent:
            raise ImportError, "could not import event"
        return pyevent
    if method in mapping:
        return mapping[method]()
    raise ImportError

registrar = None

def initialize(methods=['pyevent','epoll','select','poll']):
    global registrar
    for method in methods:
        try:
            registrar = get_registrar(method)
            break
        except ImportError:
            pass
    if registrar is None:
        raise ImportError, "Could not import any of given methods: %s" % (methods,)
    print 'Registered Event Listener initialized with method:',method

def read(sock,cb,*args):
    if not registrar:
        raise Exception, "must call initialize before using rel api"
    return registrar.read(sock,cb,*args)

def write(sock,cb,*args):
    if not registrar:
        raise Exception, "must call initialize before using rel api"
    return registrar.write(sock,cb,*args)

def timeout(delay, cb, *args):
    if not registrar:
        raise Exception, "must call initialize before using rel api"
    return registrar.timeout(delay,cb,*args)

def dispatch():
    if not registrar:
        raise Exception, "must call initialize before using rel api"
    registrar.dispatch()
