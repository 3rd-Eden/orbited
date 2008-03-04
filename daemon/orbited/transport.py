from orbited import __version__
from orbited.config import map as config
from orbited.http import HTTPRequest
import event
num_retry_limit = int(config['[transport]']['num_retry_limit'])
timeout = int(config['[transport]']['timeout'])

# Therapy Wellness
# 323 255 5409
# 2460 Colorado

transports = { }

def setup():
    transports['basic'] = BasicTransport

class TransportHandler(object):
    
    def __init__(self):
        self.connections = {}
        
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
        
        
    def __timed_out(self, conn):
        del self.connections[conn.key]
        conn.close()
        
class TransportConnection(object):
  
    def __init__(self, key, timed_out_cb):
        self.transport = None
        self.event_callback = None
        self.events = []
        self.key = key
        self.__timed_out_cb = timed_out_cb
        self.timer = event.timeout(timeout, self.__timed_out_cb)
        
    def close(self):
        self.end_transport()
        if self.timer.pending():
            self.timer.delete()
        
    def end_transport(self):
        self.transport.end()
        self.transport = None
        self.event_callback = None
        if not self.timer.pending():
            self.timer.add()
        
    def http_request(self, request):
        transport_name = request.form['transport']
        if self.transport is not None and transport_name != self.transport.name:
            self.end_transport()
        self.transport = transports[transport_name](self.set_event_cb)
        self.transport.http_request(request)
        if self.timer.pending():
            self.timer.delete()
    def send_events(self, events):
        self.events.extend(event)
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
      
    def __init__(self, get_events):
        self.get_events = get_events
    
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
  
    def __init__(self, get_events):
        Transport.__init__(self, get_events)
        self.browser_conn = None

    def send_events(self, events):
        events_copy = []
        while events:
            events_copy.append(events.pop(0))
        payload = json.encode([event.payload for event in events_copy])
    
    def send_event(self, event):
        self.browser_conn.write(payload, self.event_success, [ events_copy ])

    def event_success(self, event):
        pass

#    def event_
    
#        return True

    def http_request(self, req):

        self.browser_conn = RawHTTPResponse(req)
        self.browser_conn.write_status('200', 'OK')
        self.browser_conn.write_header('Server', 'Orbited __version__')
        self.browser_conn.end_headers()



class RawTransport(object):

    pass  

class BasicTransport(Transport):
    pass

setup()