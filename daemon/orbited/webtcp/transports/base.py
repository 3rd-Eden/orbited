from twisted.web import server, resource, static, error


class CometTransport(resource.Resource):
  
    def __init__(self, **options):
        self.options = options
        
    def render(self, request):
        self.packets = []
        request = self.request
        self.request.notifiyFinish().addCallback(self.finished)
        self.closeDeferred = defer.Deferred()
        return server.NOT_DONE_YET
    
    
    
   def send_packet(self, name, id, *info):
        self.packets.append((id, name, info))
    
    def flush(self):
        if self.packets:
            self.write(self.packets)
            self.packets = []
            
    def finished(self, arg):
        if open:
            self.request = None
            self.open = False
            self.close()
        
    def onClose(self):
        return self.closeDeferred

    def close(self):
        if not self.open:
            return
        self.open = False
        if self.request:
            self.request.finish()
        self.request = None
        self.closeDeferred.callback(self)
        self.closeDeferred = none
        
    # Override these    
    def write(self, packets):
        raise Exception("NotImplemented")
    
    def opened(self):
        raise Exception("NotImplemented")
