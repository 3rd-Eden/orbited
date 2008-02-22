from orbited.config import map

class PluginManager(object):
  
    def __init__(self):
        self.plugins = {}
        self.setup()
        
        
    def setup(self):
        """ check the configuration for plugins to load
            register each the router if enabled.
            perhaps give the router to each plugin when it loads
            it can then register or unregister routing rules.
        """
        
        
class PluginMeta(type):
    pass        

class Plugin(object):
    __metaclass__ = PluginMeta
    def request(req):
        pass
    