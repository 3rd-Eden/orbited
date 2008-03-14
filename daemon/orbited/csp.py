#from orbited.router import router, CSPDestination
from orbited.http import HTTPRequest


import random
import event
from orbited.dynamic import DynamicHTTPResponse
from orbited.json import json
from orbited.orbit import InternalOPRequest
#from orbited.config import map as config
from orbited.transport import transports as supported_transports

#router.register(CSPDestination, '/_/csp')
#router.register(StaticDestination, '/_/csp/static', '[orbited-static]')


class CSP(object):
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
"""        self.sessions = {}
        self.identifiers = {}
        self.connection_timers = {}
        self.registered = {}
        self.time_count = 0
        event.timeout(1, self.tick)
    
    def message(self, recipient, msg):
        if not options['enabled']:
            raise Exception("CSPNotEnabled")
        if recipient not in self.identifiers:
            raise Exception("RecipientNotFound")
        self.sessions[
"""    
    def http_request(self, request):
        request = HTTPRequest(request)
        junk, method = request.url.rsplit('/', 1)
        if not hasattr(self, method):
            return request.error("Invalid Method")
        response = request.HTTPResponse()
        return getattr(self, method)(request, response)
    
    def contains(self, key):
        return False


    def signon(self, request, response):
        response.write("CSP Hello World")
        response.dispatch()


