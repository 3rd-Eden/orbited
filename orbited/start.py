import sys
import os
from twisted.internet import reactor
from twisted.web import server, resource, static
#from revolved import RevolvedConnection

root = resource.Resource()
system = resource.Resource()
root.putChild('_', system)
static_files = static.File(os.path.join(os.path.split(__file__)[0], 'static'))
system.putChild('static', static_files)
site = server.Site(root)


def main():
    from echo import EchoFactory
    from proxy import SimpleProxyFactory
    from jsonproxy import JsonProxyFactory
    from stock import StockFactory
    root.putChild('echo', EchoFactory())
    root.putChild('proxy', SimpleProxyFactory())
    root.putChild('jsonproxy', JsonProxyFactory())
    root.putChild('stock', StockFactory())
    try:
        port = int(sys.argv[1])
    except:
        port = 7000
    reactor.listenTCP(port, site)
    reactor.run()

if __name__ == "__main__":
    main()