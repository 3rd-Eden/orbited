import rel as event
import sys
engine = "pyevent"
if len(sys.argv) > 1:
    engine = sys.argv[1]
event.initialize([engine])
port = 8888
if len(sys.argv) > 2:
    port = int(sys.argv[2])

from dez import HTTPDaemon, HTTPResponse, RawHTTPResponse

def test_dispatch(request):
    # Very raw way
    request.write("HTTP/1.0 200 OK\r\nContent-type: text/html\r\nContent-length: 10\r\n\r\nAloha des!", None)
    request.close()
    
    # HTTPReponse method
#    r = HTTPResponse(request)
#    r.write('Aloha Des!!')
#    r.dispatch()

    # RawHTTPResponse method

#    r = RawHTTPResponse(request)
#    r.write_status(200, "OK")
#    r.write_header("good", "day")
#    r.write_header("Content-length", 10)
#    r.write_headers_end()
#    r.write('Aloha Des!')
#    r.close()

def noop():
    return True

def main():
    httpd = HTTPDaemon("127.0.0.1", port)
    httpd.register_prefix("/index", test_dispatch)
    event.timeout(1, noop)
    event.dispatch()

def profile():
    import hotshot
    prof = hotshot.Profile("orbited_http_test.profile")
    prof.runcall(main)
    prof.close()