from twisted.internet import defer
from twisted.web import server
from twisted.web import resource
IE_BANNER = ":Get a real browser"

class SSEConnection(resource.Resource):
    def __init__(self, request):
        self.request = request
        if 'ie' in request.args:
            request.setHeader("content-type", "text/plain")
            request.setHeader("cache-control", "no-cache, must-revalidate")
            request.setHeader("expires" "Mon, 26 Jul 1997 05:00:00 GMT")
#            del request.headers['content-type']
            request.write("" + IE_BANNER + " " * (256 - len(IE_BANNER)) + "\n")
#            request.write(":<pre>:\n")
        else:
            request.setHeader("content-type", "text/event-stream")
        self.buffer = ""
        self.close_deferred = defer.Deferred()

    def write_event(self, name):
        self.buffer += 'event:%s\r\n' % name
    def write_data(self, value):
        self.buffer += '\n'.join(['data:%s' % d for d in value.splitlines()]) + '\n'
    def write_id(self, value):
        self.buffer += 'id:%s\n' % value
    def write_retry(self, retry):
        self.buffer += 'retry:%s\n' % retry
    def write_dispatch(self):
        self.buffer += '\r\n'
    def flush(self):
        try:
            self.request.write(self.buffer)
            self.buffer = ""
        except:
            self.close()
                
    def finish(self):
        try:
            self.request.finish()
            self.request = None
        except:
            pass
        self.close()
        
        
    def close(self):
        self.close_deferred.callback(self)
    
    def onClose(self):
        return self.close_deferred
    
    def getClientIP(self):
        return self.request.getClientIP()