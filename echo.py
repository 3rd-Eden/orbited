from tcp import TCPConnection, TCPConnectionFactory


class EchoConnection(TCPConnection):
    ping_timeout = 5 # override default of 20.
    ping_interval = 5 # override default of 20
    def dataReceived(self, data):
        print "Echo Recv: " + data
        self.send("Echo: " + data)
        
    def connectionMade(self):
        print "EchoConnection Made"
        self.send("Welcome to the Echo Server 0.1")
        
    def connectionLost(self):
        print "EchoConnection Lost"
        

class EchoFactory(TCPConnectionFactory):
    protocol = EchoConnection

