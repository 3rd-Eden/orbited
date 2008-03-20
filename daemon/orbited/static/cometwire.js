CometWire = function () {
    this.transport = null;
};

CometWire.prototype = {
    
    connect: function (url, connect_cb) {
        this.url = url;
        var self = this;
        Orbited.connect(function(data) { self.connect_callback(data); }, null, "/_/cometwire/", "iframe");
    },  
    
    connect_callback: function (data) {
        alert(data);
        alert(this);
        this.transport = new UpstreamTransport(this.url, data);
        this.transport.send("hello");
    }
    
};