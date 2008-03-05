"""
This is basically a direct copy of pyevent's test.py, with four differences:
    1) Changed:
        ""
        !/usr/bin/env python

        import glob, os, signal, sys, time, unittest
        sys.path.insert(0, glob.glob('./build/lib.*')[0])
        import event
        ""
       To:
        import os, signal, sys, time, unittest
        import rel as event
       The extra lines are basically there because you used to have to build pyevent instead of installing it with setup.py
    2) In test_signal2, I changed the first line from "def __signal2_cb(sig):" to "def __signal2_cb(sig=None):" and added an "event.dispatch()" at the end to activate this test. It apparently was deactivated because without the "sig=None", "event.timeout(2, __signal2_cb)" throws an error. This test also reveals what appears to be a strange pyevent bug.
    3) At the very bottom, changed "unittest.main()" to accommodate different event notification methods.
    4) Added a timer for each test method.
"""

import os, signal, sys, time, unittest
import rel as event

class EventTest(unittest.TestCase):
    def setUp(self):
        event.init()

    def test_timeout(self):
        starttime = time.time()
        def __timeout_cb(ev, handle, evtype, ts):
            print "TIMER [test_timeout]:",time.time()-starttime
            now = time.time()
            assert int(now - ts['start']) == ts['secs'], 'timeout failed'
        print 'test_timeout'
        ts = { 'start':time.time(), 'secs':5 }
        ev = event.event(__timeout_cb, arg=ts)
        ev.add(ts['secs'])
        event.dispatch()

    def test_timeout2(self):
        starttime = time.time()
        def __timeout2_cb(start, secs):
            print "TIMER [test_timeout2]:",time.time()-starttime
            dur = int(time.time() - start)
            assert dur == secs, 'timeout2 failed'
        print 'test_timeout2'
        event.timeout(5, __timeout2_cb, time.time(), 5)
        event.dispatch()

    def test_signal(self):
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

    def test_signal2(self):
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

    def test_read(self):
        starttime = time.time()
        def __read_cb(ev, fd, evtype, pipe):
            print "TIMER [test_read]:",time.time()-starttime
            buf = os.read(fd, 1024)
            assert buf == 'hi niels', 'read event failed'
        print 'test_read'
        pipe = os.pipe()
        event.event(__read_cb, handle=pipe[0],
                    evtype=event.EV_READ).add()
        os.write(pipe[1], 'hi niels')
        event.dispatch()

    def test_read2(self):
        starttime = time.time()
        def __read2_cb(fd, msg):
            print "TIMER [test_read2]:",time.time()-starttime
            assert os.read(fd, 1024) == msg, 'read2 event failed'
        print 'test_read2'
        msg = 'hello world'
        pipe = os.pipe()
        event.read(pipe[0], __read2_cb, pipe[0], msg)
        os.write(pipe[1], msg)
        event.dispatch()

if __name__ == '__main__':
    # pyevent alternatives: epoll, poll, select
    method = "pyevent"
    if len(sys.argv) > 1:
        method = sys.argv[1]
        sys.argv.remove(sys.argv[1])
    event.initialize([method])
    unittest.main()