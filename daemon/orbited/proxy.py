from config import map as config
from tcp import TCPConnection, TCPConnectionFactory
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientCreator
from logger import get_logger

logger = get_logger("Proxy")
class ProxyProtocol(Protocol):
    def send(self, msg):
        logger.debug("%s:%s (%s) -> %s" % ( self.host, self.port, len(msg),  msg.replace('\r', '\\r').replace('\n', '\\n')))
        self.transport.write(msg)
        
    def dataReceived(self, data):
        logger.debug("%s:%s (%s) <- %s" % ( self.host, self.port, len(data),  data.replace('\r', '\\r').replace('\n', '\\n\n')))
        self.proxy_conn.send(data)

    def connectionLost(self, reason):
        self.proxy_conn.loseConnection()

class ProxyClient(object):
  
    def __init__(self):
        self.c = ClientCreator(reactor, ProxyProtocol)
        
    def connect(self, host, port):
        d = defer.Deferred()
        logger.debug("opening remote connection to %s:%s" % (host, port))
        self.c.connectTCP(host, port).addCallback(self.connected, d, host, port)
        return d
    
    def connected(self, conn, d, host, port):
        conn.host, conn.port = host, port
        d.callback(conn)
        
class ProxyConnection(TCPConnection):
#    ping_timeout  = 10 # override default of 20.
#    ping_interval = 10 # override default of 20
    
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
        getattr(self, 'state_' + self.state)(data)
    
    def state_initial(self, data):
        try:
            host, port = data.split(':')
            self.host = host
            self.port = int(port)
            if (self.host, self.port) not in config['[access]']:
                logger.warn('unauthorized', data)
                raise (Exception("Unauthorized"), "(host, port) pair not authorized for proxying")
            logger.access(self.getClientIP(), "TCP/raw", " -> ", self.host, ":", self.port, " [ ", self.getClientIP(), " ]")
            self.factory.client.connect(self.host, self.port).addCallback(self.connected_remote)
            self.state = 'proxy'
        except Exception, x:
            logger.warn("Invalid handshake: " + str(x) + " (payload: %s)" % data)
            self.send("Invalid handshake: " + str(x) + " (payload: %s)" % data)
            self.loseConnection()
            
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

class SimpleProxyFactory(TCPConnectionFactory):
    protocol = ProxyConnection

    def __init__(self, *args, **kwargs):
        TCPConnectionFactory.__init__(self, *args, **kwargs)
        self.client = ProxyClient()