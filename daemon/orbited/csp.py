#from orbited.router import router, CSPDestination
from orbited.op.message import SingleRecipientMessage
from orbited.http import HTTPRequest
import random
import event
#from orbited.dynamic import DynamicHTTPResponse
from orbited.json import json
#from orbited.orbit import InternalOPRequest
#from orbited.config import map as config
from orbited.transport import transports as supported_transports
from time import time

#router.register(CSPDestination, '/_/csp')
#router.register(StaticDestination, '/_/csp/static', '[orbited-static]')

class DuplicateConnection(Exception):
    pass


def echo(msg, conn):
    print 'CSP RECV: ' + msg
    conn.send(json.encode(['Echo', msg]))

def test(conn):
    print 'Detected CSP connection', conn
    conn.set_received_callback(echo, [conn])

class CSP(object):
  
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.dispatcher.app.cometwire.set_connect_cb('/_/csp/down', self.__connect)
        self.connections = {}
        self.unidentified_connections = {}
        self.connect_cbs = {}
        self.set_internal_connect_cb(80, test)
        
        
        
    def __conn_closed(self, id):
        conn = self.connections.pop(id, None)
        if conn:
            conn.close()
            self.dispatcher.app.orbit_daemon.signoff_cb(id)
            
    def __connect(self, transport_id, upstream_conn, downstream_conn):
        self.unidentified_connections[transport_id] = CSPConnection(
            self.__conn_closed, 
            self.__identify,
            transport_id, 
            upstream_conn, 
            downstream_conn )
    
    def __identify(self, transport_id, id, domain=None, port=None):
        if not domain:
            domain = "internal"
        # TODO: let OP know about a connect here, and wait for welcome or unwelcome, 
        #       or go ahead, as specified by the config.
        if id in self.connections:
            # TODO: best to close previous connection?
            self.connections[id].close()
            del self.connections[id]
        self.dispatcher.app.orbit_daemon.signon_cb(id)
        self.connections[id] = self.unidentified_connections.pop(transport_id)
        if domain == "internal" and port in self.connect_cbs:
            cb, args = self.connect_cbs[port]
            cb(self.connections[id], *args)
        
    def set_internal_connect_cb(self, port, cb, args=()):
        self.connect_cbs[port] = (cb, args)
    
    
    def contains(self, key):        
        return key in self.connections

    def get(self, key):
        return self.connections[key]
    
    def dispatch(self, msg):
        self.connections[msg.recipient].send_msgs([msg])
    
    
class CSPConnection(object):
    
    def __init__(self, closed_cb, identify_cb, transport_id, upstream, downstream):
        self.__closed_cb = closed_cb
        self.__identify_cb = identify_cb
        self.transport_id = transport_id
        self.id = None
        self.stream = Stream(upstream, downstream, self.__receive_frame)
        self.state = "initial"
        self.received_cb = (None, None)
        self.closed_cb = (None, None)
# ============================================
# Public
# ============================================
        
    def set_close_cb(self, cb, args):
        self.close_cb = (cb, args)
        
    def send_msgs(self, msgs):
        # TODO: Use success / failure callbacks
        for msg in msgs:
            self.stream.send("PAYLOAD", msg.payload)
        
    def send(self, data, success_cb=None, failure_cb=None):
        r = SingleRecipientMessage(data, self.id, success_cb, failure_cb)
        self.send_msgs([r])

    def disconnect(self):
        self.close()
        
    def set_received_callback(self, cb, args=()):
        self.received_cb = (cb, args)
        
    
# ============================================
# Internal Yoho Shizat
# ============================================
        
    def __receive_frame(self, type, payload):
        getattr(self, "receive_%s" % self.state)(type, payload)
        
    def receive_initial(self, type, payload):
        if type != "ID" or len(payload) != 3:
            return self.stream.send("UNWELCOME")
        self.state = "connected"
        self.__identify_cb(self.transport_id, *payload)
        self.stream.send("WELCOME")
            
    def receive_connected(self, type, payload):
        if type == "DISCONNECT":
            return self.close()
        elif type == "PAYLOAD":
#            self.stream.send("PAYLOAD", json.encode(["ECHO", payload]))
            cb, args = self.received_cb
            if cb:
                cb(payload, *args)
        
    def close(self):
        self.stream.send("DISCONNECT")
        print "CSP close", self.id

class Stream(object):
    
    def __init__(self, upstream, downstream, receive_cb):
        self.upstream = upstream
        self.downstream = downstream        
        self.__receive_cb = receive_cb
        self.upstream.set_receive_cb(self.__receive)
        self.sent_frames = {}
        self.resend_timers = {}
        self.received_frames = {}
        self.next_received_id = 1
        self.last_sent_id = 0

        self.sent_times = {}
        self.RESEND_TIMEOUT = 1.0
        self.total_roundtrip_s = 0
        self.num_ack_back = 0
        
    def __receive(self, data):
        try:
            frame = json.decode(data)
        except:
            pass # TODO: do we actually want to ignore bad frames?
        else:
            # Receive ACK from Client
            if len(frame) == 2 and frame[0] == "ACK":
                ack_id = int(frame[1])
                if ack_id in self.sent_frames:
                    del self.sent_frames[ack_id]
                    
                    delta = time() - self.sent_times.pop(ack_id)
                    self.total_roundtrip_s += delta
                    self.num_ack_back += 1
                    self.RESEND_TIMEOUT = self.total_roundtrip_s / self.num_ack_back

                    self.resend_timers[ack_id].delete()
                    del self.resend_timers[ack_id]
            
            elif len(frame) == 3 and frame[1] in ["PAYLOAD", "ID", "DISCONNECT" ]:
                
                id, type, args = frame
                
                if id >= self.next_received_id:
                    self.received_frames[id] = frame
                self.send("ACK", id)
                self.__check_received()
                
    def __check_received(self):
        while self.next_received_id in self.received_frames:
            frame = self.received_frames[self.next_received_id]
            id, type, payload = frame
            self.__receive_cb(type, payload)
            del self.received_frames[self.next_received_id]
            self.next_received_id += 1
                
    def send(self, type=None, payload=[], id=None):
        if type == "ACK":
            if not isinstance(payload, int):
                raise Exception("InvalidFrame")
            frame = ["ACK", payload]
        elif type in [ "WELCOME", "UNWELCOME", "PAYLOAD", "DISCONNECT" ]:
            self.last_sent_id += 1
            id = self.last_sent_id
            frame = [ id, type, payload ]
            self.sent_frames[id] = frame
            # Setup Frame timer
            self.resend_timers[id] = event.timeout(self.RESEND_TIMEOUT, self.__resend_timeout, id)
            self.sent_times[id] = time()
        elif id in self.sent_frames:
            frame = self.sent_frames[id]
        else:
            raise Exception("InvalidFrame")
        self.downstream.send(json.encode(frame))
        
    def __resend_timeout(self, id):
        self.send(id=id)
        return True
    
    
