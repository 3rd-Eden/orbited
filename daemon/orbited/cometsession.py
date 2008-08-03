import os
import random
from zope.interface import implements
from twisted.internet import reactor, interfaces
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.error import CannotListenError
from twisted.web import server, resource, static, error
from twisted.internet import reactor, defer

from orbited import logging
from orbited import transports

def setup_site(port):
    root = resource.Resource()
    static_files = static.File(os.path.join(os.path.dirname(__file__), 'static'))
    root.putChild('static', static_files)
    site = server.Site(root)
    root.putChild('tcp', TCPResource(port))
    return site

class Port(object):    
    """ A cometsession.Port object can be used in two different ways.
    # Method 1
    reactor.listenWith(cometsession.Port, 9999, SomeFactory())
    
    # Method 2
    root = twisted.web.resource.Resource()
    site = twisted.web.server.Site(root)
    reactor.listenTcp(site, 9999)
    reactor.listenWith(cometsession.Port, factory=SomeFactory(), resource=root, childName='tcp')
    
    Either of these methods should acheive the same effect, but Method2 allows you
    To listen with multiple protocols on the same port by using different urls.
    """
    implements(interfaces.IListeningPort)

    logger = logging.get_logger('orbited.cometsession.Port')

    def __init__(self, port=None, factory=None, backlog=50, interface='', reactor=None, resource=None, childName=None):
        self.port = port
        self.factory = factory
        self.backlog = backlog
        self.interface = interface
        self.resource = resource
        self.childName = childName
        self.wrapped_port = None
        self.listening = False
                
    def startListening(self):
        self.logger.debug('startingListening')
        if not self.listening:
            self.listening = True
            if self.port:
                self.logger.debug('creating new site and resource')
                self.wrapped_factory = setup_site(self)
                self.wrapped_port = reactor.listenTCP(
                    self.port, 
                    self.wrapped_factory,
                    self.backlog, 
                    self.interface
                )
            elif self.resource and self.childName:
                self.logger.debug('adding into existing resource as %s' % self.childName)
                self.resource.putChild(self.childName, TCPResource(self))
        else:
            raise CannotListenError("Already listening...")

    def stopListening():
        self.logger.debug('stopListening')
        if self.wrapped_port:
            self.listening = False
            self.wrapped_port.stopListening()
        elif self.resource:
            pass
            # TODO: self.resource.removeChild(self.childName) ?

    def connectionMade(self, transportProtocol):
        """
            proto is the tcp-emulation protocol
            
            protocol is the real protocol on top of the transport that depends
            on proto
            
        """
        self.logger.debug('connectionMade')
        protocol = self.factory.buildProtocol(transportProtocol.getPeer())
        if protocol is None:
            transportProtocol.loseConnection()
            return
        
        transport = FakeTCPTransport(transportProtocol, protocol)
        transportProtocol.parentTransport = transport
        protocol.makeConnection(transport)
        
    def getHost():
        if self.wrapped_port:
            return self.wrapped_port.getHost()
        elif self.resource:
            pass
            # TODO: how do we do getHost if we just have self.resource?

class FakeTCPTransport(object):
    implements(interfaces.ITransport)
    
    def __init__(self, transportProtocol, protocol):
        self.transportProtocol = transportProtocol
        self.protocol = protocol
        
    # ==========================
    # "Real" protocol facing API
    # ==========================
    
    def write(self, data):
        self.transportProtocol.write(data)

    def writeSequence(self, data):
        self.transportProtocol.write(data)

    def loseConnection(self):
        self.transportProtocol.loseConnection()

    def getPeer(self):
        return self.transportProtocol.getPeer()

    def getHost(self):
        return self.transportProtocol.getHost()

    # ==============================
    # transport emulation facing API
    # ==============================
        
    def dataReceived(self, data):
        self.protocol.dataReceived(data)
        
    def connectionLost(self):
        self.protocol.connectionLost(None)
            
    
class TCPConnectionResource(resource.Resource):

    logger = logging.get_logger('orbited.cometsession.TCPConnectionResource')

    # Determines timeout interval after ping has been sent
    pingTimeout = 30
    # Determines interval to wait before sending a ping
    # since the last time we heard from the client.
    pingInterval = 30

    def __init__(self, root, key, peer, host, **options):
        resource.Resource.__init__(self)
        
        self.root = root
        self.key = key
        self.peer = peer
        self.host = host
        self.transport = None
        self.cometTransport = None
        self.parentTransport = None
        self.options = {}
        self.msgQueue = []
        self.unackQueue = []
        self.lastAckId = 0
        self.packetId = 0
        self.pingTimer = None
        self.timeoutTimer = None
        self.lostTriggered = False
        self.resetPingTimer()
        self.open = False
        
    def getPeer(self):
        return self.peer
    
    def getHost(self):
        return self.host
    
    def write(self, data):
        self.send(data)
        
    def writeSequence(self, data):
        for datum in data:
            self.write(data)

    def loseConnection(self):
        # TODO: self.close() ?
        self.send(TCPClose())
        if self.cometTransport:
            self.cometTransport.close()
            self.cometTransport = None
        self.connectionLost()
        return None

    def connectionLost(self):
        if not self.lostTriggered:
            self.lostTriggered = True
            self.parentTransport.connectionLost()
    
    def getChild(self, path, request):
        if path in transports.map:
            return transports.create(path, self)
        return error.NoResource("No such child resource.")

    def render(self, request):
