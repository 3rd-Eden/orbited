import random
from orbited import __version__
from orbited.config import map as config
from orbited.http import HTTPRequest
from orbited.json import json
from orbited.logger import get_logger
from orbited.op.message import SingleRecipientMessage
import event

log = get_logger("transport")

num_retry_limit = int(config['[transport]']['num_retry_limit'])
timeout = int(config['[transport]']['timeout'])

transports = {}

def setup_registered_transports():
    transports['basic'] = BasicTransport
    transports['raw'] = DownstreamTransport
    transports['iframe'] = IFrameTransport
    transports['leaky_iframe'] = LeakyIFrameTransport
    transports['xhr_multipart'] = XHRMultipartTransport
    transports['xhr_stream'] = XHRStreamTransport
    transports['sse'] = ServerSentEventsTransport

class TransportHandler(object):
    
    def __init__(self, dispatcher):
        self.connections = {}
        self.dispatcher = dispatcher
        self.orbit_daemon = self.dispatcher.app.orbit_daemon
        self.url_callbacks = {} # Callbacks for assigning connection identifiers
        
    def contains(self, key):
        return key in self.connections
    
    def get(self, key):
        print self.connections
        return self.connections[key]
        
    def set_identifier_callback(self, url, cb, args=[]):
        """Set a callback for when a connection is made and no identifier
        is specified. The callback should return a tuple of
        (identifier, [initial_msgs]) which will be used to initialize
        the connection."""
        self.url_callbacks[url] = (cb, args)
        
    def http_request(self, conn):
        # TODO: use cookies to get info out            
        req = HTTPRequest(conn)
        transport_name = req.form.get('transport', None)
        if transport_name is None:
            return req.error("Transport name not specified")
        if transport_name not in transports:
            return req.error("Invalid Transport Name: %s" % transport_name)
        
        identifier = req.form.get('identifier', None)
        # If no identifier is specified, see if the
        # url callback can provide an identifier.
        initial_msgs = None
        if identifier is None:
            if req.url in self.url_callbacks:
                cb, args = self.url_callbacks[req.url]
                identifier, initial_msgs = cb(*args)
            else:
                return req.error("Identifier not specified.")
            
        key = identifier
        if key not in self.connections:
            # OP SIGNON
            self.orbit_daemon.signon_cb(key)
            self.connections[key] = TransportConnection(key, self.__timed_out)
        self.connections[key].http_request(req)
        
        log.debug("Accepted: %s" % (key,))
        # Send initial messages
        if initial_msgs:
            self.connections[key].send_msgs(initial_msgs)
        
    def dispatch(self, msg):
        self.connections[msg.recipient].send_msgs([msg])
        
    def __timed_out(self, conn):
        log.debug('transport connection timed out', conn.key)
        # OP SIGNOFF
        # Todo: add missed messages
        self.orbit_daemon.signoff_cb(conn.key)
        del self.connections[conn.key]
        conn.close()
        
class TransportConnection(object):
  
    def __init__(self, key, timed_out_cb):
        self.transport = None
        self.msg_ready_callback = None
        self.msgs = []
        self.key = key
        self.__timed_out_cb = timed_out_cb
        self.__start_timer()
        
    def __start_timer(self):
        self.timer = event.timeout(timeout, self.__timed_out_cb, self)
                
    def __stop_timer(self):
        if self.timer:
            self.timer.delete()
            self.timer = None
                
    def close(self):
        """Close this transport and stop the timeout timer."""
        self.end_transport()
        self.__stop_timer()
        
    def __transport_close_cb(self, transport):
        if transport == self.transport:
            self.end_transport()
        
    def end_transport(self):
        """Close the network connection for this transport."""
        if self.transport:
            self.transport.end()
            self.transport = None
            self.msg_ready_callback = None
            self.__start_timer()
        
    def http_request(self, request):
        print 'TransportConnection.http_request', request
        transport_name = request.form['transport']
        if self.transport is not None and transport_name != self.transport.name:
            self.end_transport()
        self.transport = transports[transport_name](self.set_msg_ready_cb, self.__transport_close_cb)
        self.transport.http_request(request)
        self.__stop_timer()
            
    def send(self, data):
        msg = SingleRecipientMessage(data, self.key)
        self.send_msgs([msg])
            
    def send_msgs(self, msgs):
        self.msgs.extend(msgs)
        self.check_msgs()
    
    def check_msgs(self):
        if not self.msg_ready_callback:
            return
        reschedule = self.msg_ready_callback(self.msgs)
        if reschedule != True:
            self.msg_ready_callback = None
    
    def set_msg_ready_cb(self, cb):
        """Callback when the transport is ready to send messages."""
        self.msg_ready_callback = cb
        if self.msgs:
            self.check_msgs()
                        
def mcb(msg):
    def aha(*args, **kw):
        print 'msg:', args, kw
    return aha                        
                        
