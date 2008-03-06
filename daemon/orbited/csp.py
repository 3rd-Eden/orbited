#from orbited.router import router, CSPDestination
from orbited.http import HTTPRequest

#router.register(CSPDestination, '/_/csp')
#router.register(StaticDestination, '/_/csp/static', '[orbited-static]')


class CSP(object):
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
    
    def http_request(self, request):
        request = HTTPRequest(request)
        junk, method = request.url.rsplit('/', 1)
        if not hasattr(self, method):
            return request.error("Invalid Method")
        response = request.HTTPResponse()
        return getattr(self, method)(request, response)
    
    def contains(self, key):
        return False


    def signon(self, request, response):
        response.write("CSP Hello World")
        response.dispatch()


