from orbited.app import Application


def main():
    app = Application()
    handler = MapHandler(app)
    app.start()
    
class MapHandler(object):
    def __init__(self, app):
        self.app = app
        self.app.set_session_handler(self)
        self.connections = []
        
    def event(self, event):
        print 'event here'
        conn = self.app.tcp.connections[event.id]
        if event.name == "open":
            self.on_open(conn)
        if event.name == "recv":
            self.on_recv(conn, event.data)
        if event.name == "close":
            self.on_close(conn)
        
    def encode(self, addr):
        print "encoding:", addr
        return "[ 55, 47 ]"
    
    def on_open(self, conn):
        self.connections.append(conn)
        self.broadcast(self.encode(conn.conn.conn.request.conn.transport.getPeer()))

    def on_recv(self, conn, data):
        
        print 'why are we receiving:', data
#        print 'on recv'
#        conn.send("You sent: " + data)
        
    def on_close(self, conn):
        self.connections.remove(conn)
        
    def broadcast(self, data):
        for conn in self.connections:
            conn.send(data)
        
if __name__ == "__main__":
    main()