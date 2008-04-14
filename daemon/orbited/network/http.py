import cgi
from twisted.internet.protocol import Factory
from twisted.internet import reactor, defer
from connection import StructuredReader


class HTTPRequest(object):
  
    def __init__(self, conn):
        self.conn = conn
        self.headers = {}
        self.content_length = 0
        self.chunked = False
        self.body = ""
        self.qs = ""
        
    def _get_form(self):
        if not hasattr(self, '_form'):
            self._form = {}
            try:
                if self.method.lower() == "get":
                    qs = self.qs
                else:
                    qs = self.body
                for key, val in cgi.parse_qsl(qs):
                    self.form[key] = val
            except ValueError:
                raise HTTPProtocolError, "Invalid querystring format"
        return self._form
            
    form = property(_get_form)
    def __str__(self):
        out = "<<< HTTPServerRequest:\n"
        out += "%s %s %s\r\n" % (self.method, self.url, self.version)
        out += '\r\n'.join(['%s: %s' % (k, v) for (k, v) in self.headers.items() ])
        out += '\r\n\r\n'
        out += self.body
        out += "\n>>>"
        return out
    
    def error(self, reason="Unknown", details="", code="500"):
        r = self.HTTPResponse()
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
    
    def HTTPResponse(self):
        return HTTPResponse(self)
    
    def RawHTTPResponse(self):
        return RawHTTPResponse(self)
    
    def HTTPVariableResponse(self):
        return HTTPVariableResponse(self)
    
    def write(self, data):
        self.conn.write(self, data)
        
    def end(self, *args, **kwargs):
        return self.conn.end(self, *args, **kwargs)
    
    def close(self, *args, **kwargs):
        return self.conn.close(self, *args, **kwargs)
    
    def set_status_line(self, line):
        try:
            self.method, self.url, self.protocol = line.split(' ',2)
        except ValueError:
            raise HTTPProtocolError, "Invalid HTTP status line"
        #self.protocol = self.protocol.lower()
        if self.method.lower() == "get" and "?" in self.url:
            self.url, self.qs = self.url.split('?', 1)        
        url_scheme, version = self.protocol.split('/',1)
        self.version = version
        major, minor = version.split('.', 1)
        self.version_major = int(major)
        self.version_minor = int(minor)
        self.url_scheme = url_scheme.lower()
        
    def set_header(self, key, val):
        self.headers[key] = val
        
        if key.lower() == 'content-length':
            self.content_length = int(val)
            
        if key.lower() == 'transfer-encoding' and val.lower() == 'chunked':
            self.chunked = True
        
    def set_body(self, data):
        self.body = data
        
    def get_body(self):
        return self.conn.get_body()

class RawHTTPResponse(object):
    def __init__(self, request):
        self.request = request
        
    def write_status(self, status):
        return self.request.conn.write("%s %s\r\n" % (self.request.version, status))
    
    def write_header(self, key, val):
        return self.request.conn.write("%s: %s\r\n" % (key, val))

    def write_headers_end(self):
        return self.request.conn.write("\r\n")
    
    def write(self, data):
        return self.request.conn.write(data)
    
class HTTPResponse(object):
  
    def __init__(self, request):
        self.request = request
        self.headers = {
            'Content-type': 'text/html'
        }
        self.buffer = []
        self.status = "200 OK"
        self.version_major = 1
        self.version_minor = min(1, request.version_minor)
        if self.version_minor == 1:
            self.headers['Connection'] = 'keep-alive'
            self.headers['Keep-alive'] = '300'

    def write(self, data):
        self.buffer.append(str(data))

    def dispatch(self):
        status_line = "HTTP/%s.%s %s\r\n" % (
            self.version_major, self.version_minor, self.status)
        self.headers['Content-length'] = str(sum([len(s) for s in self.buffer]))
        h = "\r\n".join(": ".join((k, v)) for (k, v) in self.headers.items())
        h += "\r\n\r\n"
        response = status_line + h + "".join(self.buffer)
        self.request.write(response)
        if self.version_minor == 1 and int(self.headers.get('Keep-alive', '0')) > 0:
            self.request.end(close=False)
        else:
            self.request.end(close=True)
        # TODO: make it so .end will generate a Deferred instead of returning
        #       the deferred that writing an empty string produces
        return self.request.write("")
    
