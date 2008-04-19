from orbited.network.http import HTTPServer
import mimetypes, os

# Note, this is a twisted port of static handling code for dez. Its not a good fit
# for twisted though, and really needs to be rewritten, particularly the static
# content handler. We need to use registerProducer stuff from twisted to make 
# streaming work.

BUFFER_SIZE = 400096 # TODO: use the registerProducer B.S from twisted for file streaming

class OrbitedHTTPDaemon(HTTPServer):
  
    def __init__(self, app):
#        HTTPServer.__init__(self)
        self.app = app
        self.static = StaticHandler('Orbited')
    def dispatch_request(self, request):
        if request.url.startswith('/_/static/'):
            return self.static(request, '/_/static/', os.path.join(os.path.split(__file__)[0], 'static'))
        elif request.url == "/tcp":
            if request.method == "PUT":
                return self.app.tcp.put(request)
        elif request.url.startswith("/tcp/"):
            id = request.url.split('?', 1)[0].rsplit('/', 1)[1]
            print id
            request.form['id'] = id
            if request.method == "GET":
                return self.app.tcp.get(request)
            if request.method == "POST":
                return self.app.tcp.post(request)
            if request.method == "DELETE":
                return self.app.tcp.delete(request)
        request.error("404")
       
class StaticHandler(object):
    def __init__(self, server_name):
        self.server_name = server_name
        self.cache = NaiveCache()

    def __call__(self, req, prefix, directory):
        path = os.path.join(directory, req.url[len(prefix):])
        if os.path.isdir(path):
            url = req.url
            if url.endswith('/'):
                url = url[:-1]
            response = req.HTTPResponse()
            response.headers['Server'] = self.server_name
            response.write('<b>%s</b><br><br>'%url)
            response.write("<a href=%s>..</a><br>"%os.path.split(url)[0])
            for child in os.listdir(path):
                response.write("<a href=%s/%s>%s</a><br>"%(url,child,child))
            return response.dispatch()
        self.cache.get(req, path, self.__write, self.__stream, self.__404)

    def __write(self, req, path):
        response = req.HTTPResponse()
        response.headers['Server'] = self.server_name
        response.headers['Content-type'] = self.cache.get_type(path)
        response.write(self.cache.get_content(path))
        response.dispatch()

    def __stream(self, req, path):
        response = req.HTTPVariableResponse()
        response.headers['Server'] = self.server_name
        response.headers['Content-type'] = self.cache.get_type(path)
        self.__write_file(response, open(path), path)

    def __404(self, req):
        response = req.HTTPResponse()
        response.headers['Server'] = self.server_name
        response.status = '404 Not Found'
        response.write("<b>404</b><br>Requested resource \"<i>%s</i>\" not found" % req.url)
        response.dispatch()


    def __write_file(self, response, openfile, path):
        data = openfile.read(BUFFER_SIZE)
#        if data == "":
#            print 'data is empty'
#            return response.end()
        self.cache.add_content(path, data)
        def cb(arg):
            self.__write_file(response, openfile, path)
        response.write(data)
        response.flush()
        return response.end()
#        print d
#        d.addCallback(cb)


class BasicCache(object):
    def __init__(self):
        self.cache = {}

    def _mimetype(self, url):
        mimetype = mimetypes.guess_type(url)[0]
        if not mimetype:
            mimetype = "application/octet-stream"
        return mimetype

    def get_type(self, path):
        return self.cache[path]['type']

    def get_content(self, path):
        return self.cache[path]['content']

    def add_content(self, path, data):
        self.cache[path]['content'] += data

    def get(self, req, path, write_back, stream_back, err_back):
        if self._is_current(path):
            return write_back(req, path)
        if os.path.isfile(path):
            self._new_path(path, req.url)
            return stream_back(req, path)
        err_back(req)

class NaiveCache(BasicCache):
    def _is_current(self, path):
        return path in self.cache and self.cache[path]['mtime'] == os.path.getmtime(path)

    def _new_path(self, path, url):
        self.cache[path] = {'mtime':os.path.getmtime(path),'type':self._mimetype(url),'content':''}
