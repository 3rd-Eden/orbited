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
from registrar import SelectRegistrar, PollRegistrar, EpollRegistrar
try:
    import event as pyevent
except:
    pyevent = None

registrar = None

mapping = {
    'select': SelectRegistrar,
    'epoll': EPollRegistrar,
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

def dispatch():
    check_init()
    registrar.dispatch()
