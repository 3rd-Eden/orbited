import rel as event
#from orbited.logger import get_logger
from dez import io
from dez.buffer import Buffer
from logging import default_get_logger
from router import Router
from response import RawHTTPResponse, HTTPResponse
from request import HTTPRequest

class HTTPDaemon(object):
    
    def __init__(self, host, port, get_logger=default_get_logger):
        
        self.log = get_logger("HTTPDaemon")
        self.get_logger = get_logger
        self.host = host
        self.port = port
        self.log.info("Listening on %s:%s" % (host, port))
        self.sock = io.server_socket(self.port)
#        self.listen = event.event(self.accept_connection, 
#            handle=self.sock, evtype=event.EV_READ | event.EV_PERSIST)
        self.listen = event.read(self.sock, self.accept_connection, None, self.sock, None)
        #self.listen.add()
        self.router = Router(self.default_cb)
        self.num_open = 0
        self.max_open = 0
        
    def register_prefix(self, prefix, cb):
        self.router.register_prefix(prefix, cb)

    def register_catch(self, cb):
        self.default_cb = cb

    def closed(self):
        self.num_open -= 1

    def default_404_cb(self, request):
        r = HTTPResponse(request)
        r.status = "404 Not Found"
        r.write("The requested document %s was not found" % request.url)
#        r.write_status(404, "Not Found")
#        data = "The requested document %s was not found" % request.url
#        r.write_header("Content-length", len(data))
#        r.write_headers_end()
#        r.write(data)
#        r.end()
        r.dispatch()

    def default_cb(self, request):
        return self.default_404_cb(request)

    def accept_connection(self, ev, sock, event_type, *arg):
#        self.num_open += 1
#        if self.num_open > self.max_open:
#            self.max_open = self.num_open
#            print "New max concurrency:", self.max_open
#        self.log.info('Accept Connection, ev: %s, sock: %s, event_type: %s, *arg: %s' % (ev, sock.fileno(), event_type, arg))
        sock, addr = sock.accept()
        HTTPConnection(sock, addr, self.router, self.get_logger,self.closed)                
        return True
                


class HTTPConnection(object):
    id = 0
    def __init__(self, sock, addr, router, get_logger, closecb):
        self.closecb = closecb
        self.log = get_logger("HTTPConnection")
        self.get_logger = get_logger
        HTTPConnection.id += 1
        self.id = HTTPConnection.id
        print 'Incoming HTTP Connection with id %s, fileno %s' % (self.id, sock.fileno())
        self.sock = sock
        self.addr, self.local_port = addr
        self.router = router
        self.response_queue = []
        self.current_cb = None
        self.current_args = None
        self.wevent = None
        self.start_request()
        
    def start_request(self):
        self.wevent = None
        self.revent = event.read(self.sock, self.read_ready)
        self.request = HTTPRequest(self)
        self.write_buffer = Buffer(mode='consume')
        self.buffer = Buffer()        
        self.state = "read"
        
    def close(self, reason=""):
        self.closecb()
        if self.revent:
            self.revent.delete()
            self.revent = None
        if self.wevent:
            self.wevent.delete()
            self.wevent = None
#        self.sock.shutdown(io.socket.SHUT_RDWR)
        self.sock.close()
    
    def read_ready(self):
        try:
            data = self.sock.recv(io.BUFFER_SIZE)
            if not data:
                self.close()
                return None
            return self.read(data)
        except io.socket.error:
            self.close()
            return None

    def read(self, data):
        if self.state != "read":
            self.log.error("Invalid additional data: %s" % data)
            self.close()
        self.buffer += data
        self.request.process()
        if self.request.headers_complete:
            self.revent.delete()
            self.revent = None
            dispatch_cb = self.router(self.request.url)
            dispatch_cb(self.request)
            return None
        return True
            
            
    def write(self, data, cb, args):
        self.response_queue.append((data, cb, args))
        if not self.wevent:
            self.wevent = event.write(self.sock, self.write_ready)
        
        
    def write_ready(self):
        if self.write_buffer.empty():
            if self.current_cb:
                cb = self.current_cb
                args = self.current_args
                cb(*args)
                self.current_cb = None
            if not self.response_queue:
                self.current_cb = None
                self.current_response = None
                self.wevent = None
                return None
            data, self.current_cb, self.current_args = self.response_queue.pop(0)            
            self.write_buffer.reset(data)
            # call conn.write("", cb) to signify request complete
            if data == "":
                self.wevent = None
                return None
        try:
            bsent = self.sock.send(self.write_buffer.get_value())
            self.write_buffer.move(bsent)
            self.log.debug('write_buffer: return True')
            return True
        except io.socket.error, msg:
            self.log.debug('io.socket.error: %s' % msg)
            self.close(reason=str(msg))
            return None
        
