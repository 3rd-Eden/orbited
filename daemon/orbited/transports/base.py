from twisted.web import server, resource, static, error
from twisted.internet import defer, reactor

class CometTransport(resource.Resource):
  
    def __init__(self, conn):
        self.conn = conn
        self.open = False
        
    def render(self, request):
        self.open = True
        self.packets = []
        self.request = request
        self.opened()
#        self.request.notifiyFinish().addCallback(self.finished)
        self.resetHeartbeat()
        self.closeDeferred = defer.Deferred()        
        self.conn.transportOpened(self)
        return server.NOT_DONE_YET
    
    def resetHeartbeat(self):
        self.heartbeatTimer = reactor.callLater(5, self.doHeartbeat)
        
    def doHeartbeat(self):
        self.writeHeartbeat()
        self.resetHeartbeat()
        
    def sendPacket(self, name, id, *info):
        self.packets.append((id, name, info))
    
    def flush(self):
        if self.packets:
            self.write(self.packets)
            self.packets = []
        if self.heartbeatTimer:
            self.heartbeatTimer.cancel()
            self.resetHeartbeat()
        
            
    def finished(self, arg):
        if self.open:
            self.request = None
            self.open = False
            self.close()
        
    def onClose(self):
        return self.closeDeferred
    

    def close(self):
        if not self.open:
            return
        self.heartbeatTimer.cancel()
        self.heartbeatTimer = None
        self.open = False
        if self.request:
            self.request.finish()
        self.request = None
        self.closeDeferred.callback(self)
        self.closeDeferred = None
        
    # Override these    
    def write(self, packets):
        raise Exception("NotImplemented")
    
    def opened(self):
        raise Exception("NotImplemented")

    def writeHeartbeat(self):
        raise Exception("NotImplemented")