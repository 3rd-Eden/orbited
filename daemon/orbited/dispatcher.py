from orbited.system import System
from orbited.config import map as config
from orbited.logger import get_logger

log = get_logger("dispatcher")

class Dispatcher(object):
  
    def __init__(self, app):
        self.app = app

    def dispatch_orbit(self, message):
        log.debug("Dispatch:", message)

        for recipient in message.recipients:
            if self.app.csp.contains(recipient):
                self.app.csp.dispatch(message.single_recipient_message(recipient))
            elif self.app.transports.contains(recipient):
                self.app.transports.dispatch(message.single_recipient_message(recipient))
            else:
                message.failure(recipient, "not connected")
                
    def setup(self):
        for prefix, (rule, params) in config['[routing]'].items():
            print prefix, '->', rule
            if rule == "transport":
                self.add_transport_rule(prefix)
#                self.app.http_server.add_cb_rule(prefix, self.app.transports.http_request)
            elif rule == "system":
                self.add_cb_rule(prefix, self.app.system.http_request)
            elif rule == "static":
                local_source = params[0]
                self.app.http_server.add_static_rule(prefix, local_source)
            elif rule == "proxy":
                host, port = params
                self.app.http_server.add_proxy_rule(prefix, host, port)
            elif rule == "wsgi":                
                # TODO: load app
                app = None
                self.app.http_server.add_wsgi_rule(prefix, app)
            elif rule == "pylons":
                try:
                    from paste.deploy import loadapp
                except ImportError:
                    message = "could not import loadapp from paste.deploy.\n"
                    message += "You must install PasteDeploy before you can"
                    message += " load a Pylons application.\n"
                    raise ImportError(message)
                
                app_config_file = params[0]
                app = loadapp(app_config_file, relative_to=".")
                self.app.http_server.add_wsgi_rule(prefix, app)

    def add_transport_rule(self, prefix):
        self.app.http_server.add_cb_rule(prefix, self.app.transports.http_request)
        
    def add_cb_rule(self, prefix, cb):
        self.app.http_server.add_cb_rule(prefix, cb)
        