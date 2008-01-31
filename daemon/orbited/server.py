import event
from orbited.logger import get_logger
from orbited import io
from orbited.buffer import Buffer


class HTTPDaemon(object):
    log = get_logger("HTTPDaemon")
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.log.info("Listening on %s:%s" % (host, port))
        self.sock = io.server_socket(self.port)
        self.listen = event.event(self.accept_connection, 
            handle=sock, evtype=event.EV_READ | event.EV_PERSIST)
        self.listen.add()
        self.router = Router(self.default_cb)
        
    def register_url(self, url, cb):
        pass
    
    def register_prefix(self, prefix, cb):
        pass

    def register_catch(self, cb):
        pass

    def default_404_cb(self, request):
        pass

    def accept_connection(self, ev, sock, event_type, *arg):
        logger.debug('Accept Connection, ev: %s, sock: %s, event_type: %s, *arg: %s' % (ev, sock, event_type, arg))
        sock, addr = sock.accept()
        HTTPConnection(self, sock, addr)
    


class HTTPConnection(object):
    id = 0
    log = get_logger("HTTPConnection")
    def __init__(self, sock, addr, dispatch_cb, read_body=True):
        HTTPConnection.id += 1
        self.id = HTTPConnection.id
        self.log.info('Creating HTTPConnection with id %s' % self.id)
        self.sock = sock
        self.addr, self.local_port = addr
        self.dispatch_cb = dispatch_cb
        self.response_queue = []
        self.current_cb = None
        self.start_request()
        
    def start_request(self):
        self.revent = event.read(self.sock, self.read_ready)
        self.request = HTTPRequest(self)
        self.write_buffer = Buffer(mode='consume')
        self.buffer = Buffer()        
        self.state = "read"
        
    def close(self):
        pass
    
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
        
        self.request.process()
        if request.headers_complete:
            self.revent.delete()
            self.revent = None
            self.dispatch_cb(self.request)
            return None
        return True
            
            
    def write(self, data, cb):
        self.response_queue.append((data, cb))
        if not self.wevent:
            self.wevent = event.write(self.sock, self.write_ready)
        
        
    def write_ready(self):
        if self.write_buffer.empty():
            self.current_cb()
            if not self.response_queue:
                self.current_cb = None
                self.current_response = None
                return None
            data, self.current_cb = self.response_queue.pop(0)
            self.write_buffer.reset(data)
        try:
            bsent = self.sock.send(self.write_buffer.get_value())
            self.log.debug('SEND: %s' % self.write_buffer.part(0,bsent))
            self.write_buffer.move(bsent)
            self.log.debug('write_buffer: return True')
            return True
        except io.socket.error, msg:
            self.logger.debug('io.socket.error: %s' % msg)
            self.close(reason=str(msg))
            return None
        
class HTTPRequest(object):
    log = get_logger('HTTPRequest')
    
    def __init__(self, conn):
        self.conn = conn
        self.state = 'action'
        self.headers = {}
        self.complete = False
        self.body = None
        self.body_cb = None
        self.body_stream_cb = None
        self.body_index = 0
            
    def process(self):
        return getattr(self, 'state_%s' % self.state)()        
    
    def state_action(self):
        if '\r\n' not in self.conn.buffer:
            return False
        i = self.conn.buffer.find('\r\n')
        self.action = self.conn.buffer.part(0,i)
        try:
            self.method, self.url, self.protocol = self.conn.buffer.part(0,i).split(' ',2)
        except ValueError:
            raise HTTPProtocolError, "Invalid HTTP status line"
        #self.protocol = self.protocol.lower()
        url_scheme, version = self.protocol.split('/',1)
        major, minor = version.split('.', 1)
        self.version_major = int(major)
        self.version_minor = int(minor)
        self.url_scheme = url_scheme.lower()
        self.conn.buffer.move(i+2)
        self.state = 'headers'
        return self.state_headers()
    
    def state_headers(self):
        while True:
            index = self.conn.buffer.find('\r\n')
            if index == -1:
                return False
            if index == 0:
                self.conn.buffer.move(2)
                self.state='headers_complete'
                return self.headers_complete()
            try:
                key, value = self.conn.buffer.part(0, index).split(': ')
            except ValueError:
                raise HTTPProtocolError, "Invalid HTTP header format"
            self.headers[key.lower()] = value
            self.conn.buffer.move(index+2)
            
            
    def state_headers_completed(self):
        self.content_length = int(self.headers.get('content-length', '0'))
        self.headers_complete = True
        return
    
    def read_body(self, cb):
        self.body_cb = cb
        self.state = 'body'
        return self.state_body()
    
    def read_body_stream(self, stream_cb)
        self.body_stream_cb = stream_cb
        self.state = 'body'
        return self.state_body()
        
    def state_body(self):
        if self.body_stream_cb:
            left = 
            self.body_stream_cb(self.conn.buffer.part(0))
            self.body_index += len(self.conn.buffer)
            self.buffer.reset()
            if self.body_index 
            
        if not self.conn.read_body:
            self.state = 'completed'
            return self.state_completed()        
        if self.type == 'get':
            self.state = 'completed'
            return self.state_completed()
        elif self.type == 'post':
            if not hasattr(self, 'content_length'):
                if 'content-length' not in self.headers:
                    raise HTTPProtocolError, 'No Content-Length header specified'
                try:
                    self.content_length = int(self.headers['content-length'])
                except ValueError:
                    raise HTTPProtocolError, 'Invalid Content-Length: %s' % self.headers[content-length]
            if len(self.conn.buffer) < self.content_length:
                return False
            self.conn.buffer.move(self.content_length)
            self.state = 'completed'
            return self.state_completed()    

    def state_completed(self):
        self.complete = True
        return
