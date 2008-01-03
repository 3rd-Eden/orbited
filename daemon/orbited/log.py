from config import map as config
from datetime import datetime

global log
log = None
class Logger(object):
    
    def __init__(self, app):
        self.app = app
        self.enabled = True
        if config["[global]"]["log.enabled"] != '1':
            self.enabled = False
            return
        self.process = self._process
        self.events = []
        self.access, self.event, self.error = None, None, None
        self.screen = []
        self.load(config["[log]"])
        
    def __call__(self, *args):
        self._process(*args)
        
    def load(self, options):        
        for type in 'access', 'error', 'event':
            for item in options['log.%s' % type]:
                if item == 'screen':
                    self.screen.append(type)
                else:
                    setattr(self, type, open(item, 'a'))
        
        
    def _process(self, context, msg, severity=5):
        if not self.enabled:
            return
        if context == "startup":
            print msg#[0]
        file = getattr(self, context.lower(), None)
        time = str(datetime.now())[:-3]
        out = "\t".join([time, context, msg])
        if file:
        
            file.write('%s\n' % out)
            file.flush()            
        if context.lower() in self.screen:
            print out
    
def create(app):
    global log
    log = Logger(app)
    