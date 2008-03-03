class JsonHolder(object):
    pass
json = JsonHolder()
try:
    import cjson
    print "json handler: cjson"
    json.encode = cjson.encode
    json.decode = cjson.decode
except ImportError:
    try:
        import simplejson
        print "json handler: simplejson"
        json.encode = simplejson.dumps
        json.decode = simplejson.loads
    except ImportError:
        import demjson
        print "json handler: demjson"
        json.encode = demjson.encode
        json.decode = demjson.decode
