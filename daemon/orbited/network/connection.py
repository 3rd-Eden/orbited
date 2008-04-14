from buffer import Buffer
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import defer

class StructuredReader(Protocol):
    
    def __init__(self):
        self.data = Buffer()
        self.rmode = None
    def dataReceived(self, data):
        self.data += data
        self.process()
        
    def process(self):
        while self.rmode:
            current_rmode = self.rmode
            rmode = self.rmode[0]
            args = self.rmode[1:]
            completed = getattr(self, 'rmode_%s' % rmode)(*args)
            # If we completed and no new rmode was set, then stop looping
            if self.rmode is current_rmode and completed:
                self.rmode = None # break out of loop
            # Stop the loop until more data is received
            elif not completed:
                break
    
    def rmode_size(self, size, d):
        if size > len(self.data):
            return False
        payload = self.data.part(0, size)
        self.data.move(size)
        d.callback(payload)
        return True
    
    def rmode_delimiter(self, delimiter, d):
        i = self.data.find(delimiter)
        if i == -1:
            return False
        payload = self.data.part(0, i)
        self.data.move(i+len(delimiter))
        d.callback(payload)
        return True
    
    def set_rmode_size(self, size):
        d = defer.Deferred()
        self.rmode = ('size', size, d)
        return d
    
    
    def set_rmode_delimiter(self, delimiter):
        d = defer.Deferred()
        self.rmode = ('delimiter', delimiter, d)
        return d



# Next lines are magic:
if __name__ == "__main__":
    from twisted.internet import reactor
    
    class TestReader(StructuredReader):
        
        def connectionMade(self):
            d = self.set_rmode_size(20)
            def woot(data):
                print 'received:', data
                reactor.stop()
            d.addCallback(woot)
    factory = Factory()
    factory.protocol = TestReader
    
    # 8007 is the port you want to run under. Choose something >1024
    reactor.listenTCP(8007, factory)
    reactor.run()
