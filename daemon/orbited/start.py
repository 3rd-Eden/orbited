import sys
import os
from twisted.internet import reactor, ssl
from twisted.web import server, resource, static
from logger import get_logger
from config import map as config
#from revolved import RevolvedConnection
logger = get_logger('Daemon')
root = resource.Resource()
static_files = static.File(os.path.join(os.path.split(__file__)[0], 'static'))
root.putChild('static', static_files)
site = server.Site(root)


def main():
    from echo import EchoFactory
    from proxy import SimpleProxyFactory
#    from jsonproxy import JsonProxyFactory
    from binaryproxy import BinaryProxyFactory
    from websocket import WebSocketFactory
    root.putChild('echo', EchoFactory())
    root.putChild('proxy', SimpleProxyFactory())
    root.putChild('binaryproxy', BinaryProxyFactory())
    root.putChild('websocket', WebSocketFactory())
    port = int(config['[global]']['http.port'])
    logger.info('Listening HTTP@%s' % port)
    reactor.listenTCP(port, site)
    # Listen on SSL port
#    reactor.listenSSL(8043, site, ssl.DefaultOpenSSLContextFactory("orbited.key", "orbited.crt"))
    reactor.run()


if __name__ == "__main__":
    main()