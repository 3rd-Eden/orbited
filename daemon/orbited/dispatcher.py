from orbited.system import System
from orbited.config import map as config
from paste.deploy import loadapp

class Dispatcher(object):
  
    def __init__(self, app):
        self.app = app
#        self.app.orbit_daemon.set_send_cb(self.dispatch_orbit)
#        self.app.
        
#    /_/plugin/

    def dispatch_orbit(self, message):
        print 'dispatch orbit:', message
#        return
        for recipient in message.recipients:
            if self.app.csp.contains(recipient):
                self.app.csp.dispatch(message.single_recipient_message(recipient))
            elif self.app.transports.contains(recipient):
                self.app.transports.dispatch(message.single_recipient_message(recipient))
            else:
                message.failure(recipient, "not connected")
    
    def transport_http_request(self, req):
        self.app.transports.http_request(req)
        
    def revolved_http_request(self, req):
        self.app.revolved.http_request(req)
        
    def csp_http_request(self, req):
        self.app.csp.http_request(req)
                
    def setup(self):
        for prefix, (rule, params) in config['[routing]'].items():
            if rule == "transport":
                print prefix, '-> transport'
                self.app.http_server.add_cb_rule(prefix, self.transport_http_request)
            elif rule == "csp":
                self.app.http_server.add_cb_rule(prefix, self.app.csp.http_request)
                print prefix, '-> csp'
            elif rule == "revolved":
                self.app.http_server.add_cb_rule(prefix, self.revolved_http_request)
                print prefix, '-> revolved'
       
            elif rule == "system":
                self.app.http_server.add_cb_rule(prefix, self.app.system.http_request)
                print prefix, '-> system'

            elif rule == "static":
                local_source = params[0]
                self.app.http_server.add_static_rule(prefix, local_source)
                print prefix, '-> static'
            elif rule == "proxy":
                host, port = params
                self.app.http_server.add_proxy_rule(prefix, host, port)
                print prefix, '-> proxy'
#            elif rule == "plugin":
#                plugin_name = params[0]
#                cb = self.app.plugin_manager.get_http_cb(
            elif rule == "wsgi":                
                # TODO: load app
                app = None
                self.app.http_server.add_wsgi_rule(prefix, app)
                
            elif rule == "pylons":                
                app_config_file = params[0]
                app = loadapp(app_config_file,
                              relative_to=".")
                self.app.http_server.add_wsgi_rule(prefix, app)
                print prefix, '-> pylons'

