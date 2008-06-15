// Requires: URL.js
// Requires: XSubdomainRequest.js

XHRStream = function() {
    var ESCAPE = "_"
    var PACKET_DELIMITER = "_P"
    var ARG_DELIMITER = "_A"
    var self = this;
    var url = null;
    xhr = null;
    var ackId = null;
    var offset = 0;
    self.retry = 50
    self.readyState = 0

    self.onread = function(packet) { }

    self.connect = function(_url) {
        if (self.readyState == 1) {
            throw new Error("Already Connected")
        }
        url = new URL(_url)
        if (xhr == null) {
            if (url.isSameDomain(location.href)) {
                xhr = new XMLHttpRequest();
            }
            else {
                xhr = new XSubdomainRequest(url.domain, url.port);
            }
        }
        url.setQsParameter('transport', 'xhrstream')
        self.readyState = 1
        open()
    }
    open = function() {

        xhr.open('GET', url.render(), true)
        if (typeof(ackId) == "number")
            xhr.setRequestHeader('ack', ackId)
        xhr.onreadystatechange = function() {
            switch(xhr.readyState) {
                case 3:
                    process();
                    break;
                case 4:
                    switch(xhr.status) {
                        case 200:
                            process();
                            reconnect();
                            break;
                        default:
                            self.disconnect();
                    }
            }
        }
        xhr.send(null);
    }
    self.disconnect = function() {
        self.readyState = 2
        xhr.onreadystatechange = function() { }
        xhr.abort()
        xhr = null;
    }
    var reconnect = function() {
        offset = 0;
        setTimeout(open, self.retry)
    }
    var process = function() {
        var stream = xhr.responseText;
        while (true) {
            if (stream.length <= offset) {
                return;
            }
            var nextBoundary = stream.indexOf(PACKET_DELIMITER, offset);
            if (nextBoundary == -1)
                return;
            var packet = stream.slice(offset, nextBoundary);
            offset = nextBoundary + PACKET_DELIMITER.length
            receivedPacket(packet)
        }
    }

    var receivedPacket = function(packetData) {
        var args = packetData.split(ARG_DELIMITER)
        ackId = parseInt(args[0])
        packet = {
            id: ackId,
            name: args[1],
            args: args.slice(2)
        }
        self.onread(packet)
    }
}