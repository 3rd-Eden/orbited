from twisted.internet import defer, reactor
from twisted.web import server
from twisted.web import resource
IE_BANNER = ":Get a real browser"

class SSEConnection(resource.Resource):
  
    def __init__(self, request):
        self.request = request
        if 'ie' in request.args:
            request.setHeader("content-type", "text/plain; charset=utf-8")
            request.setHeader("cache-control", "no-cache, must-revalidate")
            request.setHeader("expires", "Mon, 26 Jul 1997 05:00:00 GMT")
            request.write("" + IE_BANNER + "x" * (2560 - len(IE_BANNER)) + "\n")
#            request.write(":<pre>:\n")
        else:
            request.setHeader("content-type", "text/plain; charset=utf-8")            
        self.buffer = ""
        self.close_deferred = defer.Deferred()
        self.timer = reactor.callLater(8   , self.close_timeout)
        self.open = True
        self.request.notifyFinish().addCallback(self.finished)
    def write_event(self, name):
        self.buffer += 'event:%s\r\n' % name
    def write_data(self, value):
        self.buffer += '\r\n'.join(['data:%s' % d for d in value.splitlines()]) + '\r\n'
    def write_id(self, value):
        self.buffer += 'id:%s\r\n' % value
    def write_retry(self, retry):
        self.buffer += 'retry:%s\r\n' % retry
    def write_dispatch(self):
        self.buffer += '\r\n'
    def flush(self):
        if not self.open:
#            print "Flushing while closed?!"
#            print repr(self.buffer)
            raise "BadFlush", "flushing while closed?!"
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
            self.request = None
        self.close()
        
    def close_timeout(self):
        self.timer = None
        self.close()
    
    def finished(self, arg):
        self.close()
        
    def close(self):
        if not self.open:
            return
        self.open = False
        if self.timer:
            self.timer.cancel()
            self.timer = None
        if self.request:
            try:
                self.request.finish()
            except:
                pass
        if self.close_deferred:
            self.close_deferred.callback(self)
            self.close_deferred = None
    
    def onClose(self):
        return self.close_deferred
    
    def getClientIP(self):
        return self.request.getClientIP()