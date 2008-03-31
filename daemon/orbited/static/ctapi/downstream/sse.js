if (typeof(CTAPITransports) == "undefined")
    CTAPITransports = { 
        downstream: { },
        upstream: { }
    }
CTAPITransports['downstream']['sse'] = function() {
    var self = this;
    self.url = null;
    self.cb = null;

    self.connect = function(cb, identifier, host, port, location) {
        self.cb = cb
        if (typeof(host) == "undefined")
            host = document.domain
        if (typeof(port) == "undefined")
            port = location.port
        if (port == "")
            port = 80
        if (typeof(location) == "undefined")
            location = "/"
        // TODO: use a real random id
        self.url = 'http://' + host + ':' + port + location +'?transport=sse'
        if (identifier !== null)
            self.url += "&identifier=" + identifier
        
        var es = document.createElement('event-source');
        es.setAttribute('src', this.url);
        document.body.appendChild(es);
        
        es.addEventListener('orbited', function (event) {
            var data = eval(event.data);
            if (typeof data !== 'undefined') {
                self.cb(data);
            }
        }, false);
    }
}