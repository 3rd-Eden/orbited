from debug import debug
from twisted.internet import reactor
from twisted.python import log
from twisted.internet.protocol import Protocol, ServerFactory
from twisted import internet
from app import App
import urllib
import sys
import cgi

class SimpleHTTPProtocol(Protocol):

    def __init__(self, app):    
        self.buffer = ""
        self.state = "headers"
        self.app = app
        self.request = Request(self)

    def dataReceived(self, data):
        debug("GOT DATA: %s" % data)
        self.buffer += data
        getattr(self, 'state_%s' % self.state)()
                
    def connectionLost(self, reason):
        print "CONNECTION CLOSED: %s" % reason
        pass
        
    def write(self, data):
        self.transport.write(data)
        
    def state_headers(self):
        debug("headers")
        index = self.buffer.find('\r\n\r\n')
        if index == -1:
            debug('exiting headers')
            return
        header_data = self.buffer[:index]
        self.buffer = self.buffer[index+4:]
        lines = header_data.split('\r\n')
        self.request.method, self.request.full_url, self.request.protocol = lines[0].split(' ')
        self.request.url = self.request.full_url.split('?', 1)[0]
        self.request.headers = {}
        for line in lines[1:]:
            key, val = line.split(': ')
            self.request.headers[key.lower()] = val
        self.state = "body"
        self.state_body()
        
    def state_body(self):
        debug("body")
        if 'content-length' not in self.request.headers:
            self.request.headers['content-length'] = '0'
        if int(self.request.headers['content-length']) > len(self.buffer):
            return
        self.request.body = self.buffer[:int(self.request.headers['content-length'])]
        self.buffer = ""
        self.state = "form"
        self.state_form()
        
    def state_form(self):    
        debug("form")
        form_line = ""
        if self.request.method.lower() == 'get':
            if '?' in self.request.full_url:
                form_line = self.request.full_url.split('?',1)[1]           
            else:
                form_line = ''
        elif self.request.method.lower() == 'post':
            form_line = self.request.body
        if form_line:
            form = dict([ j.split('=') for j in form_line.split('&') ])
        else:
            form = dict()
        form = dict([ (k, v.replace('[ampersand]', '&').replace('[equals]', '=')) for (k,v) in cgi.parse_qsl(urllib.urlencode(form)) ])
        self.request.form = form
        self.request_received()
        
    def request_received(self):        
        debug("request_received")
        self.app.dispatch(self.request)
        self.request = Request(self)
        self.state = "headers"
        self.state_headers()
    
class Request(object):
    def __init__(self, conn):
        self.headers = {}
        self.body = None
        self.form = {}
        self.url = None
        self.full_url = None
        self.action = None
        self.protocol = None
        self.method = None
        self.conn = conn
        self.response = Response(conn)
        
class Response(object):
    def __init__(self, conn):
        self.conn = conn
        self.headers = {
            'Content-type': 'text/html',
#            'Connection': 'close',
        }
        self.body = ''
        
    def add_header(self, key, value):
        self.headers[key] = value

    def write(self, data):
        self.body+=data
    
    def render(self):
        self.headers['Content-Length'] = str(len(self.body))
        out = 'HTTP/1.1 200 OK\r\n'
        out += '\r\n'.join([': '.join(j) for j in self.headers.items() ])
        out += '\r\n\r\n'
        out += self.body
        return out
    
    def send(self):
        x = self.render()
        debug("ready to send: %s" % x)
        self.conn.write(x)
    
class SimpleHTTPFactory(ServerFactory):
    protocol = SimpleHTTPProtocol
    def __init__(self, app):
        self.app = app
    
    def buildProtocol(self, addr):
        p = self.protocol(self.app)
        return p

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    app = App()
    factory = SimpleHTTPFactory(app)
    reactor.listenTCP(4700, factory)
    reactor.run()