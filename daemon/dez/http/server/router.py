class Router(object):
    def __init__(self, default_cb):
        self.default_cb = default_cb
        self.prefixes = []
        
    def register_prefix(self, prefix, cb):
        self.prefixes.append((prefix, cb))
        
    def __call__(self, url):
        for prefix, cb in self.prefixes:
            if url.startswith(prefix):
                return cb
        return self.default_cb
    
    