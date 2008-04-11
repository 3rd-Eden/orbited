import os
from orbited.json import json
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

    def get_plugins(self, req):
        req.write(json.encode([[True,"plugin manager ready"],["%s.%s"%key for key in self.plugins.keys()]]))
        req.close()

    def setup(self):
        self.dispatcher.add_cb_rule("/_/manage/get_plugins", self.get_plugins)
        for key, val in [(key, val) for key, val in map.items() if key.startswith('[plugin:')]:
            pl_name = key[8:-1]
            try:
                pl_module = __import__("%s.main"%pl_name,fromlist=[pl_name])
                log.info('Successfully imported plugin module: "%s"'%pl_name)
            except ImportError:
                log.error('Error importing plugin module: "%s"'%pl_name)
                continue
            self.dispatcher.add_static_rule("/"+pl_name+"/static/", (os.path.join(os.path.dirname(pl_module.__file__), 'static')))
            log.info('Registering statics: "/%s/static/"'%pl_name)
            for pl_class in [i.__name__ for i in [getattr(pl_module,z) for z in dir(pl_module)] if hasattr(i,'__bases__') and Plugin in i.__bases__]:
                log.info('Importing class: "%s.%s"'%(pl_name,pl_class))
                self.plugins[(pl_name,pl_class.lower())] = getattr(pl_module,pl_class)(pl_name, pl_module, self.dispatcher, active=val.get('active',0))

class PluginMeta(type):
    def __init__(cls, name, bases, dct):
        if name != "Plugin":
            old__init__ = cls.__init__
            def new__init__(self, name, module, app, active):
                Plugin.__init__(self, name, module, app, active)
                if Plugin.__init__ != old__init__:
                    old__init__(self)
            cls.__init__ = new__init__

class Plugin(object):
    __metaclass__ = PluginMeta
    def __init__(self, name, module, app, active):
        self.__active = False
        self.__name = name + "." + self.__class__.__name__
        if active:
            self.__active = True
        path = "/"+name+"/"+self.__class__.__name__.lower()
        log.info('Registering path: "%s"'%path)
        app.add_cb_rule(path+"/manage/start", self.__start)
        app.add_cb_rule(path+"/manage/stop", self.__stop)
        app.add_cb_rule(path+"/manage/status", self.__status)
        app.add_cb_rule(path+"/",self.__404)
        for key in [key for key,val in self.__class__.__dict__.items() if hasattr(val,'_exposed')]:
            cb = self.__dispatch(key)
            app.add_cb_rule(path+"/"+key,cb)
            if key == "index":
                app.add_cb_rule(path,cb)

    def __dispatch(self, func):
        def cb(req):
            if self.__active:
                return getattr(self,func)(req)
            self.__404(req)
        return cb

    def __404(self, req):
        req.write("404")
        req.close()

    def __start(self, req):
        if self.__active:
            response = [False, "%s already started"%self.__name]
        else:
            self.__active = True
            response = [True, "%s started"%self.__name]
        req.write(json.encode(response))
        req.close()

    def __stop(self, req):
        if self.__active:
            self.__active = False
            response = [True, "%s stopped"%self.__name]
        else:
            response = [False, "%s already stopped"%self.__name]
        req.write(json.encode(response))
        req.close()

    def __status(self, req):
        response = [True,"%s status: stopped"%self.__name]
        if self.__active:
            response[1] = "%s status: started"%self.__name
        req.write(json.encode(response))
        req.close()
