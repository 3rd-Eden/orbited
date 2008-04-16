import os, pkg_resources
from dez.http.server import HTTPResponse
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

    def index(self, req):
        req.write("<html><head><title>Manage Plugin</title><link rel=stylesheet href=/_/static/manage.css><script src=/_/static/manage.js></script><script src=/_/static/library.js></script><script>Plugin = new Library('/_/manage/');</script></head><body onload='Plugin.get(\"get_plugins\",Manager.load);'><h1>Orbited<span>Plugin</span>: <b id=name></b></h1><div class=section><h4>Active Plugins</h4><div id=plugins></div></div><div class=section><h4>Last Output <b id=flag></b></h4><div id=output></div></div><div class=section><h4>Available Functions</h4><div id=functions></div></div></body></html>")
        req.close()

    def get_plugins(self, req):
        req.write(json.encode([[True,"plugin manager ready"],[key for key in self.plugins.keys()]]))
        req.close()

    def setup(self):
        self.dispatcher.add_cb_rule("/_/manage",self.index)
        self.dispatcher.add_cb_rule("/_/manage/get_plugins", self.get_plugins)
        for plugin_entry in pkg_resources.iter_entry_points('orbited.plugins'):
            plugin = None
            try:
                plugin = plugin_entry.load()
                plugin._name = str(plugin_entry).split("=")[0].strip()
                self.plugins[plugin._name] = plugin(self.dispatcher)
            except:
                log.error("Couldn't load \"%s\"" % plugin_entry.name,exc_info=True)

class PluginMeta(type):
    def __init__(cls, name, bases, dct):
        if name != "Plugin":
            old__init__ = cls.__init__
            def new__init__(self, app):
                Plugin.__init__(self, app)
                if Plugin.__init__ != old__init__:
                    old__init__(self)
            cls.__init__ = new__init__

class Plugin(object):
    __metaclass__ = PluginMeta
    def __init__(self, app):
        self.__active = map.get('[plugin:%s]'%self._name,{}).get('active',0)
        log.info('Registering path: "/_/%s"'%self._name)
        app.add_cb_rule("/_/%s/manage/start"%self._name, self.__start)
        app.add_cb_rule("/_/%s/manage/stop"%self._name, self.__stop)
        app.add_cb_rule("/_/%s/manage/status"%self._name, self.__status)
        app.add_cb_rule("/_/%s/"%self._name, self.__404)
        if hasattr(self,'static'):
            static_path = "/_/"+self._name+"/static/"
            app.add_static_rule(static_path, self.static)
            log.info('Static dir: "' + static_path + '" -> "' + self.static + '"')
            index_path = os.path.join(self.static,'index.html')
            if os.path.isfile(index_path) and not hasattr(self,'index'):
                f = open(index_path)
                self.__index_file = f.read()
                f.close()
                app.add_cb_rule("/_/%s"%self._name,self.__dispatch('_index'))
        for key in [key for key,val in self.__class__.__dict__.items() if hasattr(val,'_exposed')]:
            cb = self.__dispatch(key)
            app.add_cb_rule("/_/%s/%s"%(self._name,key),cb)
            if key == "index":
                app.add_cb_rule("/_/%s"%self._name,cb)

    def _index(self, req):
        response = HTTPResponse(req)
        response.headers['Content-type'] = "text/html"
        response.write(self.__index_file)
        response.dispatch()

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
            response = [False, "%s already started"%self._name]
        else:
            self.__active = True
            response = [True, "%s started"%self._name]
        req.write(json.encode(response))
        req.close()

    def __stop(self, req):
        if self.__active:
            self.__active = False
            response = [True, "%s stopped"%self._name]
        else:
            response = [False, "%s already stopped"%self._name]
        req.write(json.encode(response))
        req.close()

    def __status(self, req):
        response = [True,"%s status: stopped"%self._name]
        if self.__active:
            response[1] = "%s status: started"%self._name
        req.write(json.encode(response))
        req.close()
