import log
import event
    
transports = {}

def create(conn, app):
    try:
        return transports[conn.request.transport_name](conn.key(), app)
    except KeyError:
        raise "InvalidTransport"

def load_transports():
    transports.update({
        'iframe': IFrameTransport,
        'iframe_raw': IFrameRawTransport,
        'iframe_domain': IFrameDomainTransport,
        'iframe_alert': IFrameAlertTransport,
        'xhr': XHRTransport,
        'xhr_buffered': XHRBufferedTransport
        
    })

def extract_user(req):
    if '|' in req.headers['url']:
        return req.headers['url'].split('|')        
    elif '!' in req.headers['url']:
        return req.headers['url'].split('!')

class Transport(object):
    def close(self):
        pass
    
    def respond(self, request):
        pass
    
    def accept_http_connection(self, conn):        
        pass
    
    def response_success(self, request, conn):
        pass
    
    def response_failure(self, request, conn):
        pass
    

class IFrameRawTransport(Transport):
    name = 'iframe_raw'
    initial_data =  "HTTP/1.1 200 OK\r\n"
    initial_data += "Content-Type: text/html\r\n"
    initial_data += "Content-Length: 100000\r\n\r\n"
    initial_data += """<!-- This is a filler element. Its only purpose is to 
    cause IE6 to start rendering incrementally. For some Reason IE6 and safri don't
    render until it receives a certain amount of data. This should be large enough 
    TODO: Check the headers before sending all this. No reason to send it
          to firefox and other, good browsers.
    -->
    <span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span>
    """
    
    def __init__(self, key, app):
        self.key = key
        self.app = app
        self.http_conn = None
        self.active = True
    
    def close(self):
        self.http_conn.close()
        self.active = False
    
    def accept_http_connection(self, conn):
        if self.http_conn is not None:
            old_conn = self.http_conn
            self.http_conn = conn
            old_conn.close()   
        else:
            self.http_conn = conn
        self.http_conn.respond(ResponseBuffer(self.initial_data, self))
    
    def respond(self, request):
        self.http_conn.respond(ResponseBuffer(request.body, self, request))
    
    def response_success(self, request, conn):
        log_recipient = "%s [ %s ]" % (str(conn.key())[1:-1], conn.addr[0])
        log.log("EVENT", "%s/%s -> %s" % (conn.addr[0], request.id, log_recipient))
        request.success(conn.key())
    
    def response_failure(self, request, conn):
        log_recipient = "%s [ %s ]" % (str(conn.key())[1:-1], conn.addr[0])
        request.error(conn.key())
    
    def expire_http_connection(self, conn):
        if conn == self.http_conn and self.active:
            del self.app.connections[self.key]            
    

class IFrameTransport(IFrameRawTransport):
    name = 'iframe'
    event_wrapper = "<script>window.parent.event(%s);</script>\n"
    
    def respond(self, request):
        # Encode in json and put in a window.parent.event function call.
        self.http_conn.respond(ResponseBuffer(self.event_wrapper % request.body, self, request))
    

class IFrameAlertTransport(IFrameTransport):
    name = 'iframe_alert'
    event_wrapper = "<script>alert('iframe_alert' + %s);</script>\n"

            
class IFrameDomainTransport(IFrameTransport):
    name = 'iframe_domain'    
    
    def _initial_data(self):
        document_domain = self.get_domain(self.http_conn.request.headers['host'])
        return IFrameTransport.initial_data + '\n<script>document.domain="%s"</script>\n' % document_domain
    
    initial_data = property(_initial_data)
    
    def get_domain(self, host):
        host = host.split(':')[0]
        subs = host.split('.')
        if len(subs) == 4:
            for sub in subs:
                try:
                    int(sub)
                except:
                    return '.'.join(subs[-2:])
            return host
        return '.'.join(subs[-2:])
    

