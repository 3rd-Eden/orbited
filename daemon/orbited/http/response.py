
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
    
class HTTPResponse(object):
    
    def __init__(self, request):
        self.request = request
        self.headers = {}
        self.buffer = []
        self.status = "200 OK"
        self.version_major = 1
        self.version_minor = 1
    
    def __setitem__(self, key, val):
        self.headers[key] = val
    
    def __getitem__(self, key):
        return self.headers[key]
    
    def write(self, data):
        self.buffer.append(data)
    
    def render(self):
        status_line = "HTTP/%s.%s %s\r\n" % (
            self.version_major, self.version_minor, self.status)
        self.headers['Content-length'] = str(sum([len(s) for s in self.buffer]))
        h = "\r\n".join(": ".join((k, v)) for (k, v) in self.headers.items())
        h += "\r\n\r\n"
        response = status_line + h + "".join(self.buffer)
        self.request.respond(HTTPContent(response))
        self.request.respond(HTTPRequestComplete())


class WSGIResponse(object):
    
  
    def __init__(self, request, app, hostname, port):
        self.hostname = hostname
        self.port = port
        self.response = HTTPResponse(request)
        self.environ = {}
        self.stderror = StringIO()
        self.setup_environ()
        
    def dispatch(self):
        output = self.app(self.environ, self.start_response)
        for data in output:
            self.response.write(data)
        self.response.render()
        
    def start_response(self, status, headers):
        self.response.status = status
        self.response.headers.update(headers)
        
    def setup_environ(self):
        environ = self.environ
        request = self.request
        environ['REQUEST_METHOD'] = request.method
        path, qs = request.url.split('?', 1)
        path_info, script_name = path.rsplit('/')
        environ['PATH_INFO'] = path_info
        environ['SCRIPT_NAME'] = script_name
        environ['QUERY_STRING'] = qs
        content_type = request.headers.get('content-type', None)
        if content_type:
            environ['CONTENT_TYPE'] = content_type
        content_length = request.headers.get('content-length', None)
        if content_length:
            environ['CONTENT_LENGTH'] = content_length
        environ['wsgi.urlscheme']    = 'http'
        environ['wsgi.input']        = StringIO(request.body)
        environ['wsgi.errors']       = self.stderror
        environ['wsgi.version']      = (1,1)
        environ['wsgi.multithread']  = False
        environ['wsgi.multiprocess'] = False
        environ['wsgi.run_once']     = False 
