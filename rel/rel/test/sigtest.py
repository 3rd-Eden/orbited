import os,signal,time
import rel as event

def test_signal():
    starttime = time.time()
    def __signal_cb(ev, sig, evtype, arg):
        print "TIMER [test_signal]:",time.time()-starttime
        if evtype == event.EV_SIGNAL:
            ev.delete()
        elif evtype == event.EV_TIMEOUT:
            os.kill(os.getpid(), signal.SIGUSR1)
    print 'test_signal'
    event.event(__signal_cb, handle=signal.SIGUSR1,
                evtype=event.EV_SIGNAL).add()
    event.event(__signal_cb).add(2)
    event.dispatch()

def test_signal2():
    starttime = time.time()
    def __signal2_cb(sig=None):
        print "TIMER [test_signal2]:",time.time()-starttime
        if sig:
            event.abort()
        else:
            os.kill(os.getpid(), signal.SIGUSR1)
    print 'test_signal2'
    event.signal(signal.SIGUSR1, __signal2_cb, signal.SIGUSR1)
    event.timeout(2, __signal2_cb)
    event.dispatch()

if __name__ == '__main__':
    for method in ['pyevent','epoll','select','poll']:
        event.initialize([method])
        test_signal()
        event.init()
        test_signal2()
