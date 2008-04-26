from tcp import TCPHandlerResource
from twisted.web import server, resource, static
from twisted.internet import reactor
import os




class OrbitedRoot(resource.Resource):
#    isLeaf = True
    def __init__(self, protocol):
        resource.Resource.__init__(self)
        tcp = TCPHandlerResource(protocol)
        self.putChild('tcp', tcp)
#        self.putChild('', self)
        
    def render(self, request):
        print '!'
        """Render a given resource. See L{IResource}'s render method.

        I delegate to methods of self with the form 'render_METHOD'
        where METHOD is the HTTP that was used to make the
        request. Examples: render_GET, render_HEAD, render_POST, and
        so on. Generally you should implement those methods instead of
        overriding this one.

        render_METHOD methods are expected to return a string which
        will be the rendered page, unless the return value is
        twisted.web.server.NOT_DONE_YET, in which case it is this
        class's responsibility to write the results to
        request.write(data), then call request.finish().

        Old code that overrides render() directly is likewise expected
        to return a string or NOT_DONE_YET.
        """
        return "Hello There"
    
#    def getChildWithDefault(self, pathEl, request):
#        x = resource.Resource.getChildWithDefault(self, pathEl, request)
#        print 'pathEl', pathEl.__class__
#        print 'request', request
#        print 'url', request.URLPath()
#        print 'return', x
#        return x
    
    def render_GET(self, request):
        return "<html>Hello, world!</html>"


    
