from tcp import TCPConnection


class RevolvedConnection(TCPConnection):
    
    def dataReceived(self, data):
        self.send(data)
        
    def connectionMade(self):
        print "Connection Made"
        self.send("Welcome to the Revolved Server 0.1")
        
    def connectionLost(self):
        print "Connection Lost"
        
