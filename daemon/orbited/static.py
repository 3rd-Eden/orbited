import sys

about_content = """
<html>
 <head>
  <title>Orbited 0.1.3</title>
 </head>
 <body>
  <h1>Orbited 0.1.3</h1>
  Python %s
 </body>
</html>""" % sys.version

header = """HTTP/1.0 200 OK
Connection: close
Content-Type: text/html
Content-Length: %s

"""

test_content = "This is a test!"

about = header % len(about_content)+ about_content
test = header % len(test_content) + test_content


