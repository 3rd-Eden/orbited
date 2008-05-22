from tcp import TCPConnection, TCPConnectionFactory
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientCreator

class HTML5ProxyProtocol(Protocol):
       
    def __init__(self, *args, **kwargs):
        self.state = "initial"
        self.buffer = ""
        
    def send(self, msg):
        print "%s:%s (%s) -> %s" % ( self.host, self.port, len(msg),  msg.replace('\r', '\\r').replace('\n', '\\n'))
        msg = '\x02' + msg + '\x17'
        self.transport.write(msg)
        
    def handshake(self):
        self.state = "handshake"
        self.transport.write("HELLO\n")
        
    def state_handshake(self):
        i = self.buffer.find('\n')
        if i == -1:
            return
        if self.buffer[:i] == "WELCOME":
            print 'got welcome'
            self.buffer = self.buffer[i+1:]
            self.state = "proxy"
            self.state_proxy()
        else:
            print "Invalid remote handshake"
            self.transport.loseConnection()

    def state_proxy(self):
        while True:
            i = self.buffer.find('\x17')
            if i == -1:
                print '\\x17 not found'
                return
            print 'recv:', self.buffer[1:i]
            if self.buffer[0] == '\x02':
                self.proxy_conn.send(self.buffer[1:i])
            else:
                print 'got back:', repr(self.buffer[:i+1])
            self.buffer = self.buffer[i+1:]

    def dataReceived(self, data):
        self.buffer += data
        getattr(self, 'state_' + self.state)()

    def connectionLost(self, reason):
        self.proxy_conn.loseConnection()

class HTML5ProxyClient(object):
  
    protocol = HTML5ProxyProtocol
    def __init__(self):
        self.c = ClientCreator(reactor, self.protocol)
        
    def connect(self, host, port):
        d = defer.Deferred()
        print "opening remote connection to %s:%s" % (host, port)
        self.c.connectTCP(host, port).addCallback(self.connected, d, host, port)
        return d
    
    def connected(self, conn, d, host, port):
        conn.host, conn.port = host, port
        conn.handshake()
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
        if data:
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
            
    def connectionLost(self):
        if self.remote_conn:
            self.remote_conn.transport.loseConnection()

class HTML5ProxyFactory(TCPConnectionFactory):
    protocol = HTML5Connection
    proxy_protocol = HTML5ProxyClient
    def __init__(self, *args, **kwargs):
        TCPConnectionFactory.__init__(self, *args, **kwargs)
        self.client = self.proxy_protocol()