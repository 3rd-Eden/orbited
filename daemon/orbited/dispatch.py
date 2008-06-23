from tcp import TCPConnection, TCPConnectionFactory
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from config import map as config
from logger import get_logger

logger = get_logger('Dispatch')

class DispatchConnection(TCPConnection):
    ping_timeout = 30
    ping_interval = 30
    
    def setup(self):
        self.state = "initial"
        self.dispatch_key = None
        
    def dataReceived(self, data):
        getattr(self, 'state_' + self.state)(data)
                
    def state_initial(self, data):
        self.dispatch_key = data
        self.factory.dispatch_connections[data] = self
        self.state = 'devnull'
        # TODO: notify web app of signon (http callback?)
        
    def state_devnull(self, data):
        pass
        
        
    def connectionLost(self):
        if self.dispatch_key:
            # TODO: notify web app of signoff (http callback?)
            if self.factory.dispatch_connections[self.dispatch_key] == self:
                del self.factory.dispatch_connections[self.dispatch_key]

class DispatchFactory(TCPConnectionFactory):
    protocol = DispatchConnection

    def __init__(self, *args, **kwargs):
        TCPConnectionFactory.__init__(self, *args, **kwargs)
        self.dispatch_connections = {}
        self.factory = DispatchProtocolFactory(self)
        port = int(config['[global]']['dispatch.port'])
        logger.info('Listening Orbit@%s (legacy dispatch protocol)' % port)
        reactor.listenTCP(port, self.factory)
      
    def receive_frame(self, conn, headers, body):
        response = ['Success', {
            'id': headers['id']
        }]
        for recipient in headers['recipients']:
            if recipient in self.dispatch_connections:
                self.dispatch_connections[recipient].send(body)
            else:
                response[0] = 'Failure'
                if 'msg' not in response[1]:
                    response[1]['msg'] = 'One or more recipients is not present:'
                response[1]['msg'] += ' ' + recipient
        conn.send_frame(*response)
        
"""
Orbit/1.0\r\n
Action: Event\r\n
Id: 45\r\n
Recipient: (michael, 123, /event)\r\n
Recipient: (jacob, 543, /event)\r\n
Length: 10\r\n
\r\n
event text
"""      

class DispatchProtocolFactory(Factory):
    def __init__(self, root):
        self.root = root
        self.protocol = DispatchProtocol
        
    def buildProtocol(self, addr):
        logger.access('Dispatch [ %s ] ' % (addr,))
        return DispatchProtocol(self.root.receive_frame)
    
class DispatchProtocol(Protocol):
  
    def __init__(self, cb=None):
        self.buffer = ""
        self.state = 'headers'
        if cb:
            self.receive_frame = cb
            
            
    def send_frame(self, status, headers):
        self.transport.write('%s\r\n' % status)
        for key, val in headers.items():
            self.transport.write('%s: %s\r\n' % (key, val))
        self.transport.write('\r\n')
        
    def dataReceived(self, data):
        self.buffer += data
        getattr(self, 'read_%s' % self.state)()
        
    def receive_frame(self, conn, headers, body):
        print "Received Frame"
        print headers
        print body
        print '==='
        
    def read_headers(self):
        if '\r\n\r\n' not in self.buffer:
            return
        data, self.buffer = self.buffer.split('\r\n\r\n', 1)
        protocol, raw_headers = data.split('\r\n', 1)
        
        #remove frame type
        frame_type, raw_headers = raw_headers.split('\r\n', 1)
        
        logger.info(raw_headers)
        header_fields =[ d.split(': ') for d in raw_headers.split('\r\n') ]
        headers = { 'recipients': [ ] }

        for (key, val) in header_fields:
            key = key.lower()
            if key == 'recipient':
                headers['recipients'].append(val)
            elif key == 'recipients':
                # error
                pass
            elif key == 'length':
                headers['length'] = int(val)
            else:
                headers[key] = val

        self.current_headers = headers
        self.state = 'body'
        self.read_body()
        
    def read_body(self):
        if len(self.buffer) < self.current_headers['length']:
            return
        body =  self.buffer[:self.current_headers['length']]
        self.buffer = self.buffer[len(body):]
        self.receive_frame(self, self.current_headers, body)
        self.current_headers = None
        self.state = 'headers'
        self.read_headers()
