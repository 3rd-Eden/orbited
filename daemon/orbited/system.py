import sys
from orbited import __version__
from dez.http.server import HTTPResponse


class System(object):
  
    def http_request(self, req):
        # remove "/_/" part of url
        action = req.url[3:]
        if hasattr(self, action):
            return getattr(self, action)(req)
        else:
            req.error("Not Found", code="404",
                "Could not find req.url.")
  
    def about(self, req):
        print __version__
        print sys.version
        response = HTTPResponse(req)
        response.write("""<!DOCTYPE HTML>
        <html>
          <head>
            <link rel="stylesheet" type="text/css" href="/_/static/orbited.css">
            <meta charset="utf-8">
            <title>Orbited %s</title>
          </head>
          <body>
            <h1>Orbited %s</h1>
            <p>
              Python %s on %s
            </p>
          </body>
        </html>
        """ % (__version__, __version__, sys.version.replace('\n', '<br>\r\n'), sys.platform))
        response.dispatch()
      