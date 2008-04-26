from tcp import TCPConnection


class RevolvedConnection(TCPConnection):
    
    def dataReceived(self, data):
        self.send(data)
        
    def connectionMade(self):
        print "Connection Made"
        self.send("Welcome to the Revolved Server 0.1")
        
    def connectionLost(self):
        print "Connection Lost"
        

class OpenAuth(object):

    def connect(self, user, *credentials):
        return True
    def channel(self, 
        
class RevolvedFactory(TCPConnectionFactory):
    protocol = RevolvedConnection
    auth = OpenAuth
    pubsub = MemoryPubSub
    
    def __init__(self):
        TCPConnectionFactory.__init__(self)
        self.auth_plugin = 

