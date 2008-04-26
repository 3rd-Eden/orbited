from twisted.web import server, resource, static
from twisted.internet import reactor

class OrbitedRoot(resource.Resource):
#    isLeaf = True
    def __init__(self):
        system = resource.Resource()
        self.putChild('_', system)
        system.putChild('static', static.File(os.path.join(os.path.split(__file__)[0], 'static')))
        
    def render_GET(self, request):
        return "<html>Hello, world!</html>"

