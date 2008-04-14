transports = {
    'raw': None,
}

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
        self.connections[id].dispatch_http(req)
                
    def dispatch_op(self, op):
        print 'dispatch_op'
        if self.conn:
            print 'self.conn.write...'
            self.conn.write(op.payload)
        print 'conn', self.conn        
        
        
class TransportConnection(object):
    
    def __init__(self, key, handler):
        self.transport = None
        self.key = key
        self.handler = handler
        self.transport = None
                
    def dispatch_http(self, req):
        if self.transport and self.transport.name != req.form['transport']:
            self.transport.close()
            self.transport = None
        if not self.transport:
            self.transport = transports[req.form['transport']](self)
        self.transport.dispatch_http(req)
        
        
#    def 