#        print '=='
#        print request
        stream = request.content.read()
#        print stream
#        print
        ack = request.args.get('ack', [None])[0]
        if ack:
            try:
                ack = int(ack)
                self.ack(ack, True)
            except ValueError:
                pass
        encoding = request.received_headers.get('tcp-encoding', None)
        request.write('OK')
        request.finish()
        reactor.callLater(0, self.parseData, stream)
        return server.NOT_DONE_YET
        
    def parseData(self, data):
        frames = [ 
            [ i.replace('__', '_') for i in f.split('_A') ]
            for f in data.split('_P') 
        ][:-1]
#        print frames
        # TODO: do we really need the id? maybe we should take it out
        #       of the protocol...
        #       -mcarter 7-29-08
        for args in frames:
#            print args
            id = args[0]
            name = args[1]
            args = args[2:]
            if name == 'close':
                self.loseConnection()
            if name == 'data':
                # TODO: should there be a try/except around this block?
                #       we don't want app-level code to break and cause
                #       only some packets to be delivered.
                self.parentTransport.dataReceived(args[0])
            if name == 'ping':
                # TODO: do we have to do anything? I don't think so...
                #       -mcarter 7-30-08
                print 'PONG!'
                pass

    # Called by the callback attached to the CometTransport
    def transportClosed(self, transport):
        if transport is self.cometTransport:
            self.cometTransport= None
    
    # Called by transports.CometTransport.render
    def transportOpened(self, transport):
        if self.cometTransport:
            self.cometTransport.close()
            self.cometTransport = None
        self.cometTransport = transport
        transport.onClose().addCallback(self.transportClosed)
        ack = transport.request.args.get('ack', [None])[0]
        if ack:
            try:
                ack = int(ack)
                self.ack(ack, True)
            except ValueError:
                pass
        
        self.resendUnackQueue()
        self.sendMsgQueue()
        if not self.open:
            self.open = True
            self.cometTransport.sendPacket("open", self.packetId)
        self.cometTransport.flush()

    def resetPingTimer(self):
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
        self.logger.debug('close reason=%s' % reason)
        if self.cometTransport:
            self.cometTransport.sendPacket('close', "", reason)
            self.cometTransport.flush()
            self.cometTransport.close()
            self.cometTransport = None
        self.root.removeConn(self)
                
#    def transport_closed(self, transport):
#        if transport is self.transport:
#            self.transport = None
        
    def ack(self, ackId, reset=False):
        self.logger.debug('ack idId=%s reset=%s' % (ackId, reset))
        if reset:
            self.resetPingTimer()
        ackId = min(ackId, self.packetId)
        if ackId <= self.lastAckId:
            return
        for i in range(ackId - self.lastAckId):
            self.unackQueue.pop(0)
        self.lastAckId = ackId
        
    def sendMsgQueue(self):
        while self.msgQueue and self.cometTransport:
            self.send(self.msgQueue.pop(0), flush=False)
        
    def send(self, data, flush=True):
        if not self.cometTransport:
            self.msgQueue.append(data)
        else:
            self.packetId += 1
            self._send(data, self.packetId)
            self.unackQueue.append(data)
            if flush:
                self.cometTransport.flush()
                
    def _send(self, data, packetId=""):
        self.logger.debug('_send data=%r packetId=%s' % (data, packetId))
        if isinstance(data, TCPPing):
            self.cometTransport.sendPacket('ping', packetId)
        elif isinstance(data, TCPClose):
            self.cometTransport.sendPacket('close', packetId)
        else:
            self.cometTransport.sendPacket('data', packetId, data)
    
    def resendUnackQueue(self):
        if not self.unackQueue:
            return
        for data in self.unackQueue:
            self._send(data)
        ackId = self.lastAckId + len(self.unackQueue)
        self.cometTransport.sendPacket('id', ackId)
        
class TCPPing(object):
    pass

class TCPClose(object):
    pass

class TCPResource(resource.Resource):
  
    def __init__(self, listeningPort):
        resource.Resource.__init__(self)
        self.listeningPort = listeningPort
        self.static_files = static.File(os.path.join(os.path.dirname(__file__), 'static'))
        self.connections = {}

    def render(self, request):
        key = None
        while key is None or key in self.connections:
            key = "".join([random.choice("ABCDEF1234567890") for i in range(10)])
        print request.getClientIP(), repr(request.getClientIP())
        # request.client and request.host should be address.IPv4Address classes
        self.connections[key] = TCPConnectionResource(self, key, request.client, request.host)
        self.listeningPort.connectionMade(self.connections[key])
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

    def connectionMade(self, conn):
        self.listeningPort.connectionMade(conn)
        
        
if __name__ == "__main__":
    class EchoProtocol(Protocol):
        
        def dataReceived(self, data):
            print "RECV:", data
            self.transport.write("Echo: " + data)
            
        def connectionMade(self):
            print "Connection Opened"
            
        def connectionLost(self):
            print "Connection Lost"
            
    class EchoFactory(Factory):
        protocol = EchoProtocol  
    
    factory = EchoFactory()    
    reactor.listenWith(Port, 7778, factory)
    reactor.run()
