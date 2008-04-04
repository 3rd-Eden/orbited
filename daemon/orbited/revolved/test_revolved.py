from revolved import *
from auth.memory import RevolvedMemoryAuthBackend
from backends.simple import SimpleRevolvedBackend
from test_backend import RevolvedDispatcherPlaceholder
from orbited.json import json

class TestRevolved(object):
    
    def setup(self):
        self.csp = DummyCSPHandler()
        self.dispatcher = RevolvedDispatcherPlaceholder()
        self.backend = SimpleRevolvedBackend(self.dispatcher)
        self.auth_backend = RevolvedMemoryAuthBackend({
            'michael': {
                'password': 'michaelpass',
                'connect': True,
                'subscribe': True,
                'publish': ['orbited', 'comet'],
            },
            'mario': {
                'password': 'mariopass',
                'connect': True,
                'subscribe': ['orbited'],
                'publish': ['orbited'],
            },
            'marcus': {
                'connect': True,
                'subscribe': True,
                'publish': [],
            },
            # All other users
            None: {
                'connect': False,
                'subscribe': False,
                'publish': [],
            },
        })
        self.revolved = RevolvedHandler(self.csp, self.backend, self.auth_backend)
        
    def test_connect(self):
        conn = DummyCSPConnection()
        conn2 = DummyCSPConnection()
        self.csp.trigger_connection_made(80, conn)
        self.csp.trigger_connection_made(80, conn2)
        assert len(self.revolved.connections) == 2
        
    def test_disconnect(self):
        conn = DummyCSPConnection()
        self.csp.trigger_connection_made(80, conn)
        assert len(self.revolved.connections) == 1
        conn.disconnect()
        assert len(self.revolved.connections) == 0
    
    def test_message(self):
        conn = DummyCSPConnection()
        # Add a sample message callback to verify that we received it
        self.message_text = None
        def _message_cb(conn, msg):
            print 'cb...', conn, msg
            self.message_text = msg
        conn.set_message_callback(_message_cb)
        # Now trigger a message
#        self.csp.trigger_connection_made(80, conn)
        conn.trigger_receive_message('[1,"PONG", []]')
        print self.message_text
        assert self.message_text == '[1,"PONG", []]'
    
    def test_auth(self):
        # Create the connection
        conn = DummyCSPConnection()
        self.csp.trigger_connection_made(80, conn)
        
        # Try authenticating the client
        self.sent_msg = None
        def conn_send(msg):
            self.sent_msg = msg
        conn.send = conn_send
    
        # Anonymous User
        conn.trigger_receive_message(json.encode([1, "AUTH", ["", ['']]]))
        assert self.sent_msg == json.encode([1, "ERR", ["Not Allowed"]])
        # Invalid User
        conn.trigger_receive_message(json.encode([1, "AUTH", ['blah', ['']]]))
        assert self.sent_msg == json.encode([1, "ERR", ["Invalid User"]])
        # Invalid Password
        conn.trigger_receive_message(json.encode([1, "AUTH", ['mario', ['badpass']]]))
        assert self.sent_msg == json.encode([1, "ERR", ["Invalid Password"]])
        # Valid Auth
        conn.trigger_receive_message(json.encode([1, "AUTH", ['mario', ['mariopass']]]))
        assert self.sent_msg == json.encode([1, "OK", [""]])
          
    def test_subscribe(self):
        # Create the connection
        conn = DummyCSPConnection()
        self.csp.trigger_connection_made(80, conn)
        
        self.sent_msg = None
        def conn_send(msg):
            self.sent_msg = msg
        conn.send = conn_send
        
        conn.trigger_receive_message(json.encode([1, "AUTH", ['mario', ['mariopass']]]))
        conn.trigger_receive_message(json.encode([2, "SUBSCRIBE", ['orbited']]))
        assert self.sent_msg == json.encode([2, "OK", [""]])
        conn.trigger_receive_message(json.encode([3, "SUBSCRIBE", ['not-allowed-channel']]))
        assert self.sent_msg == json.encode([3, "ERR", ["Not Authorized"]])
        
    def test_publish(self):
        # Create the connection
        conn = DummyCSPConnection()
        self.csp.trigger_connection_made(80, conn)
        revolved_conn = self.revolved.connections[0]

        self.sent_msg = None
        def conn_send(msg):
            self.sent_msg = msg
        conn.send = conn_send
        
        conn.trigger_receive_message(json.encode([1, "AUTH", ['mario', ['mariopass']]]))
        conn.trigger_receive_message(json.encode([2, "SUBSCRIBE", ['orbited']]))
        assert self.sent_msg == json.encode([2, "OK", [""]])
        conn.trigger_receive_message(json.encode([3, "PUBLISH", ['orbited', 'hello world']]))
        assert self.sent_msg == json.encode([3, "OK", [""]])
        assert self.dispatcher.published_messages == {u'orbited': [[u'mario', u'orbited', u'hello world']]}
        # Actually do the send
        revolved_conn.send([0, "PUBLISH", ['orbited', 'hello world']])
        print self.sent_msg
        assert self.sent_msg == json.encode([0, "PUBLISH", ['orbited', 'hello world']])
       
    def test_send(self):
        # Create the connection
        conn = DummyCSPConnection()
        conn2 = DummyCSPConnection()
        self.csp.trigger_connection_made(80, conn)
        self.csp.trigger_connection_made(80, conn2)

        self.sent_msg = None
        def conn_send(msg):
            self.sent_msg = msg
        conn.send = conn_send
        
        conn.trigger_receive_message(json.encode([1, "AUTH", ['mario', ['mariopass']]]))
        conn2.trigger_receive_message(json.encode([1, "AUTH", ['michael', ['michaelpass']]]))
        conn.trigger_receive_message(json.encode([2, "SUBSCRIBE", ['orbited']]))
        conn.trigger_receive_message(json.encode([3, "SEND", ['michael', 'hello world']]))
        assert self.dispatcher.sent_messages == [[u'mario', u'michael', u'hello world']]
        conn.trigger_receive_message(json.encode([3, "SEND", ['unknownrecipient', 'hello world']]))
        assert self.sent_msg == json.encode([3, "ERR", ["User Not Found"]])
        assert self.dispatcher.sent_messages == [[u'mario', u'michael', u'hello world']]
    
    def test_disconnect(self):
        # Create the connection
        conn = DummyCSPConnection()
        conn2 = DummyCSPConnection()
        self.csp.trigger_connection_made(80, conn)
        self.csp.trigger_connection_made(80, conn2)
        # Try BOTH authenticated and non-authenticated connections
        conn.trigger_receive_message(json.encode([1, "DISCONNECT", []]))
        conn.trigger_receive_message(json.encode([1, "AUTH", ['mario', ['mariopass']]]))
        conn2.trigger_receive_message(json.encode([1, "DISCONNECT", []]))
        assert len(self.revolved.connections) == 0