from tcp import TCPConnection, TCPConnectionFactory


class EchoConnection(TCPConnection):
    
    def dataReceived(self, data):
        self.send("Echo: " + data)
        
    def connectionMade(self):
        print "Connection Made"
        self.send("Welcome to the Echo Server 0.1")
        
    def connectionLost(self):
        print "Connection Lost"
        

class EchoFactory(TCPConnectionFactory):
    protocol = EchoConnection
