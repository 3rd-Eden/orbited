from twisted.internet import reactor
from orbited.http import OrbitedHTTPDaemon
from orbited.op import OrbitedOPDaemon
from orbited.transport import TransportHandler

class Application(object):
  
    def __init__(self):
        self.httpd = OrbitedHTTPDaemon(self)
        self.opd = OrbitedOPDaemon(self)
        self.transports = TransportHandler(self)
        
    def start(self):
        reactor.listenTCP(8000, self.httpd)
        reactor.listenTCP(9000, self.opd)
        reactor.run()
    