from dez.op.server.server import OPServer
from orbited.op.message import OrbitMessage

class OPDaemon(object):
  
    def __init__(self, host, port, dispatcher):
        self.server = OPServer(host, port)
        self.server.set_connect_cb(self.__connect_cb)
        self.dispatcher = dispatcher
        self.__send_cb = None
        self.connections = []
    
    def __connect_cb(self, conn):
        conn.set_request_cb(self.__request_cb)
        conn.set_close_cb(self.__disconnect_cb, [conn])
        self.connections.append(conn)
            
    def __disconnect_cb(self, conn):
        if conn in self.connections:
            self.connections.remove(conn)
        
    def __request_cb(self, frame):
        print 'FRAME:', frame.action
        if frame.action == 'CONNECT':
            frame.received()
            
        if frame.action == 'CALLBACK':
            frame.received()
            
        if frame.action == 'SEND':
            recipients = frame.headers['recipients']
            payload = frame.body
            m = OrbitMessage(recipients, payload, self.__message_cb, [frame])
            self.dispatcher.dispatch_orbit(m)
            frame.received()
        
    def __message_cb(self, message, frame):
        if message.failure_recipients:
            frame.failure(message.failure_recipients)
        else:
            frame.success(message.success_recipients)

    def signon_cb(self, key):
        for conn in self.connections:
            conn.signon_cb({'key': ",".join(key)})
            
    def signoff_cb(self, key):
        for conn in self.connections:
            conn.signoff_cb({'key': key})
