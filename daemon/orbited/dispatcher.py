#from orbited.router import * # router, CSPDestination, StaticDestination, etc.
from orbited.system import System
#from orbited.op.message import O
from orbited.config import map as config

class Dispatcher(object):
  
    def __init__(self, app):
        self.app = app
        self.setup()
        
#    /_/plugin/

    def dispatch_orbit(self, event):
            
        for recipient in event.recipients:
            if self.csp.contains(recipient):
                self.csp.dispatch(event.single_recipient_event(recipient))
            elif self.transports.contains(recipient):
                self.transports.event(event.single_recipient_event(recipient))
            else:
                event.failure(recipient, "not connected")
    
    def transport_http_request(self, req):
        self.transports.http_request(req)
        
    def revolved_http_request(self, req):
        self.revolved.http_request(req)
        
    def csp_http_request(self, req):
        self.csp.http_request(req)
                
    def setup_routing(self):
        for prefix, (rule, params) in config['[routing]'].items():
            if rule == "transport":
                self.app.http_server.add_cb(prefix, self.transport_http_request)
            elif rule == "csp":
                self.app.http_server.add_cb(prefix, self.csp_http_request)
            elif rule == "revolved":
                self.app.http_server.add_cb(prefix, self.revolved_http_request)            
            elif rule == "system":
                self.app.http_server.add_cb(prefix, self.app.system.http_request)
            elif rule == "static":
                local_source = params[0]
                http_server.add_static_rule(prefix, local_source)
            elif rule == "proxy":
                host, port = params
                http_server.add_proxy_rule(prefix, host, port)
#            elif rule == "plugin":
#                plugin_name = params[0]
#                cb = self.app.plugin_manager.get_http_cb(
            elif rule == "wsgi":                
                # TODO: load app
                app = None
                http_server.add_wsgi_rule(prefix, app)
                
