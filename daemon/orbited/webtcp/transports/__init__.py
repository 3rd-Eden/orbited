import xhrstream
#import htmlfile
#import sse
transports = {
    'xhrstream': xhrstream.XHRStreamingTransport,
#    'htmlfile': htmlfile.HTMLFileTransport,
#    'sse': sse.SSETransport
}
def create(request):
    transport_name = request.args.get('transport', ['xhrstream'])[0]    
    x = transports.get(transport_name, None)
    if not x:
        return None
    return x(request)
