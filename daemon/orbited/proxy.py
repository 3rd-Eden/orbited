from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol

from orbited import logging

ERRORS = {
    'InvalidHandshake': 102,
    'RemoteConnectionTimeout': 104
}

class ProxyIncomingProtocol(Protocol):

    logger = logging.get_logger('orbited.proxy.ProxyIncomingProtocol')

    def connectionMade(self):
        self.logger.debug("connectionMade")
        self.state = 'handshake'
        self.binary = False
        self.otherConn = None

    def dataReceived(self, data):
        if self.otherConn:
            return self.otherConn.transport.write(data)            
        if self.state == "handshake":
            try:
                self.binary = (data[0] == '1')
                hostname, port = data[1:].split(':')
                port = int(port)
                self.state = 'connecting'
                client = ClientCreator(reactor, ProxyOutgoingProtocol, self)
                client.connectTCP(hostname, port)
                self.logger.debug("connecting to %r:%d" % (hostname, port))
                # TODO: connect timeout or onConnectFailed handling...
            except:
                self.logger.error("failed to connect on handshake", tb=True)
                self.transport.write("0" + str(ERRORS['InvalidHandshake']))
                self.transport.loseConnection()
                raise
        else:
            self.transport.write("0" + str(ERRORS['InvalidHandshake']))            
            self.state = 'closed'
            self.transport.loseConnection()

    def connectionLost(self, reason):
        self.logger.debug("connectionLost %s" % reason)
        if self.otherConn:
            self.otherConn.transport.loseConnection()

    def remoteConnectionEstablished(self, otherConn):
        if self.state == 'closed':
            return otherConn.transport.loseConnection()
        self.otherConn = otherConn
        self.transport.write('1')
        self.state = 'proxy' # Not really necessary...
        
    def remoteConnectionLost(self, otherConn, reason):
        self.logger.debug("remoteConnectionLost %s" % reason)
        self.transport.loseConnection()

    def write(self, data):
        self.logger.debug("write %r" % data)
        # TODO: how about some real encoding, like base64, or even hex?
        if self.binary:
            data  = ",".join([ str(ord(byte)) for byte in data])
        self.transport.write(data)

class ProxyOutgoingProtocol(Protocol):

    logger = logging.get_logger('orbited.proxy.ProxyOutgoingProtocol')

    def __init__(self, otherConn):
        self.otherConn = otherConn

    def connectionMade(self):
        self.otherConn.remoteConnectionEstablished(self)

    def dataReceived(self, data):
        self.logger.debug("dataReceived %r" % data)
        self.otherConn.write(data)

    def connectionLost(self, reason):
        self.otherConn.remoteConnectionLost(self, reason)

class ProxyFactory(Factory):

    protocol = ProxyIncomingProtocol

