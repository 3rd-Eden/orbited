from twisted.internet import reactor
from twisted.web import server, resource
from echo import EchoFactory
#from revolved import RevolvedConnection

def main():
    root = resource.Resource()
    root.putChild('echo', EchoFactory())
#    root.putChild('revolved', TCPConnectionResource(RevolvedConnection))
    site = server.Site(root)
    reactor.listenTCP(7000, site)
    reactor.run()

if __name__ == "__main__":
    main()