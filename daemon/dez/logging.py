
class FakeLogger(object):
    def debug(self, *args, **kwargs):
        pass
    info = debug
    acess = debug
    warn = debug
    error = debug
    
logger = FakeLogger()

def default_get_logger(name):
    return logger
