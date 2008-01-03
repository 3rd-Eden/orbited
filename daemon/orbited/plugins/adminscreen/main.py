import event
import simplejson
import os
from orbited.plugin import RawPlugin
from orbited.log import getLogger
from orbited.orbit import FakeOPRequest
from orbited.util import formatBlock
from orbited.http.content import HTTPContent, HTTPClose
import logging

logger = getLogger('AdminScreen')
#logger.setLevel(logging.DEBUG)

class AdminScreen(RawPlugin):
    name = "adminscreen"
    hooks = {
        '<transport.create': 'add_transport',
        '>app.Application.remove_session': 'remove_transport',
        '>transport.Transport.success': 'event_success',
        '>transport.Transport.failure': 'event_failure',
        '>transport.Transport.accept_browser_connection': 'accept_connection',
#        '>http.http.HTTPConnection.dispatch': 'http_connect',
    }
    
    routing = {
        'base': '/_/adminscreen',
        
        'ORBITED': [
            '/event',
        ],
        'static': {
            '/static': os.path.join(os.path.split(__file__)[0], 'static'),
        }
    }
    
    def __init__(self):
#        logger.debug("init..")
        self.connections = {}
        self.admin_connections = {}
#        self.timer = event.timeout(2, self.broadcast)
        self.events = []
        self.user_agents = {}

    def dispatch(self, request):
        logger.info("dispatch!: %s" % request)
        headers = formatBlock('''
            HTTP/1.0 200 Ok
            Connection: close
        ''') + '\r\n\r\n'
        request.respond(HTTPContent(headers))
        request.respond(HTTPContent("hello world from adminscreen!<br>\nurl: %s" % request.url))
        request.respond(HTTPClose())
        
    # Hooks
    def accept_connection(self, transport, browser_conn):
#        logger.debug("accept_connection")
        ua = browser_conn.request.headers['user-agent']        
        self.user_agents[transport.key] = self.resolve_ua(ua)
        event.timeout(0, self.broadcast, None)
        # return browser_conn
        
    
    def add_transport(self, conn):
#        logger.debug("add_transport, connection = %s" % (conn,))
        if conn.key[2] == "/_/adminscreen/event":
            self.admin_connections[conn.key] = conn
        self.connections[conn.key] = conn
    
    def remove_transport(self, app, conn):
#    logger.debug("remove_transport")
        del self.connections[conn.key]
        del self.user_agents[conn.key]        
        if conn.key in self.admin_connections:
            del self.admin_connections[conn.key]       
        self.broadcast()
            
    def event_success(self, conn, request, browser_conn):
#        logger.debug("event_success")
        self.events.append(("event", ("success",)))
    
    def event_failure(self, conn, request, browser_conn, reason):
#        logger.debug("event_failure")
        self.events.append(("event", ("failure",)))
    
#    def http_connect(self, http_conn):
#        ua = http_conn.request.headers['user-agent']
#        self.send(ua)
    
    # Application 
    def send(self, data):
        data = simplejson.dumps("<p>%s</p>\n" % data)
        
        for admin in self.admin_connections.values():
            r = FakeOPRequest(data)
            admin.event(r)

    def ua_count(self):
        count = {
            'opera': 0,
            'safari': 0,
            'gecko': 0,
            'msie': 0,
            'other': 0,
        }
        for key, ua in self.user_agents.items():
            count[ua] += 1
        return count
        
    def resolve_ua(self, ua):
        ua = ua.lower()
#        logger.debug("find: %s" % ua)
        if ua.find('opera') !=-1:
            return 'opera'
        elif ua.find('webkit') != -1:
            return 'safari'
        elif ua.find('gecko') != -1:
            return 'gecko'
        elif ua.find('msie') != -1:
            return 'msie'
        else:
            return 'other'
    
    def broadcast(self, repeat=True):
        # logger.debug("broadcast")
        if not self.admin_connections:
            return repeat
        self.send(self.generate_payload())
        self.reset_payload()
        return repeat
    
    def generate_payload(self):
#        logger.debug("generate_payload")
        return self.ua_count()
        if not hasattr(self, 'testid'):
            self.testid = 0
        self.testid += 1
        return simplejson.dumps("<p>%s</p>\n" % self.testid)
    
    def reset_payload(self):
        # logger.debug("reset_payload")
        pass
    
