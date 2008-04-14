from orbited.network.http import HTTPServer


class OrbitedHTTPDaemon(HTTPServer):
  
    def __init__(self, app):
#        HTTPServer.__init__(self)
        self.app = app
        
    def dispatch_request(self, request):
      
        print "incoming:", request.form
        self.app.transports.dispatch_http(request)
        
    
    
        
        