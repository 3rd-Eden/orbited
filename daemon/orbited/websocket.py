import urlparse
from tcp import TCPConnection, TCPConnectionFactory
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientCreator
from logger import get_logger

log = get_logger("WebSocket")
class ProxyProtocol(Protocol):
       
    def send(self, msg):

#        print "%s:%s (%s) -> %s" % ( self.host, self.port, len(msg),  msg.replace('\r', '\\r').replace('\n', '\\n'))
        self.transport.write('\x00' + msg + '\x00')
        self.transport.write(msg)
        
    def dataReceived(self, data):
        getattr(self, 'read_' + self.state)(data)

    def connectionLost(self, reason):
        if self.d:
            self.d.errback(reason)
            self.d = None
        if hasattr(self, 'proxy_conn') and self.proxy_conn:
            self.proxy_conn.loseConnection()
            self.proxy_conn = None    
    def handshake(self, host, port, url, d):
        self.d = d
        self.host = host
        self.port = port
        self.url = url
        self.state = 'initial'
        self.buffer = ""
        hostname = self.host
        if self.port != 80:
            hostname += ':' + str(self.port)
        self.transport.write('OPTIONS %s HTTP/1.1\r\nUpgrade: WebSocket/1.0\r\nHost: %s\r\n\r\n' % (self.url, hostname))

    def read_initial(self, data):
        self.buffer += data
        if '\r\n\r\n' not in self.buffer:
            return
        try:
            response, extra = self.buffer.split('\r\n\r\n', 1)
            status, headers = response.split('\r\n', 1)
            headers = dict([ d.split(': ') for d in headers.split('\r\n') ])
            if status != 'HTTP/1.1 101 Switching Protocols':
                self.connectionLost("bad status")
            if headers.get('Upgrade', None) != 'WebSocket/1.0':
                self.connectionLost("missing upgrade header")
            self.state = 'proxy'
            self.d.callback(self)
            self.d = None
            if extra:
                self.buffer = extra
                self.read_proxy("")
        except Exception, e:
              self.connectionLost(str(e))

    def read_proxy(self, data):
        self.buffer += data
        while True:
            i = self.buffer.find('\x00')
            if i == -1:
                return
            j = self.buffer.find('\x00', i+1)
            if j == -1:
                return
            payload = self.buffer[i+1:j]
            self.buffer = self.buffer[j+1:]
            self.proxy_conn.send(payload)
      
class ProxyClient(object):
  
    def __init__(self):
        self.c = ClientCreator(reactor, ProxyProtocol)
        
    def connect(self, host, port, url):
        d = defer.Deferred()
#        print "opening remote connection to %s:%s" % (host, port)
        self.c.connectTCP(host, port).addCallback(self.connected, d, host, port, url)
        return d
    
    def connected(self, conn, d, host, port, url):
        conn.handshake(host, port, url, d)
        
class WebSocketConnection(TCPConnection):
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
    
    def failed_handshake(self, err=None):
        self.loseConnection()
        
    def dataReceived(self, data):
        getattr(self, 'state_' + self.state)(data)
    
    def state_initial(self, data):
        try:
            url = urlparse.urlparse(data)
            if url.scheme != '' and url.scheme != 'http':
                raise Exception("InvalidScheme"), "only http schemes are supported"
            if not url.port:
                url.port = 80
            self.url  = url.path + (url.query and '?' + k.query or '')
            self.url += (url.fragment and '#' + url.fragment)
            self.host = url.hostname
            self.port = url.port
            log.access(self.getClientIP(), 
                "WebSocket", " -> ", data, " [ ", self.getClientIP(), " ]")
            self.factory.client.connect(self.host, self.port, self.url).addCallback(self.connected_remote).addErrback(self.failed_handshake)
            self.state = 'proxy'
        except Exception, x:
#            print "Invalid handshake: " + str(x) + "(payload: %s)" % data
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

class WebSocketFactory(TCPConnectionFactory):
    protocol = WebSocketConnection

    def __init__(self, *args, **kwargs):
        TCPConnectionFactory.__init__(self, *args, **kwargs)
        self.client = ProxyClient()