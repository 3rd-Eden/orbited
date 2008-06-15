#import sse
#import htmlfile
import xhrstream
import htmlfile
import sse
transports = {
    'xhrstream': xhrstream.XHRStreamingTransport,
    'htmlfile': htmlfile.HTMLFileTransport,
    'sse': sse.SSETransport
}
def create(request):
    transport_name = request.args.get('transport', ['xhrstream'])[0]
    x = transports[transport_name]
    return x(request)

