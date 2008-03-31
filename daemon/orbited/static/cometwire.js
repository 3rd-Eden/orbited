if (typeof(CTAPITransports) == "undefined")
    CTAPITransports = { }



CometWire = function () {
    var self = this;
    self.upstream_transport = null;
    self.downstream_transport = null;
    self.state = 0;
    
    self.connect = function(url, connect_cb, args, preferred_transports) {
        shell.print("[CW] connecting")
        /* Cross-browser "transport_name not in CSPTransports */
        if ((typeof(preferred_transports) == "undefined")) {
            preferred_transports = []
        }
        self.state++;
        self.url = url;
        self.connect_cb = connect_cb
        self.args = args
        self.downstream_transport = create_transport(preferred_transports)
        self.downstream_transport.connect(self.message_cb, null, "127.0.0.1", 8000, "/_/cometwire/")
//        Orbited.connect(function(data) { self.message_cb(data); }, null, "http://127.0.0.1:8000/_/cometwire/", "leaky_iframe");
    };
    var choose_best_transport = function() {
        return 'iframe_fxcx'
    }
    var create_transport = function(preferred_transports) {
        // TODO: error checking... transport_name in CSPTransports ?
        for (var i = 0; i < preferred_transports.length; i++) {
            if (typeof(CTAPITransports[preferred_transports[i]]) != "undefined")
                shell.print("[ CW ] choose downstream transport: " + preferred_transports[i])
                return new CTAPITransports[preferred_transports[i]]()
        }
        transport_name = choose_best_transport()
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
        CWFRAME = data
        if (self.state == 1) {
            self.state += 1
            frame = eval(data)
            if (frame[0] == "ID")   {
                self.id = data[1]
                self.upstream_transport = new CTAPITransports['upstream']['xhr'](self.url, frame[1]);
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
                cb = self.receive_cb[0]
                args = self.receive_cb[1]
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
    };

};

/* Firefox test code */
start = function() {
    c = new CometWire()
    c.connect("/_/csp/up", ccb, c)
    return c
}
ccb = function(conn) {    
    console.log("connected", conn)
    conn.set_receive_cb(rcb, conn)
    conn.set_close_cb(clcb, conn)
}
rcb = function(data, conn) {
    console.log("received", data, "on", conn)
}
clcb = function(conn) {
    console.log("closed", conn)
}
/* End test code */