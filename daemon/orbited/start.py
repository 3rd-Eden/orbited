import urlparse
import sys
import os
from twisted.internet import reactor
from twisted.web import server, resource, static
from logger import get_logger
from config import map as config
#from revolved import RevolvedConnection
logger = get_logger('Daemon')
#if 'INDEX' in config['[static]']:
#    print 'index found', config['[static]']['INDEX']
#    root = static.File(config['[static]']['INDEX'])
#else:
root = resource.Resource()
static_files = static.File(os.path.join(os.path.split(__file__)[0], 'static'))
root.putChild('static', static_files)
site = server.Site(root)

def setup_static(taken):
    for key, val in config['[static]'].items():
        if key in taken:
            logger.error("cannot mount static directory with reserved name %s" % key)
            sys.exit(0)
        if key == 'INDEX':
            key = ''
        root.putChild(key, static.File(val))

def main():
    from echo import EchoFactory
    from proxy import SimpleProxyFactory
    from binaryproxy import BinaryProxyFactory
    from websocket import WebSocketFactory
    from dispatch import DispatchFactory
    root.putChild('echo', EchoFactory())
    root.putChild('proxy', SimpleProxyFactory())
    root.putChild('binaryproxy', BinaryProxyFactory())
    root.putChild('websocket', WebSocketFactory())
    if config['[global]']['dispatch.enabled'] == '1':
        root.putChild('legacy', DispatchFactory())
    setup_static(['echo', 'proxy', 'binaryproxy', 'websocket'])
    for addr in config['[listen]']:
        url = urlparse.urlparse(addr)
        hostname = url.hostname
        if hostname == None:
            hostname = ''
        if url.scheme == 'http':
            logger.info('Listening http@%s' % url.port)
            reactor.listenTCP(url.port, site, interface=hostname)
        elif url.scheme == 'https':
            from twisted.internet import ssl
            crt = config['[ssl]']['crt']
            key = config['[ssl]']['key']
            try:
                ssl_context = ssl.DefaultOpenSSLContextFactory(key, crt)
            except ImportError:
                raise
            except:
                logger.error("Error opening key or crt file: %s, %s" % (key, crt))
                sys.exit(0)
            logger.info('Listening https@%s (%s, %s)' % (url.port, key, crt))
            reactor.listenSSL(url.port, site, ssl_context)
        else:
            logger.error("Invalid Listen URI: %s" % addr)
            sys.exit(0)
    reactor.run()


if __name__ == "__main__":
    main()
