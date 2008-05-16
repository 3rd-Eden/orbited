from tcp import TCPConnection, TCPConnectionFactory
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientCreator

class HTML5ProxyProtocol(Protocol):
       
    def send(self, msg):
#        msg = msg.replace('\n', '\r\n')
        print 'write: ' + msg.replace('\r', '\\r').replace('\n', '\\n\n')
        self.transport.write(msg)
        
    def dataReceived(self, data):
        self.proxy_conn.send(data)

    def connectionLost(self, reason):
        self.proxy_conn.loseConnection()

class ProxyClient(object):
  
    def __init__(self):
        self.c = ClientCreator(reactor, HTML5ProxyProtocol)
        
    def connect(self, host, port):
        d = defer.Deferred()
        print 'do connected to ', host, ':', port, port.__class__
        self.c.connectTCP(host, port).addCallback(self.connected, d)
        return d
    
    def connected(self, conn, d):
        d.callback(conn)
        
class HTML5Connection(TCPConnection):
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
            print self.host, self.port
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
        
    def connectionMade(self):
        print "HTML5 Connection Made", self.id
        
    def connectionLost(self):
        self.remote_conn.transport.loseConnection()
        print "HTML5 Connection Lost", self.id

class SimpleProxyFactory(TCPConnectionFactory):
    protocol = HTML5Connection

    def __init__(self, *args, **kwargs):
        TCPConnectionFactory.__init__(self, *args, **kwargs)
        self.client = ProxyClient()