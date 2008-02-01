from orbited.http.server import HTTPDaemon
#from orbited.stomp.server import StompDaemon
#from orbited.op.server import OPDaemon
from orbited.config import map as config
from transport import TransportConnection
import random
httpconf = config['[http]']
class Application(object):
  
    def __init__(self):
        self.http_daemon = HTTPDaemon(httpconf['bind_addr'], int(httpconf['port']))
#        self.stomp_daemon = StompDaemon()
#        self.orbit_daemon = OrbitDaemon()
        self.connections = {}
        self.csp_connections = {}
        self.revolved_connections = {}
        
        
        
    def send(self, event):
        if event.key not in self.connections:
            event.failed("Destination not found")
        self.connections[event.key].send(event)
            
    def accept_http_connection(self, conn):
        if conn.key not in self.connections:
            self.connections[conn.key] = TransportConnection()
            if conn.url == "/_/session":
                sessions.accept_transport_connection(self.connections[conn.key])
        self.connections[conn.key].accept_http_connection(conn)

    def http_connection_closed(self, conn):
        if conn.key in self.connections:
            self.connections[conn.key].http_conn_closed(conn)

    def transport_connection_closed(self, tconn):
        if tconn.url == "/_/session":
            sessions.close_transport_connection(tconn)
        del self.connections[tconn.key]


    def unique_key(self):
        k = None
        while k is None or k in self.connections:
            k = "".join([random.choice("ABCDEF123456790") for i in range(10) ])
        return k

    def start(self):
        print 'starting...'

    def main(self):
        """ Start the daemons """
        def collect_toplevel_exceptions():
            return True
        import event
        event.timeout(1, collect_toplevel_exceptions)
        while True:
            try:
                event.dispatch()
            except KeyboardInterrupt, k:
                event.abort()
                print 'Received Ctr+c shutdown'
                sys.stdout.flush()
                sys.exit(0)

            except Exception, e:
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

                logger.critical('%s:%s\t%s' % (exception, instance, relevant_line))
                print x

