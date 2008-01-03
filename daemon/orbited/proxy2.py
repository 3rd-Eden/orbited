import io
import event
from debug import *

class Proxy(object):
    def __str__(self):
        return "<Proxy %s>" % self.id
        
    def __init__(self, parent, addr, port, sock, buffer="", keepalive=0, id="0"):
        self.parent = parent
        self.keepalive = keepalive
        self.addr = addr
        self.port = port
        self.id = id
        self.setup(sock)
        self.write_to_server(buffer)
        self.closed_client = False

    def setup(self, sock):
        self.client_sock = sock
        if not hasattr(self, 'server_sock'):
            self.server_sock = io.client_socket(self.addr, self.port)
        self.client_wevent = None
        self.client_revent = event.read(self.client_sock, self.client_read_ready)
        self.server_wevent = None
        if not hasattr(self, 'server_revent') or not self.server_revent:
            self.server_revent = event.read(self.server_sock, self.server_read_ready)
        self.server_closed = False
        self.client_closed = False        
        self.from_client_buffer = ""        
        self.state = "proxying"
        self.buffer = ProxyBuffer()
        
    def next_request(self, sock, buffer):
#        print "next_request!"
        self.setup(sock)
        self.write_to_server(buffer)
        
    def request_complete(self):
        # Connection closed / should be closed
        if self.keepalive == 0 or self.buffer.version == 1.0:
            self.close_server()
            self.close_client()
            self.parent.proxy_complete(self, True)
            
        # Leave Connection open as per HTTP/1.1 keepalive
        else:
            self.state = "waiting"
            self.close_client(False)
            self.parent.proxy_complete(self)

    def server_has_closed(self, err=False):
        self.close_server()
        if self.state == "waiting":
            self.parent.proxy_expired(self)
        
    def client_has_closed(self, err=False):
        # print "client has indeed closed!"
        self.close_client()
        self.closed_client = True
    
    def close_server(self, close_sock=True):
        if self.server_wevent:
            self.server_wevent.delete()
        if self.server_revent:
            self.server_revent.delete()
        if close_sock:
            self.server_sock.close()
        
    def close_client(self,close_sock=True):
        if self.client_wevent:
            self.client_wevent.delete()
        if self.client_revent:
            self.client_revent.delete()
        if close_sock:
            self.client_sock.close()
            
    def write_to_server(self, data):
        # print "writing to server: %s" % data
        self.from_client_buffer += data
        if not self.server_wevent:
            self.server_wevent = event.write(self.server_sock, self.server_write_ready)
            
    def client_read_ready(self):
        try:
            data = self.client_sock.recv(io.BUFFER_SIZE)
            # print 'CLIENT READ: %s' % data
            if not data:
                self.client_has_closed()
                return None
#            self.debug("client_read\n===\n%s\n==========" % data)
            self.write_to_server(data)
            return True
        except io.socket.error:
            self.client_has_closed(err=True)
            return None        
        
    def server_write_ready(self):
        try:
            if not self.from_client_buffer:
                if self.closed_client:
                    self.parent.proxy_completed(self, True)
                self.server_wevent = None
                return None
            bsent = self.server_sock.send(self.from_client_buffer)
            # print 'SERVER WRITE: %s' % self.from_client_buffer[:bsent]
            self.from_client_buffer = self.from_client_buffer[bsent:]
            return True
        except io.socket.error:
            self.server_has_closed(err=True)
        
    def server_read_ready(self):
        try:
            data = self.server_sock.recv(io.BUFFER_SIZE)
            self.buffer.recv(data)
            if not data:
                self.server_has_closed()
                if not self.buffer.out:
                    self.request_complete()
                return None            
            if self.buffer.out and not self.client_wevent:
                self.client_wevent = event.write(self.client_sock, self.client_write_ready)
            return True
        except io.socket.error:
            self.server_has_closed(err=True)
        
    def client_write_ready(self):
        try:
            if not self.buffer.out:
                self.client_wevent = None                
                return None
            bsent = self.client_sock.send(self.buffer.out)
            self.buffer.out = self.buffer.out[bsent:]
            if self.buffer.complete and not self.buffer.out:
                self.request_complete()
                return None
            return True
        except io.socket.error, err:
            self.client_has_closed(err=True)
            
