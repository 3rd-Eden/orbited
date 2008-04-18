__version__ = "0.4.twisted.a1" # TODO: from orbited import __version__


class TransportHandler(object):
  
  
    def __init__(self, app):
        self.app = app
        self.connections = {}
        self.conn = None
        
    def dispatch_http(self, req):
      
        transport_name = req.form.get('transport', None)
        if transport_name is None:
            return req.error("Transport name not specified")
        
        if transport_name not in transports:
            return req.error("Invalid Transport Name: %s" % transport_name)
        
        id = req.form.get('id', None)      
        if id is None:
            return request.error("id must be specified for Orbited request")
        if id not in self.connections:
            self.connections[id] = TransportConnection(id, self)
        self.connections[id].http_open(req)
                
    def dispatch_op(self, op):
        print 'dispatch_op'
        if op.recipient not in self.connections:
            print 'recipient', op.recipient, 'not found'
            return
        conn = self.connections[op.recipient]
        m = Message(op.recipient, op.payload)
        conn.send(m)


class Message(object):
    def __init__(self, recipient, payload):
        self.recipient = recipient
        self.payload = payload

        
class TransportConnection(object):
    
    def __init__(self, key, handler, reliable=True):
        self.reliable = reliable
        self.transport = None
        self.key = key
        self.handler = handler
        self.transport = None
        self.message_queue = []
        self.awaiting_ack = []
        self.id = 0
        
    def http_open(self, req):
        if self.transport and self.transport.name != req.form['transport']:
            self.transport.close()
            self.transport = None
        if not self.transport:
            self.transport = transports[req.form['transport']](self)
        self.transport.http_open(req)
        self.flush()
        
    def http_close(self, req):
        if self.transport:
            self.transport.http_close(req)
        
    def flush(self):
        if self.transport.ready and self.message_queue:
            message_group = self.message_queue
            self.message_queue = []
            if self.reliable:
                self.id += 1
                self.awaiting_ack[self.id] = message_group
            self.transport.push(message_group, self.id)
    
    def send(self, message):
        self.message_queue.append(message)
        self.flush()
        
class SSETransport(object):
    name = 'sse'
    def __init__(self, conn):
        self.conn = conn
        self.browser_conn = None
        self.ready = False
        
    def http_open(self, req):
        if self.browser_conn:
            self.browser_conn.end()
            
        self.browser_conn = req.HTTPVariableResponse()
        self.initial_response()
        self.ready = True
    def http_close(self, req):
        if self.conn.request == req:
            self.conn = None
            self.ready = False
        
    def initial_response(self):
        self.browser_conn.status = '200 OK'
        self.browser_conn.headers['Server'] = 'Orbited/%s' % __version__
        self.browser_conn.headers['Content-type'] = 'text/event-stream'
        self.browser_conn.write('retry:5000\n\n')
        
    def push(self, messages, id):
        self.browser_conn.write(self.encode(messages, id))
        
    def encode(self, messages, id):
            
        msgs = []
        for msg in messages:
            msgs.append('\n'.join(['data:%s' % line for line in msg.payload.splitlines()]))
        
        output = ( 
            '\n\n'.join(msgs) + '\n' + 
            'id:%s\n' % id +
            '\n'
        )
        return output
        
transports = {
    'sse': SSETransport,
}
