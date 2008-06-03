from twisted.internet import defer, reactor
from twisted.web import server
from twisted.web import resource
from orbited import json
IE_BANNER = "get a real browser"
class HTMLFileConnection(resource.Resource):
  
    def __init__(self, request):
        self.request = request
        request.setHeader("content-type", "text/html; charset=utf-8")
        request.setHeader("cache-control", "no-cache, must-revalidate")
        request.setHeader("expires", "Mon, 26 Jul 1997 05:00:00 GMT")
        request.write("<!-- " + IE_BANNER + " " * (256 - len(IE_BANNER)) + "-->\n")
        request.write("<html><head>\n  <script src=\"/_/static/transports/IEHTMLFileFrame.js\"></script>\n")
        request.write("  <script src=\"/_/static/JSON.js\"></script></head><body>")
        self.close_deferred = defer.Deferred()
        self.timer = reactor.callLater(5, self.close_timeout)
        self.open = True
        self.request.notifyFinish().addCallback(self.finished)
        self.buffer = []
        self.current = {
            'name': None,
            'id': None,
            'retry': None,
            'data': None
        }
        
    def write_event(self, name):
        self.current['name'] = name
        
    def write_data(self, value):
        self.current['data'] = value
        
    def write_id(self, value):
        self.current['id'] = value
        
    def write_retry(self, retry):
        self.current['retry'] = retry
        
    def write_dispatch(self):
        self.buffer.append(self.current)
        self.current = {
            'name': None,
            'id': None,
            'retry': None,
            'data': None
        }
        
    def flush(self):
        if not self.open:
            print "Flushing while closed?!"
            print repr(self.buffer)
            raise "BadFlush", "flushing while closed?!"
        try:
            wbuffer = "<script>\n"
            for event in self.buffer:
                wbuffer+= "  receive("
                wbuffer += json.encode(event['name']) + ', '
                wbuffer += json.encode(event['data']) + ', '
                wbuffer += json.encode(event['id']) + ', '
                wbuffer += json.encode(event['retry']) + ');\n'
            wbuffer += "</script>\n"
            print wbuffer   
            self.request.write(wbuffer)
            self.buffer = []
        except:
            self.close()
                
    def finish(self):
        try:
            self.request.finish()
            self.request = None
        except:
            pass
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