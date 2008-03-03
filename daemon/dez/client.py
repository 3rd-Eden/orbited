from line_receiver import SocketClient, SocketDaemon, Connection

def main():
    client = SocketClient(cb=LocalEchoHTTPClient)
    client.connect("www.google.com",80)

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
