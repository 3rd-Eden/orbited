from twisted.internet import reactor
from orbited.http import OrbitedHTTPDaemon
from orbited.op import OrbitedOPDaemon
from orbited.transport import TransportHandler
from orbited.tcp import TCPHandler

class Application(object):
  
    def __init__(self):
        self.httpd = OrbitedHTTPDaemon(self)
        self.opd = OrbitedOPDaemon(self)
        self.tcp = TCPHandler(self)
        self.handlers = {}
#        self.transports = TransportHandler(self)
        
    def start(self):
        reactor.listenTCP(8000, self.httpd)
        reactor.listenTCP(9000, self.opd)
        reactor.run()
    
    def event(self, event):
#        print 'got event', event
#        print 'id', event.id
#        print 'name', event.name
#        print '============'
        
        if event.id in self.handlers:
            handler = self.handlers[event.id]
            handler.event(event)
        elif None in self.handlers:
            handler = self.handlers[None]
            handler.event(event)
        else:
            print "EVENT!", event
        
        
    def set_session_handler(self,handler,id=None):
        self.handlers[id] = handler
        
