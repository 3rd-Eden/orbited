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
        self.example_handler = ExampleHandler(self)
#        self.transports = TransportHandler(self)
        
    def start(self):
        reactor.listenTCP(8000, self.httpd)
        reactor.listenTCP(9000, self.opd)
        reactor.run()
    
    def event(self, event):
        if event.id in self.handlers:
            handler = self.handlers[event.id]
            handler.event(event)
        else:
            print "EVENT!", event
        
        
    def set_session_handler(self,id, handler):
        self.handlers[id] = handler
        
        
        
class ExampleHandler(object):
    def __init__(self, app):
        self.app = app
        self.app.set_session_handler('abc', self)
        
    def event(self, event):
        conn = self.app.tcp.connections[event.id]
        if event.name == "open":
            self.on_open(conn)
        if event.name == "recv":
            self.on_recv(conn, event.data)
        if event.name == "close":
            self.on_close(conn)
        
    def on_open(self, conn):
        conn.send("Welcome to the Example app!")
    
    def on_recv(self, conn, data):
        conn.send("You sent: " + data)
        
    def on_close(self, conn):
        print "Lost Connection to: %s" % (conn.id,)