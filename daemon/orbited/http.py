from dez.http.server import HTTPResponse, RawHTTPResponse

class HTTPRequest(object):
  
    def __init__(self, request):
        self.headers = request.headers
        self.conn = request
        self.form = {}
        
    def RawHTTPResponse(self):
        return RawHTTPResponse(self.conn)
    
    def HTTPResponse(self):
        return HTTPResponse(self.conn)
        

# 946 8306 dr chen
# 909 946 6959 Susan
