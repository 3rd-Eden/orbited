import event
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
        self.listen = event.read(self.sock, self.accept_connection)
        self.router = Router(self.default_cb)
        
    def register_url(self, url, cb):
        pass
    
    def register_prefix(self, prefix, cb):
        self.router.register_prefix(prefix, cb)

    def register_catch(self, cb):
        self.default_cb = cb

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

    def accept_connection(self):
        opened_sock, addr = self.sock.accept()
#        self.log.info('Accept Connection, ev: %s, sock: %s, event_type: %s, *arg: %s' % (ev, sock.fileno(), event_type, arg))
        HTTPConnection(opened_sock, addr, self.router, self.get_logger)
    


class HTTPConnection(object):
    id = 0
    def __init__(self, sock, addr, router, get_logger):
        self.log = get_logger("HTTPConnection")
        self.get_logger = get_logger
        HTTPConnection.id += 1
        self.id = HTTPConnection.id
        self.log.info('Incoming HTTP Connection with id %s, fileno %s' % (self.id, sock.fileno()))
        self.sock = sock
        self.addr, self.local_port = addr
        self.router = router
        self.response_queue = []
        self.current_cb = None
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
            
            
    def write(self, data, cb):
        self.response_queue.append((data, cb))
        if not self.wevent:
            self.wevent = event.write(self.sock, self.write_ready)
        
        
    def write_ready(self):
        if self.write_buffer.empty():
            if self.current_cb:
                cb = self.current_cb[0]
                args = self.current_cb[1]
                cb(args)
                self.current_cb = None
            if not self.response_queue:
                self.current_cb = None
                self.current_response = None
                return None
            data, self.current_cb = self.response_queue.pop(0)            
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
        
