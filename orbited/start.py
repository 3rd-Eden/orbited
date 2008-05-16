import os
from twisted.internet import reactor
from twisted.web import server, resource, static
from echo import EchoFactory
from html5 import SimpleProxyFactory

#from revolved import RevolvedConnection

def main():
    root = resource.Resource()
    root.putChild('echo', EchoFactory())
    root.putChild('proxy', SimpleProxyFactory())
    sys = resource.Resource()
    root.putChild('_', sys)
    static_files = static.File(os.path.join(os.path.split(__file__)[0], 'static', 'build'))
    sys.putChild('static', static_files)
    site = server.Site(root)
    reactor.listenTCP(7000, site)
    reactor.run()

if __name__ == "__main__":
    main()