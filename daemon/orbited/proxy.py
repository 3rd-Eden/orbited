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
        # TODO: add handshake timer
        self.logger.debug("connectionMade")
        self.state = 'handshake'
        self.binary = False
        # TODO rename this to outgoingProtocol
        self.outgoingConn = None
        self.buffer = ""
        
    def dataReceived(self, data):
        self.logger.debug('dataReceived: data=%r' % data)
        self.logger.debug('self.outgoingConn is', self.outgoingConn)
        self.logger.debug('self.binary', self.binary)
        self.buffer += data
        if self.outgoingConn:
            # NB: otherConn is-a ProxyOutgoingProtocol
            if self.binary:
                # NOTE: This is not *strictly* necessary because we know that
                #       each send is framed by the HTTP POST request. No need
                #       for the \n, except then we'd be violating the 
                #       funtionality implied by the ITransport interface.
                binaryBuffer = []
                while True:
                    i = self.buffer.find('\n')
                    if i == -1:
                        break
                    self.logger.debug('found \\n')
                    data = self.buffer[:i]
                    self.buffer = self.buffer[i+i:]
                    binaryBuffer.extend([ int(b) for b in data.split(',') ])
                if binaryBuffer:
                    data = "".join([chr(b) for b in binaryBuffer])
                else:
                    return
            else:
                self.buffer = ""
            self.logger.debug("write (out):", data)
            return self.outgoingConn.transport.write(data)
        if self.state == "handshake":
            i = self.buffer.find('\n')
            if i == -1:
                return
            data = self.buffer[:i]
            self.buffer = self.buffer[i+1:]
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
        if self.outgoingConn:
            self.outgoingConn.transport.loseConnection()

    # XXX the wording is confusing;  shouldn't this be called
    #     outgoingConnectionEstablished?  dito for remoteConnectionLost.
    def outgoingConnectionEstablished(self, outgoingConn):
        if self.state == 'closed':
            return outgoingConn.transport.loseConnection()
        self.outgoingConn = outgoingConn
        self.transport.write('1')
        self.state = 'proxy' # Not really necessary...
        
    def outgoingConnectionLost(self, outgoingConn, reason):
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

    def __init__(self, incomingConn):
        # TODO rename this to incomingProtocol
        self.incomingConn = incomingConn

    def connectionMade(self):
        self.incomingConn.outgoingConnectionEstablished(self)

    def dataReceived(self, data):
        self.logger.debug("dataReceived %r" % data)
        self.incomingConn.write(data)

    def connectionLost(self, reason):
        self.incomingConn.outgoingConnectionLost(self, reason)

class ProxyFactory(Factory):

    protocol = ProxyIncomingProtocol

