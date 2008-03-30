CometWire = function () {
    var self = this;
    self.upstream_transport = null;
    self.downstream_transport = null;
    self.state = "waiting";
    
    self.connect = function(url, connect_cb, args, preferred_transports) {
        shell.print("connecting cometwire")
        /* Cross-browser "transport_name not in CSPTransports */
        if ((typeof(preferred_transports) == "undefined")) {
            preferred_transports = []
        }
        self.state = "connecting"
        self.url = url;
        self.connect_cb = connect_cb
        self.args = args
        self.downstream_transport = create_transport(preferred_transports)
        self.downstream_transport.connect(self.message_cb, null, "localhost", 8000, "/_/cometwire/")
//        Orbited.connect(function(data) { self.message_cb(data); }, null, "http://127.0.0.1:8000/_/cometwire/", "leaky_iframe");
    };
    var choose_best_transport = function() {
        return 'iframe'
    }
    var create_transport = function(preferred_transports) {
        // TODO: error checking... transport_name in CSPTransports ?
        for (var i = 0; i < preferred_transports.length; i++) {
            if (typeof(CSPTransports[preferred_transports[i]]) != "undefined")
                shell.print("[ CW ] choose downstream transport: " + preferred_transports[i])
                return new CSPTransports[preferred_transports[i]]()
        }
        transport_name = choose_best_transport()
        shell.print("[ CW ] choose downstream transport: " + transport_name)
        return new CSPTransports[transport_name]()
    }
    self.set_close_cb = function(cb, args) {
        self.close_cb = [cb, args]
    }
    self.close = function() {
        if (typeof(self.close_cb) != "undefined") {
            self.state = "closed"
            cb = self.close_cb[0]
            args = self.close_cb[1]
            cb(args)
        }
    }

    self.send = function(payload) {
        return self.upstream_transport.send(payload) 
    }

    self.message_cb = function (data) {
        console.log("COMETWIRE receive down: " + data)
        if (data.length == 2) {
            if (self.state == "connecting") {
                if (data[0] == "ID") {
                    self.id = data[1]
                    self.upstream_transport = new UpstreamTransport(self.url, data[1]);
                    self.upstream_transport.connect(
                        function(args) {
                            self.upstream_connect_callback(args) 
                        },
                        null
                    )
                    return
                }
            }
            else if (data[0] == "TIMEOUT") {
                self.close()
                return
                //Orbited.disconnect()
            }
        }
        if (typeof(self.receive_cb) != "undefined") {
            cb = self.receive_cb[0]
            args = self.receive_cb[1]
            cb(data, args)
        }
    };

    self.upstream_connect_callback = function (cbargs) {
        self.state = "connected"
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