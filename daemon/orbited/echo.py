from tcp import TCPConnection, TCPConnectionFactory
from twisted.internet import reactor

class EchoConnection(TCPConnection):
    ping_timeout  = 5 # override default of 20.
    ping_interval = 5 # override default of 20
    
    def dataReceived(self, data):
        print "Echo Recv: " + data
        self.send("Echo: " + data)
        
    def connectionMade(self):
        print "EchoConnection Made", self.id
        self.send("Welcome to the Echo Server 0.1")
        DELAY = 15
        for i in range(300):
            reactor.callLater(i*DELAY, self.send, ("Welcome %s!" % i) * 1)
        
    def connectionLost(self):
        if self.id == "ABC":
            self.factory.connections['ABC'] = EchoConnection(self.factory, 'ABC')
        else:
            print "EchoConnection Lost", self.id

class EchoFactory(TCPConnectionFactory):
    protocol = EchoConnection

    def __init__(self, *args, **kwargs):
      TCPConnectionFactory.__init__(self, *args, **kwargs)
      self.connections['ABC'] = EchoConnection(self, 'ABC')