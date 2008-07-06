from orbited.util import format_block
from orbited import json
from twisted.internet import reactor
from base import HTTPTransport

class SSETransport(HTTPTransport):
    
    def opened(self):
        self.request.setHeader('content-type', 'application/x-dom-event-stream')
        
    
    def write(self, packets):
        payload = json.encode(packets)
        data = (
            'Event: orbited\n' +
            '\n'.join(['data: %s' % line for line in payload.splitlines()]) +
            '\n\n'
        )
#        print 'WRITE:', data.replace('\n', '\\n\n').replace('\r', '\\r')
#        print '==='
        self.request.write(data)