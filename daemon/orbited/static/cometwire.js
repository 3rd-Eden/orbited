Orbited.require("json.js")
Orbited.require("ctapi/upstream/xhr.js")
Orbited.require("ctapi/downstream/all.js")

if (typeof(CTAPITransports) == "undefined")
    CTAPITransports = { }

CometWire = function () {
    var self = this;
    self.upstream_transport = null;
    self.downstream_transport = null;
    self.state = 0;
    self.id = null
    
    self.connect = function(connect_cb, args, url, preferred_transports) {
        shell.print("[CW] connecting")
        /* Cross-browser "transport_name not in CSPTransports */
        if ((typeof(preferred_transports) == "undefined")) {
            preferred_transports = []
        }
        self.state++;
        self.url = url;
        if (self.url == null)
            self.url = "/_/csp/"
        self.connect_cb = connect_cb
        self.args = args
        self.downstream_transport = create_downstream_transport(preferred_transports)
        self.downstream_transport.connect(self.message_cb, null, document.domain, 8000, self.url + "down")
    }
    var choose_best_transport = function() {
        //throw out non-XD
        
        for (var t in CTAPITransports.downstream) {
            return t        //actually, just return the first one
        }
    }
    var create_downstream_transport = function(preferred_transports) {
        // TODO: error checking... transport_name in CSPTransports ?
        for (var i = 0; i < preferred_transports.length; i++) {
            if (typeof(CTAPITransports['downstream'][preferred_transports[i]]) != "undefined")
                shell.print("[ CW ] choose downstream transport: " + preferred_transports[i])
                return new CTAPITransports['downstream'][preferred_transports[i]]()
        }
        var transport_name = choose_best_transport()
        shell.print("[ CW ] choose downstream transport: " + transport_name)
        return new CTAPITransports['downstream'][transport_name]()
    }
    self.set_close_cb = function(cb, args) {
        self.close_cb = [cb, args]
    }
    self.close = function() {
        if (typeof(self.close_cb) != "undefined") {
            self.state = 0
            cb = self.close_cb[0]
            args = self.close_cb[1]
            cb(args)
        }
    }

    self.send = function(payload) {
        return self.upstream_transport.send(payload) 
    }

    self.message_cb = function (data) {
        if (self.state == 1) {
            self.state += 1
            var frame = eval(data)
            if (frame[0] == "ID")   {
                self.id = frame[1]
                // TODO: choose best upstream transport
                // TODO: ask downstream if it supporst upstream first.
                self.upstream_transport = new CTAPITransports['upstream']['xhr'](self.url + "up/" + "xhr", frame[1]);
                self.upstream_transport.connect(
                    function(args) {
                        self.upstream_connect_callback(args) 
                    },
                    null
                )
                return
            }
            else {
                self.close()
            }
        }
        else if (self.state == 2) {
            frame = eval(data)
            if (frame[0] == "TIMEOUT") {
                self.close()
                return
            }
            else if (frame[0] == "CONNECTED") {
                self.state += 1
                return
            }
        }
        else if (self.state == 3) {
            if (typeof(self.receive_cb) != "undefined") {
                var cb = self.receive_cb[0]
                var args = self.receive_cb[1]
                cb(data, args)
            }
        }

    };

    self.upstream_connect_callback = function (cbargs) {
        if (typeof(self.connect_cb) != "undefined") {
            self.connect_cb(self.args);
        }
    };

    self.set_receive_cb = function(cb, args) {
        self.receive_cb = [cb, args];
    }

}