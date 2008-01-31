from orbited.logger import get_logger

log = get_logger("HTTPDaemon")

class HTTPDaemon(object):
    
    def __init__(self, server, port):
        log.info("Listening on %s:%s" % (server, port))
        pass
    
    
    
    
    def register(self, rule, cb):
        pass
    
    
    
    
    


class HTTPRawResponse(object):
    pass


class HTTPDynamicResponse(object):
    pass