from tcp import TCPConnection, TCPConnectionFactory
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientCreator
import json

class JsonProxyProtocol(Protocol):
       
    def send(self, msg):
        print "%s:%s (%s) -> %s" % ( self.host, self.port, len(msg),  msg.replace('\r', '\\r').replace('\n', '\\n'))
        self.transport.write(msg)
        
    def dataReceived(self, data):
        self.proxy_conn.send(data)

    def connectionLost(self, reason):
        self.proxy_conn.loseConnection()

class ProxyClient(object):
  
    def __init__(self):
        self.c = ClientCreator(reactor, JsonProxyProtocol)
        
    def connect(self, host, port):
        d = defer.Deferred()
        print "opening remote connection to %s:%s" % (host, port)
        self.c.connectTCP(host, port).addCallback(self.connected, d, host, port)
        return d
    
    def connected(self, conn, d, host, port):
        conn.host, conn.port = host, port
        d.callback(conn)
        
class JsonProxyConnection(TCPConnection):
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
    
    def send(self, data, *args):
        if isinstance(data, str):
            print 'encoding(%s) ' % len(data)
            data = json.encode(data)
        return TCPConnection.send(self, data, *args)
    
    def dataReceived(self, data):
        if not data:
            return
        print 'decode?:', data
        data = json.decode(str(data))
        print 'decoded:' + data
        getattr(self, 'state_' + self.state)(data)
    
    def state_initial(self, data):
        try:
            host, port = data.split(':')
            self.host = host
            self.port = int(port)
            self.factory.client.connect(self.host, self.port).addCallback(self.connected_remote)
            self.state = 'proxy'
        except Exception, x:
            self.send("Invalid handhsake: " + str(x) + "(payload: %s)" % data)
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

class JsonProxyFactory(TCPConnectionFactory):
    protocol = JsonProxyConnection

    def __init__(self, *args, **kwargs):
        TCPConnectionFactory.__init__(self, *args, **kwargs)
        self.client = ProxyClient()