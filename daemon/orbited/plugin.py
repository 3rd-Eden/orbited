from orbited.config import map
from orbited.logger import get_logger
log = get_logger("plugin")

def exposed(func):
    func._exposed = True
    return func

class PluginManager(object):
    def __init__(self, dispatcher):
        self.plugins = {}
        self.dispatcher = dispatcher
        self.setup()

    def setup(self):
        for key, val in map.items():
            if key.startswith('[plugin:'):
                plugin_name = key[8:-1]
                try:
                    plug = __import__("%s.main"%plugin_name,fromlist=[plugin_name])
                    log.info('Successfully imported plugin module: "%s"'%plugin_name)
                except ImportError:
                    log.error('Error importing plugin module: "%s"'%plugin_name)
                    continue
                # TODO instead of calling Main(), figure out how
                # to view all classes defined in file, and use any
                # class that inherits from Plugin
                # (so you can define multiple classes in one file)
                self.plugins[plugin_name] = plug.Main(self.dispatcher)
                if 'active' in val and val['active']:
                    self.plugins[plugin_name]._activate()

class PluginMeta(type):
    def __init__(cls, name, bases, dct):
        if name != "Plugin":
            old__init__ = cls.__init__
            def new__init__(self, app):
                Plugin.__init__(self, app)
                old__init__(self)
            cls.__init__ = new__init__

class Plugin(object):
    __metaclass__ = PluginMeta
    def __init__(self, app):
        self.__app = app

    def __dispatch(self, func):
        def cb(req):
            getattr(self,func)(req)
        return cb

    def _activate(self):
        for key, val in self.__class__.__dict__.items():
            if hasattr(val,'_exposed'):
                self.__app.add_cb_rule("/"+key,self.__dispatch(key))
