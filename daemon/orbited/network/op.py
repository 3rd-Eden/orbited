from twisted.internet.protocol import Factory
from twisted.internet import reactor, defer
from connection import StructuredReader

class OPRequest(object):
    def __init__(self):
        self.recipient = None
        self.payload = None
        
        
class OPServerProtocol(StructuredReader):
    def __init__(self):
        StructuredReader.__init__(self)
        
    def write(self, data):
        return self.transport.write(data)
    def connectionMade(self):
        self.start_request()
        
        
    def start_request(self):
        self.request = OPRequest()
        self.set_rmode_delimiter('\r\n').addCallback(self.recv_recipient)
        
    def recv_recipient(self, recipient):
        self.request.recipient = recipient
        self.set_rmode_delimiter('\r\n').addCallback(self.recv_payload)
        
    def recv_payload(self, payload):
        self.request.payload = payload
        self.factory.dispatch(self.request)
        self.write('OK\r\n')
        self.start_request()
        
        
class OPServer(Factory):
    protocol = OPServerProtocol
    def dispatch(self, request):
        pass
    
    
