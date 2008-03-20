from dez.stomp.server.server import STOMPServer
from orbited.op.message import OrbitMessage
from orbited.stomp.transaction import STOMPTransaction

class STOMPDaemon(object):
    def __init__(self, host, port, dispatcher):
        self.server = STOMPServer(host, port)
        self.server.set_connect_cb(self.__connect_cb)
        self.dispatcher = dispatcher
        self.__send_cb = None
        self.connections = set()
        self.transactions = {}

    def __connect_cb(self, conn):
        conn.set_request_cb(self.__request_cb)
        conn.set_close_cb(self.__disconnect_cb, [conn])
        self.connections.add(conn)

    def __disconnect_cb(self, conn):
        if conn in self.connections:
            self.connections.remove(conn)

    def __request_cb(self, frame):
        if frame.action == 'BEGIN':
            self.transactions[frame.headers['transaction']] = STOMPTransaction(self,frame.headers['transaction'])
        elif 'transaction' in frame.headers:
            self.transactions[frame.headers['transaction']](frame)
        elif frame.action == 'SEND':
            recipients = frame.headers['destination']
            payload = frame.body
            m = OrbitMessage(recipients, payload, self.__message_cb, [frame])
            self.dispatcher.dispatch_orbit(m)
        frame.received()

    def __message_cb(self, message, frame):
        if message.failure_recipients:
            frame.failure(message.failure_recipients)
        if message.success_recipients:
            frame.success(message.success_recipients)

    def commit(self, frame):
        self.__request_cb(frame)

    def abort(self, trans_id):
        del self.transactions[trans_id]

    def signon_cb(self, key):
        for conn in self.connections:
            conn.signon_cb(",".join(key))

    def signoff_cb(self, key):
        for conn in self.connections:
            conn.signoff_cb(",".join(key))