class HTTPVariableResponse(object):
    def __init__(self, request):
        self.request = request
        self.started = False
        self.headers = {
            'Content-type': 'text/html'
        }
        self.status = "200 OK"
        self.version_major = 1
        self.version_minor = min(1, request.version_minor)
        if self.version_minor == 1:
            self.headers['Connection'] = 'keep-alive'
            self.headers['Keep-alive'] = '300'
            self.headers['Transfer-encoding'] = 'chunked'
            
    def write(self, data):
        print 'write:', data
        if not self.started:
            self.start_response()
        if not data:
            return defer.succeed(None)
        if self.version_minor == 1:
            return self.write_chunk(data)
        else:
            return self.request.write(data)

    def write_chunk(self, data, cb=None, args=[]):
        return self.request.write("%X\r\n%s\r\n"%(len(data),data))

    def start_response(self):
        self.started = True
        status_line = "HTTP/%s.%s %s\r\n" % (
            self.version_major, self.version_minor, self.status)
        h = "\r\n".join(": ".join((k, v)) for (k, v) in self.headers.items())
        h += "\r\n\r\n"
        response = status_line + h
        return self.request.write(status_line + h)

    def end(self):
        if self.version_minor == 1:
            self.write_chunk("")
            if int(self.headers.get('Keep-alive', '0')) > 0:
                self.request.end(close=False)
            else:
                self.request.end(close=True)
        else:
            self.request.end()
            
    
class HTTPServerProtocol(StructuredReader):
    id = 0
    def __init__(self):
        StructuredReader.__init__(self)
        self.request = None
        HTTPServerProtocol.id += 1
        self.id = HTTPServerProtocol.id
        self.response_queue = []
        
    def write(self, request, data):
        if self.response_queue and request == self.response_queue[0]:
            return self.transport.write(data)
        else:
            pass
            # TODO: hold on to the write and buffer it until its this request's
            #       turn to write
    def end(self, request, close=False):
        self.response_queue.remove(request)
        
        # TODO: see if any data were buffered for the next request and start
        #       writing them
        
        # TODO: close the connection if close == True
        
    def connectionMade(self):
        print "HTTP Connection opened: %s" % self.id
        self._start_request()
      
    def _start_request(self):
        self.request = HTTPRequest(self)
        self.response_queue.append(self.request)
        self.set_rmode_delimiter('\r\n').addCallback(self._recv_status)
        
    def get_body(self):
        if not self.request.chunked and self.request.content_length == 0:
            request = self.request
            self._start_request()
            return defer.succeed(request)
        
        self.body_defer = defer.Deferred()            
        if self.request.chunked:
            raise HTTPProtocolError("No support for transfer-encoding chunked uploads")
            self.set_rmode_delimiter('\r\n').addCallback(self._recv_chunk_size)
        else: # we have a size
            self.set_rmode_size(self.request.content_length).addCallback(self._recv_body)
            
        return self.body_defer
        
    def _recv_body(self, data):
        self.request.set_body(data)
        d = self.body_defer
        self.body_defer = None
        request = self.request
        self._start_request()
        d.callback(request)
        
    def _recv_status(self, data):
        self.request.set_status_line(data)
        self.set_rmode_delimiter('\r\n').addCallback(self._recv_header)
        
    def _recv_header(self, data):
        if data == "":
            return self._received_headers()
        key, val = data.split(': ', 1)
        self.request.set_header(key, val)
        self.set_rmode_delimiter('\r\n').addCallback(self._recv_header)
                
    def _received_headers(self):
        self.factory.dispatch_initial_request(self.request)
        
class HTTPServer(Factory):
    protocol = HTTPServerProtocol
    def dispatch_initial_request(self, request):
        request.get_body().addCallback(self.dispatch_request)
        
    def dispatch_request(self, request):
      
        response = request.HTTPVariableResponse()
        reactor.callLater(0, response.write, "Testing123<br>\n")
        reactor.callLater(.4, response.write, "456?<br>\n")
        reactor.callLater(.8, response.write, "789!<br>\n")
        reactor.callLater(1.2, response.end)
        return 
        response = request.RawHTTPResponse()
        response.write_status("200 Ok")
        response.write_header("Content-length", "11")
        response.write_header("Content-type", "text/html")
        response.write_headers_end()
        response.write("hello world")
        
if __name__ == "__main__":
    factory = HTTPServer()
    
    # 8007 is the port you want to run under. Choose something >1024
    reactor.listenTCP(8007, factory)
    reactor.run()
