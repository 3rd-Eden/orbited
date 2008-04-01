Orbited.require("CSP.js")

TCPConnection = function(location, onopen, onread, onclose) {
    var self = this
    self.network = true                     // we don't use this, htm5? does
    self.readyState = 0

    var _onconnect = function() {
        conn.receive_cb = [_onread, null]
        conn.close_cb = [onclose, null]
        self.readyState = 1
        onopen()
    }

    // TODO: do something with the location parameter
    var conn = new CSP()
    conn.connect(null, _onconnect, null)

    var _onread = function(s) {
        if (typeof(onread.handleEvent) == "undefined") {
            onread(s)
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