"""
import random
import event
from orbited.dynamic import DynamicHTTPResponse
from orbited.json import json
from orbited.orbit import InternalOPRequest
from orbited.config import map as config
from orbited.transport import map as supported_transports
options = config['[csp]']
EVENT_PATH = options['event_path']


# TODO: implement pushing PINGs. They are never sent.
# TODO: implement receiving pongs
# TODO: implement receiving pings
# TODO: implement pushing pongs
class CSP(object):
    connect_timeout = int(options['connect.timeout'])
    
    def __init__(self):
        options['enabled'] = int(options['enabled'])
        if not options['enabled']:
            return
        self.sessions = {}
        self.identifiers = {}
        self.connection_timers = {}
        self.registered = {}
        self.time_count = 0
        event.timeout(1, self.tick)
        
      
    def event(self, recipient, request):
        if not options['enabled']:
            return
        if recipient not in self.identifiers:
            return False
        self.sessions[self.identifiers[recipient]].event(self.time_count, request)
        return True
    
    
    def register_location(self, location, connect, disconnect):
        if location in self.registered:
            raise Exception("AlreadyRegistered")
        self.registered[location] = (connect, disconnect)
        
    def tick(self):
        self.time_count += 1
        for id in self.sessions:
            self.sessions[id].timeout(self.time_count)
        return True
        
    def dispatch(self, request):
        response = DynamicHTTPResponse(request)
        fname = request.url[len('/_/csp/'):]
        f = getattr(self, 'dynamic_%s' % (fname,), None)
        if f is None:
            response.write('Invalid function')
            return response.render()
        d = f(request, response)
        if d != False:
            response.render()
        
    def dynamic_connect(self, request, response):
        transports = request.form.get('transports', None)
        if not transports:
            return self.error_params(response, ['transports'])
        # TODO: sanitize transports string first
        transports = transports.split(',')
        # TODO: put good transport choosing here
        chosen_transport = None
        for transport in transports:
            if transport in supported_transports:
                chosen_transport = transport
                break
        if not chosen_transport:
            return response.write(json.encode(["ERR", [ "No supported transports matched"]]))
        id = "".join([random.choice("1234567890ABCDEFG") for i in range(6) ])
        while id in self.sessions:
            id = "".join([random.choice("1234567890ABCDEFG") for i in range(6) ])
        id = 't' # for testing
        self.sessions[id] = Session(self, id, self.time_count)
        # TODO: add timer. maybe the session will do that.
        #self.connection_timers[id] = event.timeout(self.connect_timeout
        return response.write(json.encode(['OK', [id, chosen_transport]]))
    
    def dynamic_identify(self, request, response):
        id = request.form.get('id', None)
        if id not in self.sessions:
            return self.error_id(response)        
        identifier = request.form.get('identifier', None)
        location = request.form.get('location', None)
        if identifier and location:
            session = self.sessions[id]
            if session.welcome:
                session = self.sessions[id]
                session.identify(identifier, location)
                if location in self.registered:
                    self.registered[location][0](session)
                return response.write(json.encode(["OK", []]))
            else:
                return self.error_welcome(response)
        else:
            self.error_params(response, ['identifier', 'location'])

    def dynamic_resend(self, request,  response):
        start = request.form.get('start', None)
        end = request.form.get('end', None)
        try:
            start = int(start)
            end = int(end)
        except:
            return self.error_params(response, ['start', 'end'])
        id = request.form.get('id', None)
        if id not in self.sessions:
            return self.error_id(response)
        try:
            self.sessions[id].resend(start, end)
        # TODO: provide good error messages.
        except:
            response.write(json.encode(["ERR", ["Resend failed"]]))
        response.write(json.encode(["OK", []]))
        
    def dynamic_pong(browser):
        
        pass
    
    def error_id(self, response):
        return response.write(json.encode(['ERR', ['invalid id']]))
    
    def error_params(self, response, params):
        return response.write(json.encode['ERR', [ 'missing param', params ]])
    
    def error_welcome(self, response):
        return response.write(json.encode(['ERR', [ 'wait for WELCOME' ] ]))
    
    def transport_session_connect(self, transport_session):
        if not options['enabled']:
            return      
        if transport_session.key[0] not in self.sessions:
            transport_session.event(InternalOPRequest(json.encode([1, 'UNWELCOME', []])))
            transport_session.event(InternalOPRequest(json.encode([2, 'CLOSE', []])))
            return transport_session.close(force=False)
        session = self.sessions[transport_session.key[0]]
        session.welcome = True
        session.transport_session = transport_session
        transport_session.event(InternalOPRequest(json.encode([1, 'WELCOME', []])))
    
    def transport_session_close(self, transport_session):
        if not options['enabled']:
            return
        if transport_session.key[0] not in self.sessions:
            return
        session = self.sessions[transport_session.key[0]]
        full_identifier = session.identifier, session.location
        if full_identifier in self.identifiers:
            del self.identifiers[full_identifier]
        del self.sessions[transport_session.key[0]]
        session.close()
        
        
csp = CSP()    
    
class Session(object):
    msg_queue_limit = int(options['cache.queue_limit'])
    msg_time_limit = int(options['cache.time_limit'])
    def __init__(self, csp, id, time_count):
        # TODO: save the last X messages. configurable by time and by amount
        self.index = 1
        self.csp = csp
        self.id = id
        self.last_activity = time_count
        self.welcome = False
        self.identified = False
        self.identifier = None
        self.location = None
        self.transport_session = None
        self.events = []
        
        
    def close(self):        
        pass
        
    def identify(self,identifier, location):
        self.identified = True
        self.location = location
        self.identifier = identifier
        self.csp.identifiers[(identifier, location)] = self.id
    
    def payload_wrapper(self, id):
        def actual_wrapper(payload):
            return json.encode([ id, 'PAYLOAD', payload])
        return actual_wrapper
        
    def event(self, time_count, request):
        self.index += 1
        self.transport_session.event(request, self.payload_wrapper(self.index))
        if len(self.events) > self.msg_queue_limit:
            self.events.pop(0)
        encoded_payload = self.payload_wrapper(self.index)(request.payload)
        self.events.append([self.index, time_count, encoded_payload])
        
    def timeout(self, time_count):
        # [csp] cache.timelimit = 0 means no timeout
        if self.msg_time_limit == 0:
            return
        
        min_time = time_count - self.msg_time_limit
        i = 0
        while i > len(self.events):
            if self.events[i][1] < min_time:
                self.events.pop(0)
            else:
                i += 1

    def activity(self, time_count):
        self.last_activity = time_count

    def resend(self, start, end):
        if not self.events:
            #TODO: error
            raise Exception("ResendFailed")
        first = self.events[0][0]
        if first > start:
            raise Exception("ResendFailed")
        i = start - first
        j = end - first
        last = self.events[-1][0]
        if last < end - 1:
            raise Exception("ResendFailed")
        for k in range(i, j):
            self.transport_session.event(InternalOPRequest(self.events[k][2]))
"""