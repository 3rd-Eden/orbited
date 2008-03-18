"""
R.E.L.
Registed Event Listener
module that uses various methods to emulate event-like behavior
functions:
    read(socket, callback, *args)
    write(socket, callback, *args)
    timeout(delay, callback, *args)
    signal(sig, callback, *args)
    event(callback,arg=None,evtype=0,handle=None)
    dispatch()
    loop()
    abort()
    init()
"""
import sys, threading, time
from registrar import SelectRegistrar, PollRegistrar, EpollRegistrar
from listener import EV_PERSIST, EV_READ, EV_SIGNAL, EV_TIMEOUT, EV_WRITE
try:
    import event as pyevent
except:
    pyevent = None

registrar = None
threader = None

mapping = {
    'select': SelectRegistrar,
    'epoll': EpollRegistrar,
    'poll': PollRegistrar,
}

class Thread_Checker(object):
    def __init__(self):
        self.go()

    def go(self):
        return
        if registrar != pyevent:
            return
        self.checker = timeout(1,self.check)
        self.sleeper = event(self.release)

    def stop(self):
        return
        if registrar != pyevent:
            return
        self.checker.delete()
        self.sleeper.delete()

    def release(self, *args):
        time.sleep(.001)
        return True

    def check(self):
        if threading.activeCount() > 1:
            self.sleeper.add(.01)
        else:
            self.sleeper.delete()
        return True

def check_init():
    if not registrar:
        print "rel.initialize not called. Trying event notification methods in default order: pyevent,epoll,poll,select"
        initialize()

def get_registrar(method):
    if method == 'pyevent':
        if not pyevent:
            raise ImportError, "could not import event"
        return pyevent
    if method in mapping:
        return mapping[method]()
    raise ImportError

def initialize(methods=['pyevent','epoll','poll','select']):
    global registrar
    global threader
    for method in methods:
        try:
            registrar = get_registrar(method)
            break
        except:
            pass
    if registrar is None:
        raise ImportError, "Could not import any of given methods: %s" % (methods,)
    threader = Thread_Checker()
    print 'Registered Event Listener initialized with method:',method

def read(sock,cb,*args):
    check_init()
    return registrar.read(sock,cb,*args)

def write(sock,cb,*args):
    check_init()
    return registrar.write(sock,cb,*args)

def timeout(delay, cb, *args):
    check_init()
    return registrar.timeout(delay,cb,*args)

def signal(sig, callback, *args):
    check_init()
    return registrar.signal(sig,callback,*args)

def dispatch():
    check_init()
    registrar.dispatch()

def loop():
    check_init()
    registrar.loop()

def abort():
    check_init()
    registrar.abort()

def init():
    check_init()
    threader.stop()
    registrar.init()
    threader.go()

def event(callback,arg=None,evtype=0,handle=None):
    check_init()
    return registrar.event(callback,arg,evtype,handle)