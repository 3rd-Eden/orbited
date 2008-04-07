from datetime import datetime
import sys
import traceback
#from orbited.config import map as config
val = []
def setup(configmap):
    if val:
        return val[0]
    defaults = {}
    for logtype in [ 'debug', 'access', 'warn', 'error', 'info' ]:
        defaults[logtype] = []        
        a = configmap['[logging]']
        b =a[logtype]
        outputs = b.split(',')
        for loc in outputs:
            loc = loc.strip()
            if not loc:
                continue
            if loc == 'enabled.default':
                continue
            if loc == 'SCREEN':
                defaults[logtype].append(ScreenLog())
            else:
                defaults[logtype].append(FileLog(loc))
            defaults[logtype][-1].open()
            
    overrides = {}
    for key, value in configmap['[loggers]'].items():
        overrides[key] = int(value)
    enabled = int(configmap['[logging]']['enabled.default']) == 1
    val.append(LoggerRoot(enabled, defaults, overrides))
    return val[0]
            
class LoggerRoot(object):
  
    def __init__(self, enabled, defaults={}, overrides = {}):
        self.enabled = enabled
        self.defaults = defaults
        self.overrides = overrides
        self.loggers = {}
        
        
    def create_logger(self, name):
        override_enabled = False
        if name in self.overrides:
            override_enabled = int(self.overrides[name]) == 1
            if not override_enabled:
                return Logger(name, False, {})
        enabled=(override_enabled or self.enabled)
        return Logger(name, enabled, self.defaults)
        
    def get_logger(self, name):
        if name not in self.loggers:
            self.loggers[name] = self.create_logger(name)
        return self.loggers[name]
        
    def add_logger(self, name, logger):
        self.loggers[name] = logger
        
class Logger(object):
  
    def __init__(self, name, enabled, defaults):
        self.defaults = defaults
        self.name = name
        if not enabled:
            self.debug = self._empty
            self.access = self._empty
            self.warn = self._empty
            self.error = self._empty
            self.enabled = self._empty
    
    
    def _empty(self, *args, **kwargs):
        return
    
    def debug(self, *args, **kwargs):
        if not self.defaults['debug']:
            self.debug = self._empty
            return
        date = "[]"
#        now = datetime.now()
#        date = now.strftime("%m/%d/%y %H:%M:%S:") + str(now.microsecond)[:3]
        output = date + ' ' + 'DEBUG  ' + self.name + "\t" + "".join([str(i) for i in args]) + '\n'
        
        if kwargs.get('tb', False):
            exception, instance, tb = traceback.sys.exc_info()
            output += "".join(traceback.format_tb(tb))
        if kwargs.get('stack', False):
            output += "".join(traceback.format_stack()[:-1])

        for logger in self.defaults['debug']:
            logger.log(output)
      
      
    
    def access(self, item, *args, **kwargs):
        if not self.defaults['access']:
            self.access= self._empty
            return
        date = "[]"
#        now = datetime.now()
#        date = now.strftime("%m/%d/%y %H:%M:%S:") + str(now.microsecond)[:3]
        output = date + ' ' + 'ACCESS ' + item + "\t" + "".join([str(i) for i in args]) + '\n'
        
        if kwargs.get('tb', False):
            exception, instance, tb = traceback.sys.exc_info()
            output += "".join(traceback.format_tb(tb))
        if kwargs.get('stack', False):
            output += "".join(traceback.format_stack()[:-1])
        
        for logger in self.defaults['access']:
            logger.log(output)
      
    def warn(self, *args, **kwargs):
        now = datetime.now()
        date = "[]"
#        now = datetime.now()
#        date = now.strftime("%m/%d/%y %H:%M:%S:") + str(now.microsecond)[:3]
        output = date + ' ' + 'WARN   ' + self.name + "\t" + "".join([str(i) for i in args]) + '\n'
        
        if kwargs.get('tb', False):
            exception, instance, tb = traceback.sys.exc_info()
            output += "".join(traceback.format_tb(tb))
        if kwargs.get('stack', False):
            output += "".join(traceback.format_stack()[:-1])
        
        for logger in self.defaults['warn']:
            logger.log(output)
      
    def info(self, *args, **kwargs):
        if not self.defaults['info']:
            self.info= self._empty
            return
      
        date = "[]"
#        now = datetime.now()
#        date = now.strftime("%m/%d/%y %H:%M:%S:") + str(now.microsecond)[:3]
        output = date + ' ' + 'INFO   ' + self.name + "\t" + "".join([str(i) for i in args]) + '\n'
        
        if kwargs.get('tb', False):
            exception, instance, tb = traceback.sys.exc_info()
            output += "".join(traceback.format_tb(tb))
        if kwargs.get('stack', False):
            output += "".join(traceback.format_stack()[:-1])
        
        for logger in self.defaults['info']:
            logger.log(output)
      
      
      
    def error(self, *args, **kwargs):
        date = "[]"
#        now = datetime.now()
#        date = now.strftime("%m/%d/%y %H:%M:%S:") + str(now.microsecond)[:3]
        output = date + ' ' + 'ERROR  ' + self.name + "\t" + "".join([str(i) for i in args]) + '\n'
        
        if kwargs.get('tb', False):
            exception, instance, tb = traceback.sys.exc_info()
            output += "".join(traceback.format_tb(tb))
        if kwargs.get('stack', False):
            output += "".join(traceback.format_stack()[:-1])
        
        for logger in self.defaults['error']:
            logger.log(output)

class ScreenLog(object):
    def __init__(self):
        pass
    
    def log(self, data):
        sys.stdout.write(data)

    def open(self):
        pass
    
    def flush(self):
        pass
    
    def close(self):
        pass
    
    
class FileLog(object):
    def __init__(self, filename):
        self.filename = filename
        self.f = None
    
    def log(self, data):
        self.f.write(data)

    def open(self):
        self.f = open(self.filename, 'a')
    
    def flush(self):
        self.f.flush()
    
    def close(self):
        self.f.close()
