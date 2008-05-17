JSONTCPConnection = function(domain, port) {
    var self = this;
    self.onopen = function() { }
    self.onclose = function() { }
    self.onread = function() { }
    self.readyState = 0

    var conn = new BaseTCPConnection()

    self.send = function(data) {
        conn.send(JSON.stringify(data));
    }
    conn.onread = function(evt) {
        evt.data = eval(evt.data);
        self.onread(evt);
    }
    conn.onclose = function(evt) {
        self.readyState = conn.readyState
        self.onclose(evt);
    }
    conn.onopen = function(evt) {
        self.readyState = conn.readyState
        self.send(domain + ":" + port)
        self.onopen(evt)
    }
    var connUrl = new URL(location.href)
//    connUrl.domain = document.domain
//    connUrl.port = location.port
    connUrl.path = "/jsonproxy"
    connUrl.qs = ""
    conn.connect(connUrl.render())
//    conn.connect("http://www.test.local:7000/proxy")
}
