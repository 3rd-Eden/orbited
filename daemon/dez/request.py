
class HTTPRequest(object):
    
    def __init__(self, conn):
        self.conn = conn
        self.log = conn.get_logger('HTTPRequest')
        
        self.state = 'action'
        self.headers = {}
        self.headers_complete = False
        self.complete = False
        self.write_ended = False
        self.send_close = False
        self.body = None
        self.body_cb = None
        self.body_stream_cb = None
        self.remaining_content = 0
        self.write_queue_size = 0
        self.pending_writes = []
            
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
                self.state='headers_completed'
                return self.state_headers_completed()
            try:
                key, value = self.conn.buffer.part(0, index).split(': ')
            except ValueError:
                raise HTTPProtocolError, "Invalid HTTP header format"
            self.headers[key.lower()] = value
            self.conn.buffer.move(index+2)
            
            
    def state_headers_completed(self):
        self.content_length = int(self.headers.get('content-length', '0'))
        self.headers_complete = True
        self.state = 'waiting'
        return
    
    def state_waiting(self):
        pass
    
    def read_body(self, cb):
        self.body_cb = cb
        self.state = 'body'
        self.remaining_content = self.content_length
    
    def read_body_stream(self, stream_cb):
        self.remaining_content = self.content_length
        self.body_stream_cb = stream_cb
        self.state = 'body'
        return self.state_body()
        
    def state_body(self):
        bytes_available = min(len(self.conn.buffer), self.remaining_content)
        self.remaining_content -= bytes_available
        if self.body_stream_cb:
            self.body_stream_cb(self.conn.buffer.part(0,bytes_available))
            self.buffer.move(bytes_read)
        if self.remaining_content == 0:
            self.state = 'completed'
            return self.state_completed()
        
    def state_completed(self):
        if self.body_stream_cb:
            self.body_stream_cb("")
        elif self.body_cb:
            self.body_cb(self.buffer.part(0, self.content_length))
            self.buffer.move(content_length)
        if len(self.conn.buffer) > 0:
            raise HTTPProtocolError, "Unexpected Data"
        
        self.state = 'write'
        for (data, cb) in self.pending_writes:
            self.write(data, cb)        
        

    def write(self, data, cb=None, args=None):
        if self.write_ended:
            raise Exception, "end already called"
        if self.state != 'write':
            self.pending_writes.append((data, cb))
        if self.state == 'waiting':
            self.state = 'body'
            return self.state_body()
        if len(data) == 0:
            return cb()
        self.write_queue_size += 1
        self.conn.write(data, self.write_cb (cb, args))
    
    def write_cb(self, *args):
        self.write_queue_size -= 1
        if self.write_ended and self.write_queue_size == 0:
            if self.send_close:
                self.conn.close()
            else:
                self.conn.start_request()
        if len(args) > 0:
            cb = args[0]
            args = args[1:]
            cb(*args)
            
    def end(self, cb=None):
        if self.write_ended:
            raise Exception, "end already called"
        self.write_ended = True
        self.conn.write("", (self.write_cb, cb))
    def close(self, cb=None):
        if not self.write_ended:
            self.end(cb)
        self.send_close = True
    