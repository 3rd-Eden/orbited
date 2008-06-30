import datetime
import os
import random
from twisted.web import server, resource, static, error
from twisted.internet import reactor, defer
import transports

class TCPPing(object):
    pass    
    
class TCPConnection(resource.Resource):
    ping_timeout = 20
    ping_interval = 20
    retry = 50
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
        print 'TIMEOUT', self.id
        self.close()
        
    def close(self):
        if self.conn:
            # self.conn.close('timeout')
            self.conn.write_event('TCPClose')
            self.conn.write_data('timeout')
            self.conn.write_dispatch()
            self.conn.flush()
            self.conn.finish()
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
        print 'get', request
        if not self.open:
            self.open = True
            self.conn = transports.create(request)
            # self.conn.open(self.id, self.packet_id, self.retry)
            self.conn.write_event('TCPOpen')
            self.conn.write_id(self.packet_id)
            self.conn.write_retry(self.retry)
            self.conn.write_dispatch()
            self.conn.flush()
            self.client_ip = self.conn.getClientIP()
            self.conn.onClose().addCallback(self.sse_closed)
            self.connectionMade()
            return server.NOT_DONE_YET
#        elif ack == None:
            
#            request.setResponseCode(409, 'Conflict')
#            return ""
        else:
            ack = request.received_headers.get('last-event-id', None)
            if not ack:
                ack = request.args.get('ack', [None])[0]
            if ack:
                self.ack(int(ack))
            self.conn = transports.create(request)
            self.conn.onClose().addCallback(self.sse_closed)
            self.conn.write_retry(self.retry)
            self.resend_unack_queue()
            self.send_msg_queue()
            self.conn.flush()
            expires = datetime.datetime.now() + datetime.timedelta(0, self.ping_timeout + self.ping_interval + 60*60*7)
            request.addCookie('tcp', self.id, path='/echo', expires=expires.strftime('%a, %d-%h-%Y %H:%M:%S GMT'))
            
        return server.NOT_DONE_YET

    def post(self, request):
        print 'post', request
        stream = request.content.read()
        expires = datetime.datetime.now() + datetime.timedelta(0, self.ping_timeout + self.ping_interval + 60*60*7)
        request.addCookie('tcp', self.id, path='/echo', expires=expires.strftime('%a, %d-%h-%Y %H:%M:%S GMT'))
        request.write('OK')
        request.finish()
        event = "message"
        id = None
        data = ""
        real_event = False
        for line in stream.split('\r\n'):
            if line:
                real_event = True
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
            elif line == "" and real_event  : # dispatch
                if event == "message":
                    self.dataReceived(data)
                elif event == "TCPAck":
                    try:
                        last_event_id = int(data)
                    except ValueError:
                        pass
                    else:
                         self.ack(last_event_id, True)
                event = "message"
                id = None
                data = ""
                real_event = False
        return server.NOT_DONE_YET
        
    def ack(self, ack_id, reset=False):
#        print 'ACK:', ack_id, 'reset:', reset
        if reset:
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
#            print 'TCPPing: ' + str(packet_id)
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
    protocol = TCPConnection
    def __init__(self):
        resource.Resource.__init__(self)
        self.static_files = static.File(os.path.join(os.path.split(__file__)[0], 'static'))
        self.connections = {}
    
    def conn_closed(self, conn):
        if conn.id in self.connections:
            del self.connections[conn.id]
    
    
    def render(self, request):
#        cookies = req
        if request.method == 'POST':
            request.setResponseCode(201, 'Created')
            return self.create_session(request)
        elif request.method == 'GET':
            id = self.create_session(request)
#            request.setResponseCode(201, 'Permanently Moved')
#            new_url = request.uri
#            if '?' in new_url:
#                new_url += '&id=' + id
#            else:
#                new_url += '?id=' + id
#            request.setHeader('location', new_url)
            expires = datetime.datetime.now() + datetime.timedelta(0, self.protocol.ping_timeout + self.protocol.ping_interval + 60*60*7)
            request.addCookie('tcp', id, path='/echo', expires=expires.strftime('%a, %d-%h-%Y %H:%M:%S GMT'))
            return self.connections[id].render(request)#, new_url)
        else:
            request.setResponseCode(404, 'Not Found')
            return ""
#        else:
#            request.setResponseCode(302, 'Found')
#            request.setHeader("Location", "/_/static/test-tcp.html")
#            return ""
    
    def create_session(self, request):
        key = None
        while key is None or key in self.connections:
            key = "".join([random.choice("ABCDEF1234567890") for i in range(10)])
        self.connections[key] = self.protocol(self, key)
        return key
    
    def getChild(self, path, request):
        if path == 'static':
            return self.static_files
        if path not in self.connections:
            return error.NoResource("No such child resource.")
        return self.connections[path]
