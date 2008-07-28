import transports
from zope.interface import implements
from twisted.internet import reactor, interfaces
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.error import CannotListenError

def setup_site():
    root = resource.Resource()
    static_files = static.File(os.path.join(os.path.dirname(__file__), 'static'))
    root.putChild('static', static_files)
    site = server.Site(root)
    root.putChild('tcp', TCPResource())
    return site

class Port(object):
    
    implements(interfaces.IListeningPort)
    def __init__(self, port, factory, backlog=50, interface='', reactor=None):
        self.port = port
        self.factory = factory
        self.backlog = backlog
        self.interface = interface
        self.wrapped_factory = setup_site()
        self.wrapped_port = None
        self.listening = False
                
    def startListening(self):
        if not self.listening:
            self.listening = True
            self.wrapped_port = reactor.listenTCP(
                self.port, 
                self.wrapped_factory,
                self.backlog, 
                self.interface
            )
        else:
            raise CannotListenError, "Already listening..."
        
    def stopListening():
        if self.wrapped_port:
            self.listening = False
            self.wrapped_port.stopListening()
        
        
    def connectionMade(self, transportProtocol):
        """
            proto is the tcp-emulation protocol
            
            protocol is the real protocol on top of the transport that depends
            on proto
            
        """
        protocol = self.factory.buildProtocol(transportProtocol.getPeer())
        if protocol is None:
            transportProtocol.transport.loseConnection()
            return
        transport = FakeTCPTransport(transportProtocol, protocol)
        transportProtocol.parentTransport = transport
        protocol.makeConnection(transport)
        
    def getHost():
        return self.wrapped_port.getHost()
    
class TCPConnectionResource(resource.Resource):
    ping_timeout = 20
    ping_interval = 20
    
    def __init__(self, root, key):
        self.root = root
        self.key = key
        self.cometTransport = None
        self.options = {}
        self.msg_queue = []
        self.unack_queue = []
        self.last_ack_id = 0
        self.packet_id = 0
        self.ping_timer = None
        self.timeout_timer = None
        self.reset_ping_timer()
        
    def getChild(self, path, request):
        if path in transports.map:
            return transport.create(path, options)
        return error.NoResource("No such child resource.")

    def render(self, request):
        stream = request.content.read()
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
        
        
    def transportClose(self, transport):
        if transport is self.transport:
            self.transport = None
            
    def transportOpen(self, transport):
        if self.transport:
            self.transport.close()
            self.transport = None            
        transport.onClose().addCallback(self.transportClosed)
        self.resend_unack_queue()
        self.send_msg_queue()
        self.transport.flush()
        
    def resetPingtimer(self):
        if self.pingTimer:
            self.pingTimer.cancel()
        if self.timeoutTimer:
            self.timeoutTimer.cancel()
            self.timeoutTimer = None
        self.pingTimer = reactor.callLater(self.pingInterval, self.sendPing)
    
    def sendPing(self):
        self.pingTimer = None
        self.send(TCPPing())
        self.timeoutTimer = reactor.callLater(self.pingTimeout, self.timeout)
        
    def timeout(self):
        self.close("timeout")
        
    def close(self, reason=""):
        if self.transport:
            self.transport.send_packet('close', "", reason)
            self.transport.flush()
            self.transport.close()
            self.transport = None
        self.root.removeConn(self)
                
    def transport_closed(self, transport):
        if transport is self.transport:
            self.transport = None
        
    def ack(self, ackId, reset=False):
#        print 'ACK:', ack_id, 'reset:', reset
        if reset:
            self.resetPingTimer()
        ackId = min(ackId, self.packetId)
        if ackId <= self.lastAckId:
            return
        for i in range(ack_id - self.lastAckId):
            self.unackQueue.pop(0)
        self.lastAckId = ackId
        
    def sendMsgQueue(self):
        while self.msgQueue and self.transport:
            self.send(self.msgQueue.pop(0), flush=False)
        
    def send(self, data, flush=True):
        if not self.transport:
            self.msgQueue.append(data)
        else:
#            print 'SEND: ' + str(data)
            self.packet_id += 1
            self._send(data, self.packet_id)
            self.unackQueue.append(data)
            if flush:
                self.transport.flush()
                
    def _send(self, data, packet_id=""):
        if isinstance(data, TCPPing):
            self.transport.sendPacket('ping', packet_id)
        else:
            self.transport.sendPacket('data', packet_id, data)
            
    def resendUnackQueue(self):
        if not self.unackQueue:
            return
        for data in self.unackQueue:
            self._send(data)
        ack_id = self.lastAckId + len(self.unackQueue)
        self.transport.sendPacket('id', ackId)
        

class TCPResource(resource.Resource):
  
    def __init__(self):
        resource.Resource.__init__(self)
        self.static_files = static.File(os.path.join(os.path.split(__file__)[0], 'static'))
        self.connections = {}
        
    def render(self, request):
        key = None
        while key is None or key in self.connections:
            key = "".join([random.choice("ABCDEF1234567890") for i in range(10)])
        self.connections[key] = TCPConnectionResource(self, key)
        return key

    def getChild(self, path, request):
        if path == 'static':
            return self.static_files
        if path not in self.connections:
            return error.NoResource("No such child resource.")
        return self.connections[path]
         
    def removeConn(self, conn):
        if conn in self.connections:
            del self.connections[conn.id]
            
            