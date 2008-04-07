import cherrypy
from client import OrbitClient
from orbited.json import json
#orbit = OrbitClient()
#orbit.connect()
#orbit.callback("signon", "http://localhost:4700/orbited_signon")
#orbit.callback("signoff", "http://localhost:4700/orbited_signoff")

class ChatServer(object):
#    i = 0
#    users = []
#    def user_keys(self):
#        return [u for u in self.users]
    
    
#    @cherrypy.expose
#    def orbited_signon(self, function, key):
#        if key not in self.users:
#            self.users.append(key)
#            orbit.send(self.user_keys(), '<b>%s joined</b>' % key)
            
#    @cherrypy.expose
#    def orbited_signoff(self, function, key):
#        if key in self.users:
#            self.users.remove(key)
#            orbit.send(self.user_keys(), '<b>%s has left</b>' % key)
            
            
    @cherrypy.expose
    def revolved_auth_channel(self, user_key):
        print 'user_key', user_key
        return json.encode(dict(publish=True, subscribe=True))
            
    @cherrypy.expose
    def revolved_auth_connect(self, user_key, auth_data):
      
        print "user_key", json.decode(user_key)
        print "auth_data", json.decode(auth_data)
        return json.encode('max' in user_key)
    
        
if __name__ == '__main__':
    import os
    # This code is straight from the cherrypy StaticContent wiki
    # which can be found here: http://www.cherrypy.org/wiki/StaticContent
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Set up site-wide config first so we get a log if errors occur.
    cherrypy.config.update({'environment': 'production',
                            'log.screen': True,
                            'server.socket_port': 4700,
                            'server.thread_pool': 0,
                            'tools.staticdir.root': current_dir})
        
    conf = {'/static': {'tools.staticdir.on': True,
                        'tools.staticdir.dir': 'static'}}
    cherrypy.quickstart(ChatServer(), '/', config=conf)
