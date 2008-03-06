from orbited import __version__
from orbited.config import map as config
from orbited.http import HTTPRequest
from orbited.json import json
import event
num_retry_limit = int(config['[transport]']['num_retry_limit'])
timeout = int(config['[transport]']['timeout'])

# Therapy Wellness
# 323 255 5409
# 2460 Colorado

transports = { }

def setup():
    transports['basic'] = BasicTransport
    transports['raw'] = RawTransport

class TransportHandler(object):
    
    def __init__(self, dispatcher):
        self.connections = {}
        self.dispatcher=dispatcher
        
    def contains(self, key):
        return key in self.connections
        
    def http_request(self, conn):
        # TODO: use cookies to get info out            
        req = HTTPRequest(conn)
        transport_name = req.form.get('transport', None)
        if transport_name is None:
            return req.error("Transport name not specified")
        if transport_name not in transports:
            return req.error("Invalid Transport Name: %s" % transport_name)
        identifier = req.form.get('identifier', None)
        if identifier is None:
            return req.error("Identifier not specified.")
        key = identifier, req.url
        if key not in self.connections:
            self.connections[key] = TransportConnection(key, self.__timed_out)
        self.connections[key].http_request(req)
        print "Accepted:", key
        
    def dispatch(self, msg):
        self.connections[msg.recipient].send_events([msg])
        
    def __timed_out(self, conn):
        print 'transport connection timed out', conn.key
        del self.connections[conn.key]
        conn.close()
        
class TransportConnection(object):
  
    def __init__(self, key, timed_out_cb):
        self.transport = None
        self.event_callback = None
        self.events = []
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
        print 'closing...'        
        self.end_transport()
        self.__stop_timer()
        
    def __transport_close_cb(self, transport):
        if transport == self.transport:
            self.end_transport()
        
        
    def end_transport(self):
        if self.transport:
            self.transport.end()
            self.transport = None
            self.event_callback = None
            self.__start_timer()
        
    def http_request(self, request):
        print 'TransportConnection.http_request', request
        transport_name = request.form['transport']
        if self.transport is not None and transport_name != self.transport.name:
            self.end_transport()
        self.transport = transports[transport_name](self.set_event_cb, self.__transport_close_cb)
        self.transport.http_request(request)
        self.__stop_timer()
            
    def send_events(self, events):
        self.events.extend(events)
        self.check_events()
    
    def check_events(self):
        if not self.event_callback:
            return
        reschedule = self.event_callback(self.events)
        if reschedule != True:
            self.event_callback = None
    
    def set_event_cb(self, cb):
        self.event_callback = cb
        if self.events:
            self.check_events()


class Transport(object):
      
    def __init__(self, ready_cb, close_cb):
        self.ready_cb = ready_cb
        self.close_cb = close_cb
    
    def http_request(self, req):
        """ new http request has been made for this transport.
        """
        raise Exception("NotImplemented"), "http_request has not been implemented"
        
    def send_events(self, events):
        """ dispatch a list of events to the client.
            all events must be removed from the given list if the callback
            should be rescheduled.
            return True to reschedule the send callback, otherwise return anything else.
        """                    
        raise Exception("NotImplemented"), "send_events has not been implemented"
                        
                        
class RawTransport(Transport):
    name = 'raw'
    def __init__(self, ready_cb, close_cb):
        self.ready_cb = ready_cb
        self.close_cb = close_cb
        self.browser_conn = None
        

    def __ready(self):
        print 'RawTransport.__ready'
        if self.browser_conn:
            self.ready_cb(self.__send_messages)

    def __send_messages(self, messages):
        print 'RawTransport.__send_messages'
        message = messages.pop(0)
        self.browser_conn.write(self.encode(message.payload), self.__msg_success_cb, [message], self.__msg_failure_cb, [message])
        return False
    
    def end(self):
        if self.browser_conn:
            self.browser_conn.close_now()
            
    def encode(self, payload):
        return payload
    
    def __msg_success_cb(self, message):
        message.success()
        self.__ready()
    def __msg_failure_cb(self, message):
        message.failure()
        self.__ready()

    def __conn_closed_cb(self, browser_conn):
        if browser_conn == self.browser_conn:
            self.browser_conn = None
            self.close_cb(self)

    def http_request(self, req):
        print 'RawTransport.http_request,', req
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
        self.browser_conn.write_status('200', 'OK')
        self.browser_conn.write_header('Server', 'Orbited %s' % __version__)
        self.browser_conn.write_headers_end()


class BasicTransport(RawTransport):
    
    def initial_response(self):
        self.browser_conn.write_status('200', 'OK')
        self.browser_conn.write_header('Server', 'Orbited %s' % __version__)
        self.browser_conn.write_header('Content-type', 'text/html')
        self.browser_conn.write_header('Content-length', '1000000000')        
        self.browser_conn.write_headers_end()
    
    def encode(self, payload):
        return payload + "<br>"


setup()