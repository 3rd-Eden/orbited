BinaryTCPSocket = function(domain, port) {
    var self = this;
    self.onopen = function() { }
    self.onclose = function() { }
    self.onread = function() { }
    self.readyState = 0

    var conn = new BaseTCPConnection()

    self.send = function(data) {
        conn.send(bytesToHex(data));
    }
    conn.onread = function(data) {
        self.onread(hexToBytes(data));
    }
    conn.onclose = function() {
        self.readyState = conn.readyState
        self.onclose();
    }
    conn.onopen = function() {
        self.readyState = conn.readyState
        conn.send(domain + ":" + port)
        self.onopen()
    }
    var connUrl = new URL(location.href)
    if (typeof(ORBITED_DOMAIN) != "undefined") 
        connUrl.domain = ORBITED_DOMAIN
    // Otherwise use the href domain
    if (typeof(ORBITED_PORT) != "undefined")
        connUrl.port = ORBITED_PORT
//    else
//        connUrl.port = connUrl.port
    connUrl.path = "/binaryproxy"
    connUrl.qs = ""
//    alert('connecting to: ' + connUrl.render())
    conn.connect(connUrl.render())
}
