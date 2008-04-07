class RevolvedDispatcher(object):    
    def __init__(self):
        self.connections = {}
        
    def connect(self, user, conn):
        print 'user connected', user, conn
        self.connections[user] = conn
        
    def disconnect(self, user):
        del self.connections[user]
    
    def send(self, sender, recipient, payload):
        """Send a message to the Revolved user."""
        self.connections[recipient].send(["SEND", [sender, payload]])
    
    def publish(self, recipient, channel, sender, payload):
        """Send a message to a recipient with the specified channel."""
        self.connections[recipient].send(["PUBLISH", [channel, sender, payload]])
        