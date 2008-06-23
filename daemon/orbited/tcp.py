import os
import random
from twisted.web import server, resource, static, error
from twisted.internet import reactor, defer
from logger import get_logger
import transports

class TCPPing(object):
    pass    


class TCPConnection(resource.Resource):
    logger = get_logger("TCPConnection")
    ping_timeout = 20
    ping_interval = 20
    retry = 50
    
    def __init__(self, factory, id):
        resource.Resource.__init__(self)
        self.factory = factory
        self.id = id
        self.transport = None
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
#        print 'TIMEOUT', self.id
        self.close()
        
    def close(self):
        if self.transport:
            self.transport.send_packet('close', "", 'timeout')
            self.transport.flush()
            self.transport.close()
        self.factory.conn_closed(self)
        self.transport = None
        self.connectionLost()
        
    def transport_closed(self, transport):
#        print 'transport_closed'
        if transport is self.transport:
#            print 'set to none'
            self.transport = None
            

    
    def close_transport(self):
        
#        print "Transport closing"
        self.transport.close()
        self.transport = None
        
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
        while self.msg_queue and self.transport:
            self.send(self.msg_queue.pop(0), flush=False)
        
    
        
    def send(self, data, flush=True):
        if not self.transport:
#            print 'queue: ' + data
            self.msg_queue.append(data)
        else:
#            print 'SEND: ' + str(data)
            self.packet_id += 1
            self._send(data, self.packet_id)
            self.unack_queue.append(data)
            if flush:
                self.transport.flush()
                
    def _send(self, data, packet_id=""):
        if isinstance(data, TCPPing):
            self.transport.send_packet('ping', packet_id)
        else:
            self.transport.send_packet('data', packet_id, data)
            
    def resend_unack_queue(self):
        if not self.unack_queue:
            return
        for data in self.unack_queue:
            self._send(data)
        ack_id = self.last_ack_id + len(self.unack_queue)
        self.transport.send_packet('id', ack_id)
        
    def render(self, request):
        self.logger.debug(request)
        transport_name = request.args.get('transport', [None])[0]
        if transport_name:
            return self.render_downstream(request)
        else:
            return self.render_upstream(request)
        
        
    def render_downstream(self, request):
#        print "Render Downstream:", request
        if self.transport:
            self.close_transport()
        self.transport = transports.create(request)
        if not self.open:
#            print 'not previously open'
            self.open = True
            self.transport.send_packet('open', self.packet_id)
            self.transport.send_packet('retry', '', self.retry)
            self.transport.flush()
            self.client_ip = self.transport.getClientIP()
            self.transport.onClose().addCallback(self.transport_closed)
            self.connectionMade()
        else:
#            print 'previously open'
            ack = request.received_headers.get('ack', None)
            if not ack:
                ack = request.args.get('ack', [None])[0]
            if ack:
                try:
                    ack = int(ack)
                    self.ack(ack, True)
                    
                except:
                    pass
#            print 'setting up new transport', self.id
            self.transport.onClose().addCallback(self.transport_closed)
            self.resend_unack_queue()
            self.send_msg_queue()
            self.transport.flush()
        return server.NOT_DONE_YET
            
    def render_upstream(self, request):
#        print 'RENDER UPSTREAM'
#        print request.received_headers
        stream = request.content.read()
        ack = request.received_headers.get('ack', None)
        if not ack:
            ack = request.args.get('ack', [None])[0]
        if ack:
            try:
                ack = int(ack)
                self.ack(ack, True)
#                print 'worked with', ack
            except:
#                print 'COULD NOT ACK WITH', ack
                pass
        encoding = request.received_headers.get('tcp-encoding', None)
        request.write('OK')
        request.finish()
        if encoding == 'text':
            self.dataReceived(stream)
        return server.NOT_DONE_YET
        
class TCPConnectionFactory(resource.Resource):
    protocol = TCPConnection
    logger = get_logger("TCPConnectionFactory")
    def __init__(self):
        resource.Resource.__init__(self)
        self.static_files = static.File(os.path.join(os.path.split(__file__)[0], 'static'))
        self.connections = {}
    
    def conn_closed(self, conn):
        if conn.id in self.connections:
            del self.connections[conn.id]
    
    
    def render(self, request):
        self.logger.debug(request)
        id = self.create_session(request)
        return id
    
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
