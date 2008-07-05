from tcp import TCPConnection, TCPConnectionFactory
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientCreator

from logger import get_logger
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

    def connectionLost(self, reason):
        self.proxy_conn.loseConnection()

class ProxyClient(object):
  
    def __init__(self):
        self.c = ClientCreator(reactor, BinaryProxyProtocol)
    
    def connect(self, host, port):
        d = defer.Deferred()
#        print "opening remote connection to %s:%s" % (host, port)
        self.c.connectTCP(host, port).addCallback(self.connected, d, host, port)
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
    
    def dataReceived(self, data):
#        print 'recv: ', data
        getattr(self, 'state_' + self.state)(data)
    
    def state_initial(self, data):
#        print 'recv:', data
        try:
            host, port = data.split(':')
            self.host = host
            self.port = int(port)
            log.access(self.getClientIP(), "TCP/bin", " -> ", self.host, ":", self.port, " [ ", self.getClientIP(), " ]")
            self.factory.client.connect(self.host, self.port).addCallback(self.connected_remote)
            self.state = 'proxy'
        except Exception, x:
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
        
    def connectionLost(self):
        if self.remote_conn:
            self.remote_conn.transport.loseConnection()
#        print "Proxy Connection Lost", self.id

class BinaryProxyFactory(TCPConnectionFactory):
    protocol = BinaryProxyConnection

    def __init__(self, *args, **kwargs):
        TCPConnectionFactory.__init__(self, *args, **kwargs)
        self.client = ProxyClient()