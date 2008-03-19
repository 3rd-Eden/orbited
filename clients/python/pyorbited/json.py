"""
Select a JSON library from any of several known libraries.
"""

class JsonHolder(object):
    pass

json = JsonHolder()

try:
    import cjson
    json.encode = cjson.encode
    json.decode = cjson.decode
except ImportError:
    try:
        import simplejson
        json.encode = simplejson.dumps
        json.decode = simplejson.loads
    except ImportError:
        import demjson
        json.encode = demjson.encode
        json.decode = demjson.decode
