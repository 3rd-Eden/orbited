Orbited.require("CSP.js")

TCPConnection = function(domain, port, secure) {
    var self = this
    
    if (secure)
        throw "not implemented"
    
    self.readyState = 0
    
    self.onopen = null
    self.onread = null
    self.onclose = null

    var _onconnect = function() {
        conn.receive_cb = [_onread, null]
        conn.close_cb = [self.onclose, null]
        self.readyState = 1
        self.onopen()
    }

    var conn = new CSP()
    conn.connect(null, domain, port, _onconnect)
    
    var _onread = function(s) {
        if (typeof(self.onread.handleEvent) == "undefined") {
            self.onread(s)
        }
        else {
            // the distant future!
            onread.handleEvent("read", s.data)
        }
    }

    self.send = function(s) {
        conn.send(s)
    }

    self.disconnect = function() {
        self.readyState = 2
        conn.disconnect()
    }
}