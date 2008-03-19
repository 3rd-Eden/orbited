from dez.op.server.server import OPServer
from orbited.op.message import OrbitMessage

class OPDaemon(object):
  
    def __init__(self, host, port, dispatcher):
        self.server = OPServer(host, port)
        self.server.set_connect_cb(self.__connect_cb) # **
        self.dispatcher = dispatcher
#        self.server.set_disconnect_cb(self.__disconnect_cb) # **
        self.__send_cb = None
        self.callbacks = {
            'failure': [],
            'success': [],
            'signon': [],
            'signoff': [],        
        }
        self.connections = []
    
    def __connect_cb(self, conn):
        conn.set_request_cb(self.__request_cb)
        self.connections.append(conn)
            
    def __disconnect_cb(self, conn):
        if conn in self.connections:
            self.connections.remove(conn)
        
    def __request_cb(self, frame):
        print 'FRAME:', frame.action
        if frame.action == 'CONNECT':
            # The server will only relay this frame if we haven't seen a 
            # CONNECT frame yet. It will auto-reply with error if we already
            # saw a CONNECT frame.
            frame.received() # **
            
#        if frame.action == 'CALLBACK':
#            self.callbacks[frame.headers['function']] = frame.callback_cb
#            frame.received() # **
            
        if frame.action == 'SEND':
            # If we haven't already gotten a CONNECT frame, this won't be relayed.
            recipients = frame.headers['recipients'] # **
            payload = frame.body # **
            m = OrbitMessage(recipients, payload, self.__message_cb, [frame])
            self.dispatcher.dispatch_orbit(m) # test with event.timeout(X, emulate_send_succ or emulate_send_failure, m, frame)
            frame.received() # **
        
    def __message_cb(self, message, frame):
        if message.failure_recipients:
            print 'MESSAGE failed'
        else:
            print 'MESSAGE success'
        return
        if message.failure_recipients:
            self.server.callback('failure', {
                'recipients': message.failed_recipients,
                'id': frame.headers['id'],
            })
        if message.succeeded_recipients:                        
            self.server.callback('failure', {
                'recipients': message.succeeded_recipients,
                'id': frame.headers['id']
            })

    def signon_cb(self, key):
        print "KEY SIGNED ON", key
        for conn in self.connections:
            conn.signon_cb({'key': ",".join(key)})
            
    def signoff_cb(self, key):
        print "KEY SIGNED OFF", key
        for conn in self.connections:
            conn.signoff_cb({'key': key})