class DownstreamTransport(object):
    name = 'raw'
    
    def __init__(self, ready_cb, close_cb):
        self.ready_cb = ready_cb
        self.close_cb = close_cb
        self.browser_conn = None
        
    def __ready(self):
        print 'DownstreamTransport.__ready'
        if self.browser_conn:
            self.ready_cb(self.__send_messages)

    def __send_messages(self, messages):
        print 'DownstreamTransport.__send_messages'
        message = messages.pop(0)
        return self.send_message(message)
        
    def send_message(self, message):
        self.browser_conn.write(self.encode(message.payload), self.__msg_success_cb, [message], self.__msg_failure_cb, [message])
        return False
    
    def end(self):
        if self.browser_conn:
            self.browser_conn.close(mcb('close...'))
            
    def encode(self, payload):
        return payload
    
    def __msg_success_cb(self, message):
        print 'success!', message
        message.success()
        self.__ready()
        
    def __msg_failure_cb(self, message):
        print 'failure!', message, message.payload, message.recipient
        message.failure()
        self.__ready()

    def __conn_closed_cb(self, browser_conn):
        if browser_conn == self.browser_conn:
            self.browser_conn = None
            self.close_cb(self)

    def http_request(self, req):
        print 'DownstreamTransport.http_request,', req
        set_ready = False
        if self.browser_conn:
            self.browser_conn.close()
        else:
            set_ready = True
        self.browser_conn = req.RawHTTPResponse()
        req.set_close_cb(self.__conn_closed_cb, [self.browser_conn])
        self.initial_response()
        if set_ready:
            self.__ready()
        
    def initial_response(self):
        self.browser_conn.write_status('200', 'OK', mcb('write_status'))
        self.browser_conn.write_header('Server', 'Orbited %s' % __version__, mcb('write_server'))
        self.browser_conn.write_headers_end(mcb('headers_end'))


class BasicTransport(DownstreamTransport):
    name = 'basic'
    
    def initial_response(self):
        self.browser_conn.write_status('200', 'OK')
        self.browser_conn.write_header('Server', 'Orbited/%s' % __version__)
        self.browser_conn.write_header('Content-type', 'text/html')
        self.browser_conn.write_header('Content-length', '1000000000')        
        self.browser_conn.write_headers_end()
    
    def encode(self, payload):
        return payload + "<br>"
        
    def ping_render(self):
        return '<i>Ping!</i><br>\r\n'
        
class IFrameTransport(DownstreamTransport):
    name = 'iframe'
    
    def initial_response(self):
        js = self.browser_conn.request.form.get('js', 'iframe.js')
        self.browser_conn.write_status('200', 'OK')
        self.browser_conn.write_header('Server', 'Orbited/%s' % __version__)
        self.browser_conn.write_header('Content-Type', 'text/html')
        self.browser_conn.write_header('Content-Length', '10000000')    
        self.browser_conn.write_header('Cache-Control', 'no-cache')        
        self.browser_conn.write_headers_end()
        self.browser_conn.write(
            '<html>'
            ' <head>'
            '  <script src="/_/static/transports/%s" charset="utf-8"></script>' % (js,)
            + ' </head>'
            ' <body onload="reload();">'
            + '<span></span>' * 100
            + '\n'
        )
    
    def encode(self, payload):
        return '<script>e(%s);</script>\n' % (json.encode(payload),)
    
    def ping_render(self):
        return '<script>p();</script>\n'

class LeakyIFrameTransport(IFrameTransport):
    def __init__(self, *args, **kwargs):
        self.first = True
        IFrameTransport.__init__(self, *args, **kwargs)
        
    name = 'leaky_iframe'
    def send_message(self, message):
        print 'ahem'
        if self.first:
            self.first = False
        elif random.random() > 0.4:
            print "Leaky IFrame, dropping: ", message.payload
            return True
        return IFrameTransport.send_message(self, message)
    

class ServerSentEventsTransport(DownstreamTransport):
    name = 'sse'
    
    def initial_response(self):
        self.browser_conn.write_status('200', 'OK')
        self.browser_conn.write_header('Server', 'Orbited/%s' % __version__)
        self.browser_conn.write_header('Content-Type', 'application/x-dom-event-stream')      
        self.browser_conn.write_headers_end()
    
    def encode(self, payload):
        return (
            'Event: orbited\n' +
            '\n'.join(['data: %s' % line for line in payload.splitlines()]) +
            '\n\n'
        )
    
    def ping_render(self):
        return (
            'Event: ping\n' +
            'data: ' +
            '\n\n'
        )
    

class XHRMultipartTransport(DownstreamTransport):
    BOUNDARY = "orbited--"
    name = 'xhr_multipart'
    
    def initial_response(self):
        self.browser_conn.write_status('200', 'OK')
        self.browser_conn.write_header('Server', 'Orbited/%s' % __version__)
        self.browser_conn.write_header('Content-Type', 
                'multipart/x-mixed-replace;boundary="%s"' % (self.BOUNDARY,))      
        self.browser_conn.write_headers_end()
    
    def encode(self, payload):
        boundary = "\r\n--%s\r\n" % self.BOUNDARY
        headers = "\r\n".join([
            'Content-Type: application/json',
            'Content-Length: %s' % (len(payload),),
        ])
        return ''.join([headers, payload, boundary])
    
    def ping_render(self):
        return self.encode("")

class XHRStreamTransport(DownstreamTransport):
    BOUNDARY = "\r\n|O|\r\n"
    name = 'xhr_stream'
    
    def initial_response(self):
        self.browser_conn.write_status('200', 'OK')
        self.browser_conn.write_header('Server', 'Orbited/%s' % __version__)
        self.browser_conn.write_header('Content-Type', 
                                    'application/x-orbited-event-stream')     
        self.browser_conn.write_headers_end()
        self.browser_conn.write("."*256 + '\r\n\r\n')
    
    def encode(self, payload):
        return self.BOUNDARY + payload + self.BOUNDARY
    
    def ping_render(self):
        return self.BOUNDARY + "ping" + self.BOUNDARY

setup_registered_transports()