CometWire = function () {
    var self = this;
    self.transport = null;
    self.state = "waiting";

    self.connect = function(url, connect_cb, args) {
        console.log("connecting cometwire")
        self.state = "connecting"
        self.url = url;
        self.connect_cb = connect_cb
        self.args = args
        Orbited.connect(function(data) { self.message_cb(data); }, null, "http://127.0.0.1:8000/_/cometwire/", "leaky_iframe");
    };
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
        return self.transport.send(payload) 
    };
    self.message_cb = function (data) {
        console.log("COMETWIRE receive down: " + data)
        if (data.length == 2) {
            if (self.state == "connecting") {
                if (data[0] == "ID") {
                    self.id = data[1]
                    self.transport = new UpstreamTransport(self.url, data[1]);
                    self.transport.connect(function(args) { self.upstream_connect_callback(args) },null)
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