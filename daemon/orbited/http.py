from dez import HTTPDaemon, HTTPResponse, RawHTTPResponse
from orbited.config import map as config
httpconf = config['[http]']

class HTTPServer(object):
    
    def __init__(self, dispatcher):
        self.dispather = dispatcher
        self.daemon = HTTPDaemon(httpconf['bind_addr'], int(httpconf['port']))
        self.daemon.register_catch(self.request)
        
        
    def request(self, req):
        self.dispatcher.http_request(req)
        
    def proxy(self, req, addr, port):
        raise Exception("ProxyNotImplemented"), "proxy functionality has not been implemented"
    
    def static(self, req, url_base, local_base):
        raise Exception("StaticNotImplemented"), "static content serving has not been implemnted"
    
    def not_found(self, req):
        pass
        
        
        
        
        
class HTTPRequest(object):
  
    def __init__(self, request):
        self.form = {}
        self.headers = request.headers
        self.conn = request
        
    def RawHTTPResponse(self):
        return RawHTTPResponse(self)
    
    def HTTPResponse(self):
        return HTTPResponse(self)
        
        
    



#946 8306 dr chen
#909 946 6959 Susan
