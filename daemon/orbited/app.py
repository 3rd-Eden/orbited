import traceback
import sys
try:
    import cStringIO as StringIO
except:
    import StringIO
    
from dez.http.application import HTTPApplication
from orbited import __version__
from orbited.op.daemon import OPDaemon
from orbited.plugin import PluginManager
from orbited.transport import TransportConnection, TransportHandler
from orbited.cometwire import CometWire
from orbited.upstream import UpstreamHandler
from orbited.csp import CSP
from orbited.revolved.revolved import RevolvedHandler
from orbited.system import System
from orbited.develop import Development
from orbited.dispatcher import Dispatcher
from orbited.logger import get_logger
log = get_logger("app")

import random

class Application(object):
  
    def __init__(self, config):
        httpconf = config['[http]']
        orbitconf = config['[op]']
        self.dispatcher = Dispatcher(self)
        self.http_server = HTTPApplication(
            httpconf['bind_addr'], 
            int(httpconf['port']), 
            server_name="Orbited %s" % __version__)
        self.orbit_daemon = OPDaemon(orbitconf['bind_addr'], int(orbitconf['port']), self.dispatcher)
        self.plugin_manager = PluginManager(self.dispatcher)
        self.transports = TransportHandler(self.dispatcher)
        self.cometwire = CometWire(self.dispatcher)
        self.upstream = UpstreamHandler(self.dispatcher)
        self.csp = CSP(self.dispatcher)
        self.revolved = RevolvedHandler(self)
#            self.csp,
#            SimpleRevolvedBackend(s
#            RevolvedOpenAuthBackend(),
            
#            self.dispatcher)
        self.system = System()
        self.develop = Development(self)
        self.dispatcher.setup()
        

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
                    log.error("Error in pyevent 0.3. See http://orbited.org/pyevent.html for details")
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
        print "Received Ctrl-C; shutting down."
            
