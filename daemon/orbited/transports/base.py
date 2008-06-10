from twisted.internet import defer, reactor

class HTTPTransport(object):
  
    def __init__(self, request):
        self.packets = []
        self.request = request
        self.opened()
        self.close_deferred = defer.Deferred()
        self.open = True
        self.request.notifyFinish().addCallback(self.finished)
        
    def send_packet(self, name, id, *info):
#        print 'sending packet:', (id, name, info)
        self.packets.append((id, name, info))
    
    def flush(self):
        if self.packets:
            self.write(self.packets)
            self.packets = []
    
    def close(self):
        if not self.open:
            return
        self.open = False
        if self.request:
            # TODO: do a check here
            try:
                self.request.finish()
            except:
                pass
            self.request = None
        if self.close_deferred:
            self.close_deferred.callback(self)
            self.close_deferred = None
    

    
    def finished(self, arg):
        self.request = None
        self.close()
    
    def onClose(self):
        return self.close_deferred
    
    def getClientIP(self):
        return self.request.getClientIP()        
    
    # Override these methods
    
            
    def write(self, packets):
        raise Exception("NotImplemented")
    
    def opened(self):
        raise Exception("NotImplemented")

