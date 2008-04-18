__version__ = "0.4.twisted.alpha1"

class SSEConnection(object):
    
    def __init__(self, request):
        self.conn = request.HTTPVariableResponse()
        self.conn.status = '200 OK'
        self.conn.headers['Server'] = 'Orbited/%s' % __version__
        self.conn.headers['Content-type'] = 'text/event-stream'
    
    def write_event(self, name):
        self.conn.write('event:%s\n' % name)
    def write_data(self, value):
        self.conn.write('\n'.join(['data:%s' % d for d in value.splitlines()]) + '\n')
    def write_id(self, value):
        self.conn.write('id:%s\n' % value)
    def write_retry(self, retry):
        self.conn.write('retry:%s\n' % retry)
    def write_dispatch(self):
        self.conn.write('\n')
    def flush(self):
        self.conn.flush()
    def close(self):
        self.conn.end()
        
    