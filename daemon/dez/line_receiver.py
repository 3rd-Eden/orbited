import event
import io
from buffer import Buffer

class SocketClient(object):
    def __init__(self,cb=None):
        self.cb = cb
        self.started = False

    def connect(self,hostname,port):
        s = io.client_socket(hostname,port)
        conn = Connection((hostname,port), s)
        print 'calling cb'
        self.cb(conn)
        print 'starting'
        if not self.started:
            self.start()

    def start(self):
        self.started = True
        event.signal(2,event.abort)
        event.dispatch()
        

class SocketDaemon(object):
    def __init__(self, hostname, port, cb=None):
        self.hostname = hostname
        self.port = port
        self.sock = io.server_socket(self.port)
        self.cb = cb
        self.listen = event.read(self.sock,self.accept_connection)

    def accept_connection(self):
        sock, addr = self.sock.accept()
        conn = Connection(addr, sock)
        if self.cb:
            self.cb(conn)
        return True

    def start(self):
        event.signal(2,event.abort)
        event.dispatch()

class Connection(object):
    def __init__(self, addr, sock):
        self.addr = addr
        self.sock = sock
        self.delimiter = None
        self.size = None
        self.read_cb = None
        self.write_cb = None
        self.response_queue = []
        self.wevent = event.write(self.sock, self.write_ready)
        self.wevent.delete() # don't schedule it yet
        self.revent = event.read(self.sock, self.read_ready)
        self.revent.delete() # don't schedule it yet
        self.buffer = Buffer()
        self.write_buffer = Buffer(mode='consume')
        self.mode = "pause"

    def close(self, reason=""):
        if self.revent:
            self.revent.delete()
            self.revent = None
        if self.wevent:
            self.wevent.delete()
            self.wevent = None
        self.sock.close()
        if self.mode == "close":
            self.read_cb(self.buffer.get_value())

    def set_mode_size(self, size, cb):
        paused = self.mode == "pause"
        self.mode = "size"
        self.read_cb = cb
        self.size = size
        if paused:
            self.unpause()
    def set_mode_close(self, cb):
        paused = self.mode == "pause"
        self.mode = "close"
        self.read_cb = cb
        if paused:
            self.unpause()
        
    def set_mode_delimiter(self, delimiter, cb):
        paused = self.mode == "pause"
        self.mode = "delim"
        self.read_cb = cb
        self.delimiter = delimiter
        if paused:
            self.unpause()

    def unpause(self):
        self.revent.add()

    def write(self, data, cb=None, cbargs=None, eb=None, ebargs=None):
        self.response_queue.append((data, cb, cbargs, eb, ebargs))
        if not self.wevent.pending():
            self.wevent.add()

    def write_ready(self):
        # Keep a queue of things to write and their related callbacks
        # if we just finished writing some segment, call its callback
        # if there are no more segments, then stop
        if self.write_buffer.empty():
            if self.write_cb:
                cb = self.write_cb
                args = self.write_args
                if args is None:
                    args = []
                cb(*args)
                self.write_cb = None
            if not self.response_queue:
                self.write_cb = None
                self.write_response = None
                return None # self.wevent.delete()
            data, self.write_cb, self.write_args, self.write_eb, self.write_ebargs = self.response_queue.pop(0)
            self.write_buffer.reset(data)
        try:
            bsent = self.sock.send(self.write_buffer.get_value())
            self.write_buffer.move(bsent)
            return True
        except io.socket.error, msg:
            self.close(reason=str(msg))
            self.write_eb(self.write_ebargs)
            # also loop through response queue and call errbacks
            return None

    def rmode_delim(self):
        i = self.buffer.find(self.delimiter)
        if i == -1:
            return None
        data = self.buffer.part(0,i)
        self.buffer.move(i+len(self.delimiter))
        return data

    def rmode_size(self):
        if len(self.buffer) < self.size:
            return None
        data = self.buffer.part(0, self.size)
        self.buffer.move(self.size)
        return data
    
    def rmode_close(self):
        return None

    def rmode_pause(self):
        return None

    def read_ready(self):
        try:
            data = self.sock.recv(io.BUFFER_SIZE)
        except io.socket.error:
            self.close()
            return None
        if not data:
            self.close()
            return None
        self.read(data)
        return True

    def read(self, data):
        self.buffer += data
        while True:
            data = getattr(self, 'rmode_%s' % self.mode)()
            if data is None:
                break
            self.read_cb(data)

    def pause(self):
        self.mode = "pause"
        self.read_cb = None
        self.size = None
        self.delimiter = None
        self.revent.delete()