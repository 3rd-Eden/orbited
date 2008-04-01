from orbited.http import HTTPRequest
from orbited.json import json

class UpstreamHandler(object):
    """Handle upstream connections."""
    
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.connections = {}
        self.callbacks = {}
        self.upstream_transports = {}
        for name, class_ in upstream_transports.items():
            self.upstream_transports[name] = class_(self)
            
    def set_connect_cb(self, identifier, cb, args=[]):
        self.callbacks[identifier] = (cb, args)
        
    def new_connection(self, conn):
        print 'NEW CONNECTION:', conn.identifier
        self.connections[conn.identifier] = conn
        if conn.identifier in self.callbacks:
            cb, args = self.callbacks[conn.identifier]
            cb(conn, *args)
        
class XHRUpstreamRouter(object):
    
    def __init__(self, upstream):
        self.upstream = upstream
        self.connections = {}
        self.upstream.dispatcher.app.http_server.add_cb_rule("/_/csp/up", self.http_request)
    
    def __close(self, conn):
        pass
        
    def http_request(self, req):
        req = HTTPRequest(req)
        print "REQUEST: ", req.form
        identifier = req.form.get('identifier', None)
        if not identifier:
            response = req.HTTPResponse()
            response.write(json.encode(["ERR", ["Identifier not specified."]]))
            return
        if identifier not in self.connections:
            self.connections[identifier] = XHRUpstreamConnection(identifier, self.__close)
            self.upstream.new_connection(self.connections[identifier])
        self.connections[identifier].http_request(req)

upstream_transports = {
    'xhr': XHRUpstreamRouter,
}

class XHRUpstreamConnection(object):
    name = 'xhr'
    
    def __init__(self, identifier, close_cb):
        self.identifier = identifier
        self.close_cb = close_cb
        self.receive_cb = None
        
    def set_receive_cb(self, cb, args=[]):
        self.receive_cb = (cb, args)
    
    def http_request(self, req):
        
        payload = req.form.get('payload', None)
        response = req.HTTPResponse()
        # TODO: pre-encode for perf gain
        response.write(json.encode(["OK", []]))
        response.dispatch()
        if self.receive_cb:
            print 'call XHRUpstreamConnection.receive_cb'
            cb, args = self.receive_cb
            cb(payload, *args)
        else: 
            print 'no cb!'
            
    def close(self):
        self.close_cb(self)