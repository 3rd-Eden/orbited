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
    
    def set_close_cb(self, cb, args=[]):
        self.conn.set_close_cb(cb, args)
    
    def error(self, reason="Unknown", details="", code="500"):
        r = HTTPResponse(self.conn)
        r.status = "%s Orbited Error" % (code,)
        r.write("""
        <html>
          <head>
            <link rel="stylesheet" type="text/css" href="/_/static/orbited.css">
            <title>%s Orbited Error - %s</title>
          </head>
          <body>
            <h1>%s Orbited Error - %s</h1>
            <p>%s</p>
          </body>
        </html>        
        """ % (code, reason, code, reason, details))
        r.dispatch()

# 946 8306 dr chen
# 909 946 6959 Susan