class XHRTransport(Transport):
    name = 'xhr'
    timeout_delay = 30
    
    def __init__(self, key, app):
        self.key = key
        self.connections = []
        self.app = app
    
    def close(self):
        for conn in self.connections:
            conn.close()
    
    def accept_http_connection(self, conn):
        
        timer = event.timeout(self.timeout_delay, self.timed_out, conn)
        conn.timer = timer
        self.connections.append(conn)
    
    def expire_http_connection(self, conn):
        if conn in self.connections:
            self.connections.remove(conn)
            conn.timer.delete()
            self.cleanup()
    
    def timed_out(self, conn):
        print "TIME OUT: %s" % conn
        self.connections.remove(conn)
        conn.respond(ResponseBuffer("", self, XHRTimeoutRequest()))
    
    def respond(self, request):
        conn = self.connections.pop(0)
        conn.respond(ResponseBuffer(request.body, self, request))
        conn.timer.delete()
    
    def timeout_response_complete(self, conn):
        conn.close()
    
    def response_success(self, request, conn):
        if isinstance(request, XHRTimeoutRequest):
            return self.timeout_response_complete(conn)
        log_recipient = "%s [ %s ]" % (str(conn.key())[1:-1], conn.addr[0])
        log.log("EVENT", "%s/%s -> %s" % (conn.addr[0], request.id, log_recipient))
        request.success(conn.key())
        conn.close()
        self.cleanup()
    
    def response_failure(self, request, conn):
        if isinstance(request, XHRTimeoutRequest):
            return self.timeout_response_complete(conn)
        log_recipient = "%s [ %s ]" % (str(conn.key())[1:-1], conn.addr[0])
        request.error(conn.key())
        conn.close()
        self.cleanup()
    
    def cleanup(self):
        if not self.connections:
            del self.app.connections[self.key]
    

class XHRBufferedTransport(XHRTransport):
    name = 'xhr_buffered'
    timeout = 10
    def __init__(self, key, app):
        XHRTransport.__init__(self, key, app)
        self.pending = []
        self.timer = None
        self.key = None
    
    def accept_http_connection(self, conn):
        if not self.key:
            self.key = conn.key()
        XHRTransport.accept_http_connection(self, conn)
        if self.pending:
            self.respond(self.pending.pop(0))
    
    def respond(self, request):
        if not self.connections:
            self.pending.append(request)
        elif self.connections:
            conn = self.connections.pop(0)
            conn.respond(ResponseBuffer(request.body, self, request))
            conn.timer.delete()
        if not self.connections:
            self.start_timer()
        else:
            self.stop_timer()
    
    def stop_timer(self):
        if self.timer:
            self.timer.delete()
            self.timer = None
    
    def start_timer(self):
        if not self.timer:
            self.timer = event.timeout(self.timeout, self.full_timeout)
    
    def full_timeout(self):
        self.cleanup()
    
    def response_failure(self, request, conn):
        if conn is None:
            print "SELF.KEY IS", self.key
            request.error(self.key)
            return
        if isinstance(request, XHRTimeoutRequest):
            return self.timeout_response_complete(conn)
        log_recipient = "%s [ %s ]" % (str(conn.key())[1:-1], conn.addr[0])
        request.error(conn.key())
        conn.close()
        # self.cleanup()
    
    def response_success(self, request, conn):
        if isinstance(request, XHRTimeoutRequest):
            return self.timeout_response_complete(conn)
        log_recipient = "%s [ %s ]" % (str(conn.key())[1:-1], conn.addr[0])
        log.log("EVENT", "%s/%s -> %s" % (conn.addr[0], request.id, log_recipient))
        request.success(conn.key())
        conn.close()
    
    def cleanup(self):
        for request in self.pending:
            self.response_failure(request, None)
        XHRTransport.cleanup(self)
    

class XHRTimeoutRequest(object):
    pass

class ResponseBuffer(object):
    
    def __init__(self, data, transport, request=None):
        self.request = request
        self.data = data
        self.transport = transport
    
    def success(self, conn):
        if self.request:
            self.transport.response_success(self.request, conn)
    
    def failure(self, conn):
        if self.request:
            self.transport.response_failure(self.request, conn)
    
