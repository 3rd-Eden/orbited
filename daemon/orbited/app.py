from orbit import OrbitDaemon
from http import HTTPDaemon
import event
import sys
from debug import *
import log
from config import map as config
from admin import AdminApp
import transport
import traceback
import StringIO
#config = config.map
"""
app:    
    stores all requests
    executes requests
    replies to requests
   
   
daemon:
    accepts socket connections. creates connection objects
    
connection:
    reads data and creates new requests as needed
request:
    processes read data and stores info about a request
    
"""

class App(object):

    def __init__(self):
        self.requests = dict()
        self.connections = dict()
        log.create(self)
        self.log = log.log
        self.admin = None
        if config['[global]']['admin.enabled'] == '1':
            self.admin = AdminApp(self, int(config['[admin]']['admin.port']))
        self.daemon = OrbitDaemon(self, self.log, int(config['[global]']['orbit.port']))
#        if int(config['proxy']):
        self.http = HTTPDaemon(self, self.log, int(config['[global]']['http.port']), config['[proxy]'])
        transport.load_transports()
        
    def accept_orbit_request(self, request):
        self.log("ACCESS", "ORBIT\t%s/%s\t%s" % (request.connection.addr[0], request.id, request.length))
        self.requests[request.key()] = request
        self.dispatch_request(request)

        
    def dispatch_request(self, request):
        for recipient in request.recipients:
            if recipient in self.connections:
                self.connections[recipient].respond(request)
            else:
                self.log("ERROR", "ORBIT\t%s/%s\tRecipient %s not Found" % (request.connection.addr[0], request.id, recipient))
                request.error(recipient)
                    
        self.requests.pop(request.key())
        
    def accept_http_connection(self, connection):
        try:
            if connection.key() not in self.connections:
                self.connections[connection.key()] = transport.create(connection, self)        
                
            elif connection.request.transport_name != self.connections[connection.key()].name:
                print "TRANSPORT EXISTS. Switching: %s -> %s" % (self.connections[connection.key()].name, connection.request.transport_name)
                self.connections[connection.key()].close()
                self.connections[connection.key()] = transport.create(connection, self)
            self.connections[connection.key()].accept_http_connection(connection)
#            self.log('close_http_connection', self.connections[connection.key()]) 
#            self.connections[connection.key()].close()
        except"InvalidTransport":                
            self.log("ERROR", "HTTP\t%s\tTransport \"%s\" Not Found" % (connection.addr[0], connection.request.transport_name))
            connection.close()
            return

    def expire_http_connection(self, connection):
        if connection.key() in self.connections:
            self.connections[connection.key()].expire_http_connection(connection)
        
    def start(self):
    
        def collect_toplevel_exceptions():
            return True
            
        event.timeout(1, collect_toplevel_exceptions)
        while True:
            try:
                event.dispatch()
            except KeyboardInterrupt, k:
                event.abort()
                print "Received Ctr+c shutdown"
                break
            except Exception, e:
                exception, instance, tb = traceback.sys.exc_info()

                # Start: There is certainly a better way of doing this
                x = StringIO.StringIO()
                traceback.print_tb(tb, file=x)
                relevant_line = x.getvalue().split('\n')[-3]
                # End: Find a better way
                
                self.log("ERROR", "%s:%s\t%s" % (exception, instance, relevant_line))
            
if __name__ == "__main__":
    a = App()
    a.start()
    