class ProxyBuffer(object):

    def __init__(self):
        self.buffer = ""
        self.out = ""
        self.mode = "unknown"
        self.complete = False
        self.size_sent = 0
        self.state = "status"
        self.headers = {}
        self.version = None
        
    def recv(self, data):
        if len(data) == 0 and self.version == 1.0:
            self.state = "complete"
            return self.state_complete()            
        self.buffer += data
        return getattr(self, 'state_%s' % self.state)()
    
    # Inadequately named... more like "move_to_buffer"
    def send(self, i):
        self.out += self.buffer[:i]
        self.buffer = self.buffer[i:]
        self.size_sent += i
    
    def state_status(self):
        index = self.buffer.find('\r\n')
        if index == -1:
            return
        self.status = self.buffer[:index]
        version_index = self.status.find(' ')
        version = self.status[:version_index]
        if version == "HTTP/1.0":
            self.version = 1.0
        elif version == "HTTP/1.1":
            self.version = 1.1
        else:
            raise "InvalidHTTPVersion", version
        self.headers_length = len(self.status)+2
        self.send(index+2)
        self.state = "headers"
        return self.state_headers()
        
    def state_headers(self):
        while True:
            index = self.buffer.find('\r\n')
            if index == -1:
                return
            header = self.buffer[:index]
            self.send(index+2)
            self.headers_length += index + 2
            if index == 0:
                self.state = 'pre_body'
                return self.state_pre_body()
            key, val = header.split(': ')
            self.headers[key] = val
            if key == 'Content-Length':
                self.mode = "normal"
                self.headers['Content-Length'] = int(self.headers['Content-Length'])
            if key == "Transfer-Encoding" and val == "chunked":
                self.mode = "chunked"

    def state_pre_body(self):
        
        # HTTP/1.0
        if self.version == 1.0:
            self.state = "http_1_0_body"
            return self.state_http_1_0_body()

        
        # HTTP/1.1 Implied 0 body length
        if self.mode == "unknown":
            self.headers['Content-Length'] = 0
            self.state = "complete"
            return self.state_complete()
            
        # HTTP/1.1 Chunked Transfer Encoding -- Annoying
        if self.mode == "chunked":
            self.state = "chunked_body"
            return self.chunked_body()            
        # HTTP/1.1 Standard request
        if self.mode == "normal":
            self.state = "body"
            self.size_left = self.headers['Content-Length']
            return self.state_body()
                
    def state_http_1_0_body(self):
        self.send(len(self.buffer))
                
    def state_body(self):
        index = len(self.buffer)
        if index > self.size_left:
            # Server sent us too much data...
            raise "ExcessContentReceived"            
        self.send(index)
        self.size_left -= index
        if self.size_left == 0:
            self.state = 'complete'
            return self.state_complete()
        
    def state_chunked_head(self):
        index = self.buffer.find('\r\n')
        if index == -1:
            return 
        chunk_head = self.buffer[:index]
        self.out.append(self.buffer[:index+2])
        self.buffer = self.buffer[index+2:]
        size = int(chunk_head.split(';', 1)[0], 16)
        if size == 0:
            self.state == 'chunked_trailers'
            return self.state_chunked_trailers()
            
    def state_chunked_body(self):
        index = self.buffer.find('\r\n')
        if index == -1:
            return 
        self.out.append(self.buffer[:index+2])
        self.buffer = self.buffer[index+2:]
        self.state_chunked_head()
    
    def state_chunked_trailer(self):
        while True:
            index = self.buffer.find('\r\n')
            if index == -1:
                return 
            self.out += self.buffer[:index+2]
            self.buffer = self.buffer[2:]
            if index == 0:
                self.state = "complete"
                return self.state_complete()
                
    def state_complete(self):
        self.complete = True
        return
        