#from orbited.router import router, CSPDestination
from orbited.http import HTTPRequest
import random
import event
#from orbited.dynamic import DynamicHTTPResponse
from orbited.json import json
#from orbited.orbit import InternalOPRequest
#from orbited.config import map as config
from orbited.transport import transports as supported_transports

#router.register(CSPDestination, '/_/csp')
#router.register(StaticDestination, '/_/csp/static', '[orbited-static]')


class CSP(object):
  
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.dispatcher.app.cometwire.set_connect_cb('/_/cometwire/', self.__connect)
        self.connections = {}
        self.packet_ids = {}
        
    def __received(self, id, payload):
        print "CSP received", id, payload
        self.packet_ids[id] += 1
        packet_id = self.packet_ids[id]
        self.connections[id].send(json.encode([packet_id, "PAYLOAD", payload]))
#        self.connections[id].
        
    def __connect(self, id, upstream_conn, downstream_conn):
        print 'CSP connect', id
        self.connections[id] = downstream_conn
        self.packet_ids[id] = 1
        downstream_conn.send(json.encode([1, "WELCOME", []]))
        upstream_conn.set_receive_cb(self.__received)
        
        
    def http_request(self, request):
        request = HTTPRequest(request)
        
        response = request.HTTPResponse()
        id = request.form.get('id', None)
        response.write(json.encode(["OK", [id]]))
        return response.dispatch()
        
        junk, method = request.url.rsplit('/', 1)
        if not hasattr(self, method):
            return request.error("Invalid Method")
        response = request.HTTPResponse()
        return getattr(self, method)(request, response)
    
    def contains(self, key):
        return False


    def signon(self, request, response):
        response.write("CSP Hello World")
        response.dispatch()

