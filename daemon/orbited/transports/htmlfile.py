from orbited.util import format_block
from orbited import json
from twisted.internet import reactor
from base import HTTPTransport

class HTMLFileTransport(HTTPTransport):
    initial_data = format_block('''
            <html>
             <head>
              <script src="/static/transports/HTMLFileFrame.js"></script>
             </head>
             <body>
        ''')
    initial_data += ' '*max(0, 256-len(initial_data)) + '\n'
    def opened(self):
        # Force reconnect ever 30 seconds
        self.close_timer = reactor.callLater(5, self.close_timeout)
        
        self.request.write(self.initial_data)
        
    def close_timeout(self):
        self.close()
    
    def write(self, packets):
        payload = json.encode(packets)
        self.request.write('<script>e(%s);</script>' % payload)
