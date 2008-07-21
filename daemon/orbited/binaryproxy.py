from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.internet.protocol import Protocol

from config import map as config
from logger import get_logger
from tcp import TCPConnection
from tcp import TCPConnectionFactory

log = get_logger("BinaryTCPConnection")

# Based on code from: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/510399

def byte_to_hex( byteStr ):
    return ''.join([ "%02X" % ord( x ) for x in byteStr ])

def hex_to_byte(hexStr):
    bytes = []
    for i in range(0, len(hexStr), 2):
        bytes.append(chr(int(hexStr[i:i+2], 16)))
    return ''.join(bytes)

class BinaryProxyProtocol(Protocol):
       
    def send(self, msg):
        bytes = hex_to_byte(msg)
#        log.debug("%s:%s (%s) -> %s" % ( self.host, self.port, len(bytes),  bytes.replace('\r', '\\r').replace('\n', '\\n')))
        self.transport.write(bytes)
        
    def dataReceived(self, data):
#        log.debug("%s:%s (%s) <- %s" % (self.host, self.port, len(data), data))
        self.proxy_conn.send(byte_to_hex(data))

    # TODO support half closure (peer write end)
    def connectionLost(self, reason):
        self.proxy_conn.loseConnection()

# XXX why does this exists?  why not directly use a ClientCreator?
class ProxyClient(object):
  
    def __init__(self):
        self.c = ClientCreator(reactor, BinaryProxyProtocol)
    
    def connect(self, host, port):
        d = defer.Deferred()
#        print "opening remote connection to %s:%s" % (host, port)
        connectDeferred = self.c.connectTCP(host, port)
        connectDeferred.addCallback(self.connected, d, host, port)
        connectDeferred.addErrback(d.errback)
        return d
    
    def connected(self, conn, d, host, port):
        conn.host, conn.port = host, port
        d.callback(conn)

class BinaryProxyConnection(TCPConnection):
    
    def setup(self):
        self.state = "initial"
        self.connected = False
        self.remote_conn = None
        self.buffer = []
    
    def connected_remote(self, conn):
        self.connected = True
        self.remote_conn = conn
        self.remote_conn.proxy_conn = self
        for item in self.buffer:
            self.remote_conn.send(item)
        # TODO clear buffer?

    def connect_remote_failed(self, reason):
        """
        Called when we could not establish a connection with backend
        server.
        
        reason is a twisted.python.failure.Failure
        """
        # TODO do this in proxy.py too...
        exception = reason.value
        log.error('Failed to connect to remote backend server: %r' % exception)
        # TODO how to propagate error to the client as an .onerror
        #      callback (in JS)?
        self.send("Failed to connect to remote backend server: %s" % exception)
        self.loseConnection()

    def dataReceived(self, data):
#        print 'recv: ', data
        getattr(self, 'state_' + self.state)(data)
    
    def state_initial(self, data):
#        print 'recv:', data
        try:
            # XXX this is assuming data is received in one single chunk?!
            host, port = data.split(':')
            self.host = host
            self.port = int(port)
            # TODO DRY this with ProxyConnection.
            if (self.host, self.port) not in config['[access]']:
                log.warn('unauthorized', data)
                raise (Exception("Unauthorized"), "(host, port) pair not authorized for proxying")
            log.access(self.getClientIP(), "TCP/bin", " -> ", self.host, ":", self.port, " [ ", self.getClientIP(), " ]")
            # TODO look for errback misses in other classes!
            clientDeferred = self.factory.client.connect(self.host, self.port)
            clientDeferred.addCallback(self.connected_remote)
            clientDeferred.addErrback(self.connect_remote_failed)
            self.state = 'proxy'
        except Exception, x:
            # TODO when we raise the unauthorized message, the client does not understand it.
            self.send("Invalid handhsake: " + str(x) + "(payload: %s)" % data)
            self.loseConnection()
            raise
            
    def state_proxy(self, data):
        if not self.connected:
            self.buffer.append(data)
        else:
            self.remote_conn.send(data)
        
#    def connectionMade(self):
#        print "Proxy Connection Made", self.id

    # TODO support half closure (peer write end)
    def connectionLost(self):
        if self.remote_conn:
            self.remote_conn.transport.loseConnection()
        # TODO set connected=False et al?
#        print "Proxy Connection Lost", self.id

class BinaryProxyFactory(TCPConnectionFactory):
    protocol = BinaryProxyConnection

    def __init__(self, *args, **kwargs):
        TCPConnectionFactory.__init__(self, *args, **kwargs)
        self.client = ProxyClient()