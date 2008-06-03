import sse
import htmlfile
transports = {
    'sse': sse.SSEConnection,
    'htmlfile': htmlfile.HTMLFileConnection
}
def create(request):
    transport_name = request.args.get('transport', ['sse'])[0]
    x = transports[transport_name]
    return x(request)

