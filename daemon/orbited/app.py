import traceback
import sys
try:
    import cStringIO as StringIO
except:
    import StringIO
    
from dez.http.application import HTTPApplication
from orbited.config import map as config
from orbited.transport import TransportConnection, TransportHandler
from orbited.dispatcher import Dispatcher
from orbited.plugin import PluginManager
from orbited.csp import CSP
from orbited.revolved import Revolved
from orbited.system import System

import random

httpconf = config['[http]']
class Application(object):
  
    def __init__(self):
        self.http_server = HTTPApplication(httpconf['bind_addr'], int(httpconf['port']))
        self.plugin_manager = PluginManager()
        self.transports = TransportHandler()
        self.csp = CSP()
        self.revolved = Revolved()
        self.system = System()
#        self.stomp_daemon = StompDaemon()
#        self.orbit_daemon = OrbitDaemon()
        self.dispatcher = Dispatcher(self)

#        self.http_router = HTTPRouter(
#            self.http_server, 
#            self.dispatcher, 
#            self.plugin_manager,
#            self.stomp_daemon,
#            self.orbit_daemon,
#        )
        
        self.connections = {}
        self.csp_connections = {}
        self.revolved_connections = {}
        
#        self.http_daemon = HTTPDaemon(httpconf['bind_addr'], int(httpconf['port']))
                    

    def start(self):
        """ Start the daemons """
        import event        
        event.signal(2, event.abort)
        last_exception = None
        while True:
            try:
                event.dispatch()
            except Exception, e:
                # TODO: without this ctr+c doesn't get us out after at least one
                #       exception has previously been raised.                
                if last_exception is e :
                    sys.exc_clear()
                    break
                last_exception = e
                exception, instance, tb = traceback.sys.exc_info()
                if 'exceptions must be strings' in str(instance):
                    print "Error in pyevent 0.3. See http://orbited.org/pyevent.html for details"
                    event.abort()
                    sys.exit(0)
                # TODO: Start: There is certainly a better way of doing this
                x = StringIO.StringIO()
                traceback.print_tb(tb, file=x)
                x = x.getvalue()
                relevant_line = x.split('\n')[-3]
                # End: Find a better way

#                logger.critical('%s:%s\t%s' % (exception, instance, relevant_line))
                print x
#                sys.stdout.flush()
            else:
                break
        print "Received Ctr+c shutdown"
            