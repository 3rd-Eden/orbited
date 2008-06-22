WebSocket = function(url) {
    var self = this;
    self.onopen = function() { }
    self.onclose = function() { }
    self.onread = function() { }
    self.readyState = 0

    var conn = new BaseTCPConnection()

    self.send = function(data) {
        conn.send(data);
    }
    conn.onread = function(data) {
        self.onread(data)
    }
    conn.onclose = function() {
        self.readyState = conn.readyState
        self.onclose();
    }
    conn.onopen = function() {
        self.readyState = conn.readyState
        conn.send(url)
        self.onopen()
    }
    var connUrl = new URL(location.href)
    if (typeof(ORBITED_DOMAIN) != "undefined") 
        connUrl.domain = ORBITED_DOMAIN
    if (typeof(ORBITED_PORT) != "undefined")
        connUrl.port = ORBITED_PORT
    connUrl.path = "/websocket"
    connUrl.qs = ""
    conn.connect(connUrl.render())
}
