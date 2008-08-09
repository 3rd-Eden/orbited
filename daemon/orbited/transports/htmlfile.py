from orbited.util import format_block
from orbited import json
from twisted.internet import reactor
from orbited import logging
from orbited.transports.base import CometTransport
from twisted.web import resource
MAXBYTES = 1048576
#MAXBYTES = 64 # for testing

from orbited import logging
logger = logging.get_logger('orbited.transports.xhrstream.HTMLFileTransport')
class HTMLFileTransport(CometTransport):
    initialData = format_block('''
            <html>
             <head>
              <script src="../../static/HTMLFileFrame.js"></script>
             </head>
             <body>
        ''')
    initialData += ' '*max(0, 256-len(initialData)) + '\n'
    def opened(self):
        logger.debug('opened!')
        # Force reconnect ever 30 seconds
        self.totalBytes = 0
#        self.closeTimer = reactor.callLater(5, self.triggerCloseTimeout)
        self.request.setHeader('cache-control', 'no-cache, must-revalidate')
        self.request.write(self.initialData)

    def triggerCloseTimeout(self):
        self.close()

    def write(self, packets):
        # TODO make some JS code to remove the script elements from DOM
        #      after they are executed.
        payload = '<script>e(%s)</script>' % (json.encode(packets),)
        self.request.write(payload);
        self.totalBytes += len(payload)
        if (self.totalBytes > MAXBYTES):
            self.close()

    def writeHeartbeat(self):
        logger.debug('writeHeartbeat')
        self.request.write('<script>h();</script>');



class CloseResource(resource.Resource):
  
    def getChild(self, path, request):
        return self
    
    def render(self, request):      
        return format_block('''
            <html>
             <head>
              <script src="../../static/HTMLFileClose.js"></script>
             </head>
             <body>
             </body>
            </html> 
        ''')