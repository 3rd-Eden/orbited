from orbited.network.op import OPServer


class OrbitedOPDaemon(OPServer):
  
    def __init__(self, app):
        self.app = app
    
    def dispatch(self, request):
        self.app.tcp.send(request.recipient, request.payload)