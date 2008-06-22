from twisted.internet import reactor
from base import HTTPTransport
ESCAPE = '_'
PACKET_DELIMITER = '_P'
ARG_DELIMITER = '_A'

class XHRStreamingTransport(HTTPTransport):
    
    def opened(self):
        # Force reconnect ever 30 seconds
        self.close_timer = reactor.callLater(30, self.close_timeout)
        self.request.setHeader('content-type', 'orbited/event-stream')
        # Safari/Tiger may need 256 bytes
        self.request.write(' ' * 256)
    def close_timeout(self):
        self.close()
    
    def write(self, packets):
        payload = PACKET_DELIMITER.join([ self.encode(packet) for packet in packets])
        payload += PACKET_DELIMITER
#        print "write:", repr(payload)
        self.request.write(payload)
        
        
    def encode(self, packet):
        id, name, info = packet
        output = ""
        args = (id, name) + info
        output += ARG_DELIMITER.join([ str(arg).replace(ESCAPE, ESCAPE*2) for arg in args ])
        return output
    