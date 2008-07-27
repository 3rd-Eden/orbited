SSE = function() {
    var self = this;
    self.onread = function(packet) { }
    var source = null
    var url = null;

    self.close = function() {
        if (source != null) {
            // TODO: can someone test this and get back to me? (No opera at the moment)
            //     : -mcarter 7-26-08
            source.removeEventSource(source.src)
            source.src = ""
            document.body.removeChild(source)
            source = null;
        }
    }


    self.connect = function(_url) {
        if (self.readyState == 1) {
            throw new Error("Already Connected")
        }
        url = new URL(_url)
        url.setQsParameter('transport', 'sse')
        self.readyState = 1
        open()
    }

    open = function() {
        var source = document.createElement("event-source");
        source.setAttribute('src', url.render());
        if (opera.version() < 9.5) {
            document.body.appendChild(source);
        }
        source.addEventListener('orbited', receiveSSE, false);
    }

    var receiveSSE = function(event) {
        var data = eval(event.data);
        if (typeof(data) != 'undefined') {
            for (var i = 0; i < data.length; ++i) {
                var packet = data[i]
                receive(packet[0], packet[1], packet[2]);
            }
        }
    
    }
                
    var receive = function(id, name, args) {
        packet = {
            id: id,
            name: name,
            args: args
        }
        self.onread(packet)
    }
}
