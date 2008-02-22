from orbited import __version__
from dez.http.server import HTTPResponse


class System(object):
  
    def about(self, req):
        response = HTTPResponse(req)
        response.write("""<!DOCTYPE HTML>
        <html>
          <head>
            <meta charset="utf-8">
            <title>Orbited 0.2.0</title>
          </head>
          <body>
            <h1>Orbited %s</h1>
            <p>
              Python %s on %s
            </p>
          </body>
        </html>
        """) % (__version__, sys.version.replace('\n', '<br>\r\n'), sys.platform)
        response.render()
      