CometWire = function () {
    var self = this;
    
    self.transport = null;
    
    self.connect = function (url, connect_cb) {
        self.url = url;
        Orbited.connect(self.connect_callback, null, "/_/cometwire/", "iframe");
    };
    
    self.connect_callback = function (data) {
        alert(data);
        alert(self);
        self.transport = new UpstreamTransport(self.url, data);
        self.transport.send("hello");
    };
    
};