from orbited.util import format_block
from orbited import json
from twisted.internet import reactor
from orbited import logging
from orbited.transports.base import CometTransport

MAXBYTES = 1024

class HTMLFileTransport(CometTransport):
    initial_data = format_block('''
            <html>
             <head>
              <script src="../static/HTMLFileFrame.js"></script>
             </head>
             <body>
        ''')
    initial_data += ' '*max(0, 256-len(initial_data)) + '\n'
    def opened(self):
        # Force reconnect ever 30 seconds
        self.totalBytes = 0
        self.close_timer = reactor.callLater(5, self.close_timeout)
        self.request.write(self.initial_data)

    def triggerCloseTimeout(self):
        self.close()

    def write(self, packets):
        payload = '<script>e(%s)</script>' % (json.encode(packets),)
        self.request.write(payload);
        self.totalBytes += len(payload)
        if (self.totalBytes > MAXBYTES):
            self.close()

    def writeHeartbeat(self):
        self.logger.debug('writeHeartbeat')
        self.request.write('<script>h();</script>');

