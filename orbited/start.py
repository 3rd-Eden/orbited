import sys
import os
from twisted.internet import reactor
from twisted.web import server, resource, static
from echo import EchoFactory
from proxy import SimpleProxyFactory
from jsonproxy import JsonProxyFactory

#from revolved import RevolvedConnection

def main():
    root = resource.Resource()
    root.putChild('echo', EchoFactory())
    root.putChild('proxy', SimpleProxyFactory())
    root.putChild('jsonproxy', JsonProxyFactory())
    system = resource.Resource()
    root.putChild('_', system)
    static_files = static.File(os.path.join(os.path.split(__file__)[0], 'static'))
    system.putChild('static', static_files)
    site = server.Site(root)
    try:
      
        port = int(sys.argv[1])
    except:
        raise
        port = 80
    reactor.listenTCP(port, site)
    reactor.run()

if __name__ == "__main__":
    main()