from twisted.internet import reactor
from base import CometTransport
ESCAPE = '_'
PACKET_DELIMITER = '_P'
ARG_DELIMITER = '_A'
MAXBYTES = 1024

class XHRStreamingTransport(CometTransport):
    def opened(self):
        self.totalBytes = 0
        # Force reconnect ever 45 seconds
#        self.close_timer = reactor.callLater(45, self.triggerCloseTimeout)
        self.request.setHeader('content-type', 'orbited/event-stream')
        # Safari/Tiger may need 256 bytes
        self.request.write(' ' * 256)
        
    def triggerCloseTimeout(self):
        self.close()
    
    def write(self, packets):
        print 'write', packets
        payload = PACKET_DELIMITER.join([ self.encode(packet) for packet in packets])
        payload += PACKET_DELIMITER
#        print "write:", repr(payload)
        self.request.write(payload)
        self.totalBytes += len(payload)
        if (self.totalBytes > MAXBYTES):
            self.close()
        
        
    def encode(self, packet):
        id, name, info = packet
        output = ""
        args = (id, name) + info
        output += ARG_DELIMITER.join([ str(arg).replace(ESCAPE, ESCAPE*2) for arg in args ])
#        if len(info) > 0:
#            print '==== compare ===='        
#            print info[0]
#            print '====    to   ===='
#            print output
        return output
    
    def writeHeartbeat(self):
#        return
        print 'write heartbeat'
        self.request.write('x')