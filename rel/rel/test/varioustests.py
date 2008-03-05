import rel, os
from dez import io

def sock_cb():
    print 'connection'

def test_sock():
    sock = io.server_socket(9999)
    rel.read(sock, sock_cb)

def timeout_cb(msg):
    print 'timeout_cb',msg

def test_timeout():
    rel.timeout(5, timeout_cb, 'yo')

sig_index = 0
def signal_cb(msg):
    global sig_index
    sig_index += 1
    if sig_index == 5:
        rel.abort()
    print 'signal test:',msg

def test_signal():
    rel.signal(2, signal_cb, 'signal test complete')

def read_cb(fd):
    print 'read_cb',os.read(fd, 1024)
    return True

def write_cb(fd):
    os.write(fd, "what's up homie?")
    return True

def test_pipe():
    r, w = os.pipe()
    rel.read(r, read_cb, r)
    rel.timeout(1, write_cb, w)

def main():
    test_sock() # works!
    test_pipe() # works!
    test_timeout() # works!
    test_signal() # works!
    rel.dispatch()

if __name__ == "__main__":
    import sys
    method = "pyevent"
    if len(sys.argv) > 1:
        method = sys.argv[1]
    rel.initialize([method])
    main()