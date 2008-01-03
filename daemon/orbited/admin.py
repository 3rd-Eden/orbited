
SEP = '|'
        
class AdminDaemon(object):
    def __init__(self, port, log):
        log("startup", "Created Admin@%s" % port)
        pass

class AdminConnection(object):

    def read_ready(self):
        try:
            data = self.sock.recv(io.BUFFER_SIZE)
        except:
            data = None
        if not data:
            self.close()
            return None
        return self.read(data)

    def read(self, data):
        complete = self.request.read(data)
        if not complete:
            return True
        
    
class AdminRequest(object):
    """
LOG|type=all|file=log.txt
SETTINGS|max_connections=50|timeout=300
START_COUNTING|
STOP_COUNTING|
COUNT_REPORT|    
    """
    
    def __init__(self):
        self.buffer = ""
        
    def read(self, data):
        self.buffer += data
        return self.process()
        
    def process(self):
        if '\r\n' not in self.buffer:
            return False        
        index = self.buffer.find('\r\n')
        self.line = self.buffer[:index]
        self.buffer = self.buffer[index+2:]
        index = self.line.find('SEP')   
        self.cmd = self.line[:index].lower()
        #TODO: Lower case the keys
        self.details = dict([ i.split('=') for i in self.line[index+1:].split('|') ])
        return True


class AdminApp(object):
    
    def __init__(self, main_app, port):
        self.main_app = main_app
        self.log = main_app.log
        self.daemon = AdminDaemon(port, self.log)
        self.request = None
        
    def incoming_request(self, request):
        getattr(self, 'cmd_%s' % request.cmd)(request)
        
        
    def cmd_start_counting(self, request):
        self.app.logger
        pass
        
        
    def __call__(self, action, details):
        pass
