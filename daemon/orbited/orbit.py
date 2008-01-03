import io
import event
from debug import *

class OrbitDaemon(object):

    def __init__(self, app, log, port):
        log("startup", "Created Orbit@%s" % port)
        self.log = log
        self.index = 0
        self.port = port
        self.app = app
        self.sock = io.server_socket(port)
        self.listen = event.event(self.accept_connection, 
            handle=self.sock, evtype=event.EV_READ | event.EV_PERSIST)
        self.listen.add()
        
    def accept_connection(self, event_, sock, event_type, *arg):
        self.index+=1
        connection = OrbitConnection(sock.accept(), self.index, self.app, self.log)
        
        
class OrbitConnection(object):
    def __init__(self, (sock, addr), id, app, log):
        self.log = log
        debug("Accepting Orbit Connection [id: %s ] from %s on port %s" % ((id,) + addr))
        self.log("ACCESS", "ORBIT\t[id: %s]\t%s\t%s" % ((id,) + addr))
        self.id = id
        self.app = app
        self.addr = addr
        self.sock = sock
        self.revent = event.read(sock, self.read_data)
        self.wevent = None
        self.response_queue = []
        self.write_buffer = ""
        self.request = Request(self, self.log)
        
    def close(self):
        debug("Closing Orbit Connection [id: %s ] from %s on port %s" % ((self.id,) + self.addr))
        self.wevent = None
        self.revent = None
        self.sock.close()
        
        
        
    def read_data(self):
        try:
            data = self.sock.recv(io.BUFFER_SIZE)
        except:
            data = None
        if not data:
            self.close()
            return None
        try:
            self.request.read_data(data)
        except RequestComplete, ex:
            debug("Request finished. Start a new one")
            self.app.accept_orbit_request(self.request)
            self.request = Request(self, self.log, ex.leftover_buffer)   
            while True:
                try:
                    self.request.process()
                    break
                except RequestComplete, ex:
                    self.app.accept_orbit_request(self.request)
                    self.request = Request(self, self.log, ex.leftover_buffer)
        return True
        
    def write_data(self):
        try:
            bsent = self.sock.send(self.write_buffer)
            debug("wrote:\n======\n%s" % self.write_buffer[:bsent])
            self.write_buffer = self.write_buffer[bsent:]
            return self.write_next()
        except io.socket.error:
            return None
            
    def write_next(self):
        if not self.write_buffer:
            if not self.response_queue:
                self.wevent = None
                return None
            else:
                self.write_buffer = self.response_queue.pop(0)
                if not self.wevent:
                    self.wevent = event.write(self.sock, self.write_data)
                return True
                    
    def respond(self, response):
        self.response_queue.append(response)
        self.write_next()
        
from debug import *
import random


class RequestComplete(Exception):

    def __init__(self, leftover_buffer):
        self.leftover_buffer = leftover_buffer
        Exception.__init__(self)


    
class Request(object):

    def __init__(self, connection, log, buffer=""):
        self.log = log
        self.connection = connection
        self.version = None
        self.type = None
        self.id = None
        self.recipients = []
        self.replies = {}
        self.state = "version"
        self.buffer = buffer
        
    def key(self):
        if not self.id:
            raise "NoKey"        
        return self.connection.id, self.id
        
        
    def read_data(self, data):
#        print "read:\n=====\n %s" % data
        self.buffer += data
        self.process()
            
    def process(self):
        if self.state == 'body':
            if len(self.buffer) < self.length:
                return
            self.body = self.buffer[:self.length]
            debug("body: %s" % self.body)
            self.buffer = self.buffer[self.length:]
            raise RequestComplete(self.buffer)
            
        if '\r\n' in self.buffer:
            i = self.buffer.find('\r\n')
            line = self.buffer[:i]
            self.buffer = self.buffer[i+2:]
            getattr(self, 'state_%s' % self.state)(line)
            self.process()
            
        
    def state_version(self, line):
        debug("version: %s" % line)
        self.version = line
        self.state = 'type'
        
    def state_type(self, line):
        debug("type: %s" % line)
        self.type = line
        self.state = "headers"
        
    def state_headers(self, line):
        debug("header: %s" % line)
        if line == '':
            self.state = 'body'
            return
        name, content = line.split(': ')
        name = name.lower()
        if name == 'id':
            self.id = content
        elif name == 'recipient':
            self.recipients.append(tuple(content.split(', ')))
        elif name == 'length':
            self.length = int(content)

    def error(self, recipient_key):
        recipient = "(%s, %s, %s)" % recipient_key
        self.replies[recipient] = 0
        if len(self.replies.keys()) == len(self.recipients):
            self.reply()
            
    def success(self, recipient_key):
        recipient = "(%s, %s, %s)" % recipient_key
        self.replies[recipient] = 1
        if len(self.replies.keys()) == len(self.recipients):
            self.reply()

    def reply(self):
        if len(self.recipients) == sum(self.replies.values()):
            self.reply_success()
        else:
            self.reply_failure()
    
    def reply_success(self):
        response = "Success\r\nid: %s\r\n\r\n" % self.id
        self.connection.respond(response)
        
    def reply_failure(self):
        response = "Failure\r\nid: %s\r\nmsg: Failed to reach one or more recipients\r\n" % self.id
        for recipient, success in self.replies.items():
            if not success:
                response += "recipient: %s\r\n" % (recipient,)
        response += "\r\n"
        self.connection.respond(response)
        