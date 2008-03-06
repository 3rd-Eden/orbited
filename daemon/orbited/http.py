from dez.http.server import HTTPResponse, RawHTTPResponse

class HTTPRequest(object):
  
    def __init__(self, request):
        self.headers = request.headers
        self.conn = request
        self.url = request.url
        self.form = request.form
        self.cookies = request.cookies
        
    def RawHTTPResponse(self):
        return RawHTTPResponse(self.conn)
    
    def HTTPResponse(self):
        return HTTPResponse(self.conn)
    
    def set_close_cb(self, cb, args):
        self.conn.set_close_cb(cb, args)
    
    def error(self, reason="Unknown", details=""):
        r = HTTPResponse(self.conn)
        r.status = "500 Orbited Error"
        r.write("""
        <html>
          <head>
            <link rel="stylesheet" type="text/css" href="/_/static/orbited.css">
            <title>500 Orbited Error - %s</title>
          </head>
          <body>
            <h1>500 Orbited Error - %s</title>
            %s
          </body>
        </html>        
        """ % (reason, reason, details))
        r.dispatch()

# 946 8306 dr chen
# 909 946 6959 Susan
