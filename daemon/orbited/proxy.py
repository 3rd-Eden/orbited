from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory, ClientCreator

ERRORS = {
    'InvalidHandshake': 102,
    'RemoteConnectionTimeout': 104
}

class ProxyIncomingProtocol(Protocol):
  
    def connectionMade(self):
        print "Proxy connectionMade"
        self.state = 'handshake'
        self.binary = False
        self.otherConn = None
        
    def dataReceived(self, data):
        if self.otherConn:
            return self.otherConn.transport.write(data)            
        if self.state == "handshake":
            try:
#                data = data
                self.binary = (data[0] == '1')
                hostname, port = data[1:].split(':')
                port = int(port)
                self.state = 'connecting'
                client = ClientCreator(reactor, ProxyOutgoingProtocol, self)
                client.connectTCP(hostname, port)
                print repr(hostname), repr(port)
                # TODO: connect timeout or onConnectFailed handling...
            except:
                self.transport.write("0" + str(ERRORS['InvalidHandshake']))
                self.transport.loseConnection()
                raise
        else:
            self.transport.write("0" + str(ERRORS['InvalidHandshake']))            
            self.state = 'closed'
            self.transport.loseConnection()
            
    def connectionLost(self, reason):
        print 'lost', reason
        if self.otherConn:
            self.otherConn.transport.loseConnection()
            
    def remoteConnectionEstablished(self, otherConn):
        if self.state == 'closed':
            return otherConn.transport.loseConnection()
        self.otherConn = otherConn
        self.transport.write('1')
        self.state = 'proxy' # Not really necessary...
        
    def remoteConnectionLost(self, otherConn, reason):
        print 'remote lost', reason
        self.transport.loseConnection()
        
    def write(self, data):
        print repr(data)
        # TODO: how about some real encoding, like base64, or even hex?
        if self.binary:
            data  = ",".join([ str(ord(byte)) for byte in data])
        self.transport.write(data)
        
class ProxyOutgoingProtocol(Protocol):
    
    def __init__(self, otherConn):
        self.otherConn = otherConn
            
    def connectionMade(self):
        self.otherConn.remoteConnectionEstablished(self)
                
    def dataReceived(self, data):
        self.otherConn.write(data)
        
    def connectionLost(self, reason):
        self.otherConn.remoteConnectionLost(self, reason)
        
class ProxyFactory(Factory):
    protocol = ProxyIncomingProtocol
    
    
        
if __name__ == "__main__":
    import cometsession
    reactor.listenWith(cometsession.Port, 9999, ProxyFactory())
    reactor.run()