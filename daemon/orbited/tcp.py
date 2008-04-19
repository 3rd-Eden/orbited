__version__ = "0.4.twisted.alpha1"
from transports.sse import SSEConnection
import random
class TCPAuthentication(object):
    def __init__(self):
        pass
    
    def authorize(self, id):
        return True

class TCPEvent(object):
    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, " ".join(["%s=%s" % (k, v) for (k, v) in self.__dict__.items() ]))

class TCPOpen(TCPEvent):
    name = 'open'
    def __init__(self, id):
        self.id = id

class TCPClose(TCPEvent):
    name = 'close'
    def __init__(self, id, graceful=1, queue=[]):
        self.id = id
        self.graceful=graceful
        self.queue = queue

class TCPRecv(TCPEvent):
    name = 'recv'
    def __init__(self, id, data):
        self.id = id
        self.data = data

class TCPHandler(object):
    def __init__(self, app):
        self.app = app
        self.authentication = TCPAuthentication()
        self.connections = {}
    
    def send(self, recipient, payload):
        if recipient not in self.connections:
            return False
        conn = self.connections[recipient]
        conn.send(payload)
        return True
    
    def put(self, request):
        key = "".join([random.choice("ABCDEF1234567890") for i in range(10)])
        request.respond('200 OK', {}, key)
        
    def get(self, request):
        id = request.form.get('id', None)
        if not id:
            return request.respond('401 Unauthorized', {})
        last_event_id = request.headers.get('Last-Event-ID', None)
        if last_event_id == None:
            if id in self.connections:
                return request.respond('409 Conflict', {})
            else:
                authorized = self.authentication.authorize(id)
                if not authorized:
                    return request.respond('401 Unauthorized', {})
                self.connections[id] = TCPConnection(self, id, SSEConnection(request))
                self.app.event(TCPOpen(id))
        else:
            if id not in self.connections:
                return request.respond('404 Session not found')
            try:
                last_event_id = int(last_event_id)
            except ValueError:
                return request.response('400 Invalid Last-Event-ID Header')
            conn = self.connections[id]
            conn.ack(last_event_id)
            conn.get(SSEConnection(request))
            
    def post(self, request):
        id = request.form.get('id', None)
        if not id:
            return request.respond('404 Session not found', {})        
        conn = self.connections[id]
        last_event_id = request.headers.get('Last-Event-ID', None)
        if last_event_id != None:
            try:
                last_event_id = int(last_event_id)
            except ValueError:
                return request.response('400 Invalid Last-Event-ID Header')
            conn.ack(last_event_id)
        self.app.event(TCPRecv(id, request.body))
        request.respond('200 OK')
#        conn.recv(request.body) # Maybe not this?
    def delete(self, request):
        id = request.form.get('id', None)
        if not id:
            return request.respond('404 Session not found', {})
        conn = self.connections[id]
        self.app.event(TCPClose(id))
        conn.close()
        del self.connections[id]
        return request.respond('200 OK')
    
    def timeout(self, conn):
        pass

class TCPConnection(object):
    
    def __init__(self, handler, id, conn, reliable=True):
        self.retry = 5000
        self.handler = handler
        self.id = id
        self.packet_id = 0
        self.reliable = reliable
        self.push_queue = []
        self.unack_queue = []
        self.last_ack_id = 0
        self.conn = conn
        self.conn.write_event('TCPOpen')
        self.conn.write_id(self.packet_id)
        self.conn.write_retry(self.retry)
        self.conn.write_dispatch()
        self.conn.flush()
    
    def send(self, data):
        print 'sending:', data
        if not self.conn:
            print 'no conn'
            self.push_queue.append(data)
        else:
            self._send(data)
                
    def _send(self, data):
        print 'actually sending', data
        if data == "!close":
            self.conn.flush()
            self.conn.close()
            self.conn = None
            return
        self.packet_id += 1
        self.conn.write_data(data)
        self.conn.write_id(self.packet_id)
        self.conn.write_dispatch()
        self.conn.flush()
        self.unack_queue.append(data)
        
    def flush_push_queue(self):
        while self.push_queue:
            if not self.conn: break #TODO: this is just for testing with data == "!close"
            data = self.push_queue.pop(0)
            self._send(data)
        
    def resend_unack_queue(self):
        if not self.unack_queue:
            return
        for data in self.unack_queue:
            self.conn.write_data(data)
            self.conn.write_dispatch()
        ack_id = self.last_ack_id + len(self.unack_queue)
        self.conn.write_id(ack_id)
        self.conn.write_dispatch()
    
    def ack(self, ack_id):
        ack_id = min(ack_id, self.packet_id)
        if ack_id <= self.last_ack_id:
            return
        for i in range(ack_id-self.last_ack_id):
            self.unack_queue.pop(0)
        self.last_ack_id = ack_id
    
    def recv(self, data):
        print 'TCP.recv:', data
    
    def get(self, conn):
        print 'got conn'
        if self.conn:
            self.conn.close()
        self.conn = conn
        self.conn.write_retry(self.retry)
        self.resend_unack_queue()
        self.flush_push_queue()
        if not self.conn: return # TODO: just for testing data == "!close"
        self.conn.flush()
        
    def close(self):
        if self.conn:
            self.conn.close()

