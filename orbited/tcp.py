import os
import random
from twisted.web import server, resource, static, error
from twisted.internet import reactor, defer
from sse import SSEConnection

    

class TCPPing(object):
    pass    
    
class TCPConnection(resource.Resource):
    ping_timeout = 20
    ping_interval = 20
    retry = 5000
    def __init__(self, factory, id):
        resource.Resource.__init__(self)
        self.factory = factory
        self.id = id
        self.conn = None
        self.open = False
        self.msg_queue = []
        self.unack_queue = []
        self.last_ack_id = 0
        self.packet_id = 0
        self.ping_timer = None
        self.timeout_timer = None
        self.reset_ping_timer()
        self.client_ip = None
        self.setup()
        
    def setup(self):
        pass
        
    def dataReceived(self, data):
        pass
    
    def connectionMade(self):
        pass
    
    def connectionLost(self):
        pass
        
    def loseConnection(self):
        self.close()

    def getClientIP(self):
        return self.client_ip
    
    def reset_ping_timer(self):
        if self.ping_timer:
            self.ping_timer.cancel()
        if self.timeout_timer:
            self.timeout_timer.cancel()
            self.timeout_timer = None
        self.ping_timer = reactor.callLater(self.ping_interval, self.send_ping)
    
    def send_ping(self):
        self.ping_timer = None
        self.send(TCPPing())
        self.timeout_timer = reactor.callLater(self.ping_timeout, self.timeout)
        
    def timeout(self):
        self.close()
        
    def close(self):
        if self.conn:
            print 'sending TCPCLose'
            self.conn.write_event('TCPClose')
            self.conn.write_data('timeout')
            self.conn.write_dispatch()
            self.conn.flush()
            print 'finishing conn'
            self.conn.finish()
        print self.factory
        self.factory.conn_closed(self)
        self.conn = None
        self.connectionLost()
        
    def sse_closed(self, conn):
        if conn is self.conn:
            self.conn = None
        
    def render(self, request):
        if request.method == 'GET':
            return self.get(request)
        if request.method == 'POST':
            return self.post(request)
        return "Not Implemented Yet"

    def get(self, request):
        last_event_id = request.received_headers.get('Last-Event-ID', None)
        if last_event_id == None:
            if self.open: # Conflicted session
                print "Conflicted Session!"
                print "Conflicted Session!"
                print "Conflicted Session!"
                request.setResponseCode('409', 'Conflict')
                return "Session already in use (Did you forget the Last-Event-ID header?)"
            else: # new session
                print ("recieved GET(%s): " % self.id) + str(request.received_headers)
                print "==="
                self.open = True
                self.conn = SSEConnection(request)
                self.conn.write_event('TCPOpen')
                self.conn.write_id(self.packet_id)
                self.conn.write_retry(self.retry)
                self.conn.write_dispatch()
                self.conn.flush()
                self.client_ip = self.conn.getClientIP()
                self.conn.onClose().addCallback(self.sse_closed)
                self.connectionMade()
                return server.NOT_DONE_YET
        try:
            last_event_id = int(last_event_id)
        except ValueError:
            request.setResponseCode('400', 'Invalid Last-Event-ID Header')
            return "Invalid Last-Event-ID Header"
        self.ack(last_event_id)
        self.conn.write_retry(self.retry)
        self.resend_unack_queue()
        self.send_msg_queue()
        self.conn.flush()
        
        return server.NOT_DONE_YET

    def post(self, request):
        print ('received POST(%s)' % self.id) + str(request.received_headers)
        print "==="
        if request.received_headers.get('content-type', None) != "text/event-stream":
            return "ERR, wrong content-type"
        stream = request.content.read()
        event = "message"
        id = None
        data = ""
        for line in stream.splitlines():
            if line.startswith('data:'):
                if data != "":
                    data += "\n"
                data += line[5:]
            elif line.startswith('id:'):
                try:
                    id = int(line[3:])
                except ValueError:
                    pass
            elif line.startswith('event:'):
                event = line[6:]
            if line == "": # dispatch
                if event == "message":
                    self.dataReceived(data)
                elif event == "TCPAck":
                    try:
                        last_event_id = int(data)
                    except ValueError:
                        pass
                    else:
                        print 'ack:', last_event_id
                        self.ack(last_event_id)
                event = "message"
                id = None
                data = ""

            
        """last_event_id = request.received_headers.get('last-event-id', None)
        if last_event_id != None:
            try:
                last_event_id = int(last_event_id)
            except ValueError:
                request.setResponseCode('400', 'Invalid Last-Event-ID Header')
                return "Invalid Last-Event-ID Header"
            self.ack(last_event_id)
        tcp = request.received_headers.get('tcp', None)
        if tcp == 'send':
            self.dataReceived(request.content.read())"""
        return ""
        
    def ack(self, ack_id):
        self.reset_ping_timer()
        ack_id = min(ack_id, self.packet_id)
        if ack_id <= self.last_ack_id:
            return
        for i in range(ack_id - self.last_ack_id):
            self.unack_queue.pop(0)
        self.last_ack_id = ack_id
        
    def send_msg_queue(self):
        while self.msg_queue and self.conn:
            self.send(self.msg_queue.pop(0), flush=False)
        
    def send(self, data, flush=True):
        if not self.conn:
            self.msg_queue.append(data)
        else:
            self.packet_id += 1
            self._send(data, self.packet_id)
            self.unack_queue.append(data)
            if flush:
                self.conn.flush()
                
    def _send(self, data, packet_id=None):
        if isinstance(data, TCPPing):
            self.conn.write_event('TCPPing')
        else:
            self.conn.write_data(data)
        if packet_id != None:
            self.conn.write_id(packet_id)
        self.conn.write_dispatch()
        
    def resend_unack_queue(self):
        if not self.unack_queue:
            return
        for data in self.unack_queue:
            self._send(data)
        ack_id = self.last_ack_id + len(self.unack_queue)
        self.conn.write_id(ack_id)
        self.conn.write_dispatch()
        
        
class TCPConnectionFactory(resource.Resource):
#    isLeaf = True
    protocol = TCPConnection
    def __init__(self):
        resource.Resource.__init__(self)
#        print os.path.join(os.path.split(__file__)[0], 'static', 'tcp', 'bridge.html')
        self.static_files = static.File(os.path.join(os.path.split(__file__)[0], 'static', 'build'))

#        self.putChild('', self)
        self.connections = {}
#        self.put
    
    def conn_closed(self, conn):
#        print "Closed: ", conn.getClientIP()
        if conn.id in self.connections:
            del self.connections[conn.id]
    
    
    def render(self, request):
        if request.method == 'POST':
            return self.create_session()
        else:
            return error.NoResource("Resource Not Found")
    
    def create_session(self):
        key = None
        while key is None or key in self.connections:
            key = "".join([random.choice("ABCDEF1234567890") for i in range(10)])
        self.connections[key] = self.protocol(self, key)
#        self.connections[key].onClose().addCallback(self.conn_closed)
#        self.connections[key].onOpen().addCallback(self.conn_opened)
        return key
    
    def getChild(self, path, request):
        if path == 'static':
            return self.static_files
#        print 'get child "%s" %s' % ( path, request )
        if path not in self.connections:
#            print 'could not find "%s"' % path
            return error.NoResource("No such child resource.")
        return self.connections[path]
