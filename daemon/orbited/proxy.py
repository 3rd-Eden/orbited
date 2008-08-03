from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol

from orbited import config
from orbited import logging

ERRORS = {
    'InvalidHandshake': 102,
    'RemoteConnectionTimeout': 104,
    'Unauthorized': 106,
}

class ProxyIncomingProtocol(Protocol):
    """
    Handles the protocol between the browser and orbited, and proxies
    the data to a backend server.
    """

    logger = logging.get_logger('orbited.proxy.ProxyIncomingProtocol')

    def connectionMade(self):
        self.logger.debug("connectionMade")
        self.state = 'handshake'
        self.binary = False
        # TODO rename this to outgoingProtocol
        self.otherConn = None

    def dataReceived(self, data):
        self.logger.debug('dataReceived: data=%r' % data)
        if self.otherConn:
            # NB: otherConn is-a ProxyOutgoingProtocol
            # TODO honour self.binary by actually decoding data into binary.
            return self.otherConn.transport.write(data)            
        if self.state == "handshake":
            # NB: we can safely process data here in one read because
            #     the first chunk of data from the browser will include
            #     the full data.
            # TODO: though, we might get busted if the client sends data
            #       imediately, maybe we should end the data with \n?
            #       OR maybe the router in the middle truncated data.
            #       UNLESS we can make sure the creation happens in a
            #       single POST.
            try:
                # XXX altough this gets saved, self.binary is not
                #     actually used from browser to backend, so the
                #     binary sockets are currently broken.
                self.binary = (data[0] == '1')
                host, port = data[1:].split(':')
                port = int(port)
            except:
                self.logger.error("failed to connect on handshake", tb=True)
                self.transport.write("0" + str(ERRORS['InvalidHandshake']))
                self.transport.loseConnection()
                return
            peer = self.transport.getPeer()
            if (host, port) not in config.map['[access]']:
                self.logger.warn('Unauthorized connect from %r:%d to %r:%d' % (peer.host, peer.port, host, port))
                self.transport.write("0" + str(ERRORS['Unauthorized']))
                self.transport.loseConnection()
                return
            self.logger.access('new connection from %s:%s to %s:%d' % (peer.host, peer.port, host, port))
            self.state = 'connecting'
            client = ClientCreator(reactor, ProxyOutgoingProtocol, self)
            client.connectTCP(host, port)
                # TODO: connect timeout or onConnectFailed handling...
        else:
            self.transport.write("0" + str(ERRORS['InvalidHandshake']))            
            self.state = 'closed'
            self.transport.loseConnection()

    def connectionLost(self, reason):
        self.logger.debug("connectionLost %s" % reason)
        if self.otherConn:
            self.otherConn.transport.loseConnection()

    # XXX the wording is confusing;  shouldn't this be called
    #     outgoingConnectionEstablished?  dito for remoteConnectionLost.
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
    """
    Handles the protocol between orbited and backend server.
    """

    logger = logging.get_logger('orbited.proxy.ProxyOutgoingProtocol')

    def __init__(self, otherConn):
        # TODO rename this to incomingProtocol
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

