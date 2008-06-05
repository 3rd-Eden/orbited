#import sse
#import htmlfile
import xhrstream

transports = {
    'xhrstream': xhrstream.XHRStreamingTransport,
}
def create(request):
    transport_name = request.args.get('transport', ['xhrstream'])[0]
    x = transports[transport_name]
    return x(request)

