from twisted.internet import reactor
from base import CometTransport
ESCAPE = '_'
PACKET_DELIMITER = '_P'
ARG_DELIMITER = '_A'

class XHRStreamingTransport(CometTransport):
    
    def opened(self):
        # Force reconnect ever 45 seconds
#        self.close_timer = reactor.callLater(45, self.triggerCloseTimeout)
        self.request.setHeader('content-type', 'orbited/event-stream')
        # Safari/Tiger may need 256 bytes
        self.request.write(' ' * 256)
        
    def triggerCloseTimeout(self):
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
    