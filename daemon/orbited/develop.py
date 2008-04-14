from dez.http.server import HTTPResponse
from orbited.http import HTTPRequest
from orbited.json import json

class Development(object):
  
    def __init__(self, app):
        self.app = app
        self.app.dispatcher.add_cb_rule('/_/develop/', self.http_request)
        
    def http_request(self, req):
        # remove "/_/develop/" part of url
        print "develop:", req.url, req.body
        req = HTTPRequest(req)
        action = req.url[11:]
        if len(action) == 0:
            return self.index(req)
        elif hasattr(self, action):
            return getattr(self, action)(req)
        else:
            req.error("Not Found", code="404",
                details="Could not find %s." % (req.url,))
                
                
                
    def index(self, req):
        pass
    
    def send(self, req):
        response = req.HTTPResponse()
        if not self.app.transports.contains('develop'):          
            response.write(json.encode(["ERR", ["Not Connected"]]))
        else:
            close = False
            payload = req.conn.body
            payload = payload.replace('\\r', '\r').replace('\\n', '\n')
            payload = payload.replace('\\\\', '\\')
            if payload.endswith('\\0'):
                payload = payload[:-2]
                close = True
            print "SEND"
            print payload.replace('\\', '\\\\').replace('\r', '\\r').replace('\n', '\\n\n')
            self.app.transports.get('develop').send(payload)
            response.write(json.encode(["OK", []]))
            if close:
                print 'closing'
                self.app.transports.get('develop').transport.browser_conn.close()
                
        response.dispatch()
