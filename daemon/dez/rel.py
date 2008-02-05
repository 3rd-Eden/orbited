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

##
# ask michael how to override init function
import time
# to make this only import for Registrar objects
##

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
        pass

class Registrar(object):
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

    def timeout(self,delay,cb,*args):
        return Timer(time.time()+delay,cb,*args)

    def handle_error(self,fd):
        print 'socket error:',fd

class SelectRegistrar(Registrar):
    def __init__(self):
        import select
        self.select = select.select
        self.events = {'read':{},'write':{}}

    def add(self, event):
        self.events[event.ev_type][event.fd] = event

    def remove(self, event):
        if event.fd in self.events[event.ev_type]:
            del self.events[event.ev_type][event.fd]

    def loop(self):
        rlist = self.events['read'].keys()
        wlist = self.events['write'].keys()
        r,w,e = self.select(rlist,wlist,rlist+wlist)
        for fd in r:
            self.events['read'][fd].ready()
        for fd in w:
            self.events['write'][fd].ready()
        for fd in e:
            self.handle_error(fd)

class PollRegistrar(Registrar):
    def __init__(self):
        import select
        self.select = select
        self.poll = self.select.poll()
        self.events = {'read': {}, 'write': {}}
        self.i = 0

    def add(self, event):
        self.events[event.ev_type][event.fd] = event
        self.register(event.fd)
        
    def register(self, fd):
        mode = 0
        if fd in self.events['read']:
            mode = mode|self.select.POLLIN
        if fd in self.events['write']:
            mode = mode|self.select.POLLOUT
        if mode == 0:
            return False
        self.poll.register(fd, mode)

    def remove(self, event):
        if event.fd not in self.events[event.ev_type]:
            return
#        print 'remove', event.ev_type, event.fd
        del self.events[event.ev_type][event.fd]
        self.poll.unregister(event.fd)
        self.register(event.fd)

    def loop(self):
#        self.i += 1
#        print self.i, 'loop'
        items = self.poll.poll()
        for fd,etype in items:
            if etype == self.select.POLLERR|self.select.POLLHUP:
                self.handle_error(fd)
                break
            elif etype == self.select.POLLIN:
                self.events['read'][fd].ready()
            elif etype == self.select.POLLOUT:
                self.events['write'][fd].ready()

    def handle_error(self, fd):
        if fd in self.events['read']:
            self.events['read'][fd].ready()
        elif fd in self.events['write']:
            self.events['write'][fd].ready()
            
class EPollRegistrar(PollRegistrar):
    def __init__(self):
        import epoll as select
        self.select = select
        self.poll = self.select.poll()
        self.events = {'read': {}, 'write': {}}
        self.i = 0

mapping = {
    'select': SelectRegistrar,
    'epoll': EPollRegistrar,
    'poll': PollRegistrar,
}

def get_registrar(method):
    if method == 'pyevent':
        import event
        return event
    if method in mapping:
        return mapping[method]()
    raise ImportError

registrar = None

def initialize(methods=['pyevent','select','poll','epoll']):
    global registrar
#    raise Exception, "..."
    for method in methods:
        try:
            registrar = get_registrar(method)
            break
        except ImportError:
            pass
    if registrar is None:
        raise ImportError, "Could not import any of given methods: %s" % (methods,)
    print 'Registered Event Listener initialized with method:',method
#    return reg

#registrar = initialize()

def read(sock,cb,*args):
    if not register:
        raise Exception, "must call initialize before using rel api"
    return registrar.read(sock,cb,*args)

def write(sock,cb,*args):
    if not register:
        raise Exception, "must call initialize before using rel api"
    return registrar.write(sock,cb,*args)

def timeout(delay, cb, *args):
    if not register:
        raise Exception, "must call initialize before using rel api"
    return registrar.timeout(delay,cb,*args)

def dispatch():
    registrar.dispatch()