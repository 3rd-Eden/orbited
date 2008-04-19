from orbited.app import Application


def main():
    app = Application()
    example_handler = ExampleHandler(app)
    app.start()
    
class ExampleHandler(object):
    def __init__(self, app):
        self.app = app
        self.app.set_session_handler(self)
        
    def event(self, event):
        print 'event here'
        conn = self.app.tcp.connections[event.id]
        if event.name == "open":
            self.on_open(conn)
        if event.name == "recv":
            self.on_recv(conn, event.data)
        if event.name == "close":
            self.on_close(conn)
        
    def on_open(self, conn):
        print 'on open'
        conn.send("Welcome to the Example app!")
    
    def on_recv(self, conn, data):
        print 'on recv'
        conn.send("You sent: " + data)
        
    def on_close(self, conn):
        print "Lost Connection to: %s" % (conn.id,)    
        
if __name__ == "__main__":
    main()