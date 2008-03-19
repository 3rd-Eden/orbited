import socket
from orbited.json import json


class OrbitClient(object):
  
    def __init__(self, host='127.0.0.1', port=9000):
        self.host = host
        self.port = port
        self.id = None
        
    def connect(self):
        self.id = 1
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect_ex((self.host, self.port))
            self.sock.send(
                "CONNECT\r\n"
                "id: 1\r\n"
                "response: receipt\r\n"
                "connection_id: client\r\n"
                "\r\n"
                "^@\r\n"
            )
            return self.read_frame()
        except:
            raise
            return False

    def callback(self, function, url):
        self.id+=1
        self.sock.send(
            "CALLBACK\r\n"
            "id: %s\r\n"
            "function: %s\r\n"
            "url: %s\r\n"
            "\r\n"
            "^@\r\n" % (self.id, function, url)
        )
        return self.read_frame()
    
    def send(self, recipients, payload, json_encode=True):
        self.id += 1
        self.sock.send(
            "SEND\r\n"
            "id: %s\r\n" % (self.id)
        )
        if json_encode:
            payload = json.encode(payload)
        for recipient in recipients:
            self.sock.send('recipient: %s\r\n' % (recipient,))
        self.sock.send('\r\n')
        self.sock.send(payload)
        self.sock.send('^@\r\n')
        return self.read_frame()
    
    def read_frame(self):
        frame = ""
        while '^@\r\n' not in frame:
            frame += self.sock.recv(1024)
        return Frame(frame)


class Frame(object):
  
    def __init__(self, data):
        i = 0
        j = data.find('\r\n')
        self.action = data[:j]
        self.headers = {}
        i = j+2
        while True:
            j = data.find('\r\n', i)
            segment = data[i:j]
            if len(segment) == 0:
                break
            key, val = segment.split(':', 1)
            self.headers[key] = val
            i = j+2
        j = data.find('^@\r\n', i)
        self.body = data[j:i]
        
    def __str__(self):
        return repr(self)
    def __repr__(self):
        output =  "<Frame %s\n" % self.action
        for k, v in self.headers.items():
            output += "\t%s:%s\n" % (k, v)
        output += self.body
        output += " >"
        return output
