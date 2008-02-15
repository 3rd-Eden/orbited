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
import sys
from registrar import SelectRegistrar, PollRegistrar, EpollRegistrar
from listener import EV_PERSIST, EV_READ, EV_SIGNAL, EV_TIMEOUT, EV_WRITE
try:
    import event as pyevent
except:
    pyevent = None

registrar = None

mapping = {
    'select': SelectRegistrar,
    'epoll': EpollRegistrar,
    'poll': PollRegistrar,
}

def check_init():
    if not registrar:
        print "rel.initialize not called. Trying event notification methods in default order: pyevent,epoll,select,poll"
        initialize()

def get_registrar(method):
    if method == 'pyevent':
        if not pyevent:
            raise ImportError, "could not import event"
        return pyevent
    if method in mapping:
        return mapping[method]()
    raise ImportError

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
    registrar.init()

def event(callback,arg=None,evtype=0,handle=None):
    check_init()
    return registrar.event(callback,arg,evtype,handle)