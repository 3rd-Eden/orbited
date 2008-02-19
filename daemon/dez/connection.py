from line_receiver import SocketClient, SocketDaemon, Connection
import sys

def main():
    client = SocketClient(cb=LocalEchoHTTPClient)
    client.connect("www.google.com",80)

def main2():
    server = SocketDaemon("localhost", 9119, cb=LengthConnection)
    server.start()

class LocalEchoHTTPClient(object):
    def __init__(self, conn):
        self.conn = conn
        self.conn.write("GET / HTTP/1.0\r\nHost: www.google.com\r\n\r\n")
        self.conn.set_mode_delimiter('\r\n', self.line_received)
        
    def line_received(self, data):
        if data == "": # end of headers
            print "[end of headers]"
            self.conn.set_mode_close(self.body)
        else:
            print data
            
    def body(self, data):
        print data
        sys.exit(0);

class EchoConnection(object):
    def __init__(self, conn):
        self.conn = conn
        self.conn.set_mode_delimiter('\r\n', self.line_received)

    def line_received(self, data):
        self.conn.write("S: " + data + '\r\n')

class LengthConnection(object):
    def __init__(self, conn):
        self.conn = conn
        self.conn.set_mode_delimiter('\r\n', self.length_received)

    def length_received(self, data):
        try:
            length = int(data)
        except:
            self.conn.write('Invalid integer: %s'%data, self.close)
        else:
            self.conn.set_mode_size(length,self.body_received)

    def body_received(self, body):
        self.conn.write('s:%s'%body,self.close)

    def close(self):
        self.conn.close()

if __name__ == '__main__':
    main()
"""
class HTTPConnection(object):
   
    def __init__(self, conn):
        self.conn = conn
        self.conn.set_mode_delimiter('\r\n', self.action)
        self.request = HTTPRequest()

    def action(self, data):
        self.request.set_action(data)
        self.conn.set_mode_delimiter('\r\n', self.header)

    def header(self, data)
        if len(data) == 0:
            if self.request.content_length > 0:
                self.conn.set_mode_size(self.body, self.request.content_length)
            else:
                self.conn.pause()
                self.dispatch()
        self.request.set_header(data)


    def body(self, data):
        self.request.set_body(data)
        self.dispatch()



class HTTPRequest(object):

    def __init__(self):
        self.content_length = 0
   
    def set_action(self, data):
        action, location, protocol = data.split(' ')
        protocol_name, protocol_version = protocol.split('/')
        version_major, version_minor = protocol_version.split('.')

    def set_header(self, data):
        if
        name, val = data.split(': ')
        if name.lower == 'content-length':
            self.content_length = int(val)
        ...
from dez.server import SocketDaemon, Connection

def main():
    server = SocketDaemon("localhost", 80, cb=HTTPConnection)

class HTTPConnection(object):
   
    def __init__(self, conn):
        self.conn = conn
        self.conn.set_mode_delimiter('\r\n', self.action)
        self.request = HTTPRequest()

    def action(self, data):
        self.request.set_action(data)
        self.conn.set_mode_delimiter('\r\n', self.header)

    def header(self, data)
        if len(data) == 0:
            if self.request.content_length > 0:
                self.conn.set_mode_size(self.body, self.request.content_length)
            else:
                self.conn.pause()
                self.dispatch()
        self.request.set_header(data)


    def body(self, data):
        self.request.set_body(data)
        self.dispatch()



class HTTPRequest(object):

    def __init__(self):
        self.content_length = 0
   
    def set_action(self, data):
        action, location, protocol = data.split(' ')
        protocol_name, protocol_version = protocol.split('/')
        version_major, version_minor = protocol_version.split('.')

    def set_header(self, data):
        if
        name, val = data.split(': ')
        if name.lower == 'content-length':
            self.content_length = int(val)
        ...
        
"""