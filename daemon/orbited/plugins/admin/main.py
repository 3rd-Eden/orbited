import event
import simplejson
import os
import event
from time import time
from orbited import plugin
from orbited.log import getLogger
from orbited.orbit import FakeOPRequest
from orbited.http.content import HTTPContent, HTTPClose
import logging


logger = getLogger("AdminPlugin")

class AdminPlugin(plugin.Plugin):
    name = 'admin'
    static = os.path.join(os.path.split(__file__)[0], 'static')
    
    def __init__(self):
        self.connections = {}
        self.admin_connections = {}
        self.events = []
        self.user_agents = {}
        
        self.seconds = [0]
        self.timer = event.timeout(1.0, self.print_bandwidth)
    
    @plugin.hook('>transport.Transport.accept_browser_connection')
    def accept_connection(self, transport, browser_conn):
        ua = browser_conn.request.headers['user-agent']        
        # self.user_agents[transport.key] = self.resolve_ua(ua)
        # event.timeout(0, self.broadcast, None)
    
    @plugin.hook('<transport.create')
    def orbited_connect(self, conn):
        if conn.key[2] == "/_/admin/event":
            self.admin_connections[conn.key] = conn
        self.connections[conn.key] = conn
    
    @plugin.hook('>app.Application.remove_session')
    def orbited_disconnect(self, app, conn, foo, bar, baz):
        del self.connections[conn.key]
        # del self.user_agents[conn.key]        
        if conn.key in self.admin_connections:
            del self.admin_connections[conn.key]       
        # self.broadcast()
    
    @plugin.hook('>transport.Transport.success')
    def event_success(self, conn, request, browser_conn):
        self.events.append(("event", ("success",)))
    
    @plugin.hook('>transport.Transport.failure')
    def event_failure(self, conn, request, browser_conn, reason):
        self.events.append(("event", ("failure",)))
    
    @plugin.hook('>http.http.HTTPConnection.sent_amount')
    def sent_bytes(self, httpconn, amount):
        # add to the bandwidth for the most recent second
        self.seconds[-1] += amount
    
    def print_bandwidth(self):
        # print "second %s: %s bytes" % (len(self.seconds), self.seconds[-1])
        self.send("second %s: %s bytes" % (len(self.seconds), self.seconds[-1]))
        self.seconds.append(0)
        return True
    
    # Application
    def send(self, data):
        data = simplejson.dumps('%s' % data)
        
        for admin in self.admin_connections.values():
            r = FakeOPRequest(data)
            admin.event(r)
    
