XSubdomainRequest = function(bridgeDomain, bridgePort, bridgePath, markedHeaders) {
    var self = this;
    if (!Boolean(bridgeDomain))
        throw new Error("Invalid bridge domain")
    if (!Boolean(bridgePath))
        bridgePath = "/_/static/XSubdomainBridge.html"
    if (!Boolean(markedHeaders))
        markedHeaders = [
            'Location',
        ]

    var ifr = null;
    var tempUrl = new URL("")
    tempUrl.domain = bridgeDomain
    tempUrl.port = bridgePort
    tempUrl.path = bridgePath
    var bridgeUrl = 'http://' + tempUrl.render()
    var receive = function(payload) {
//        alert('received: ' + payload);
        if (payload[0] == "initialized") {
            push([method, url, data, requestHeaders, markedHeaders])
        }
        if (payload[0] == "readystatechange") {
//            alert('readyState: ' + payload[1].readyState)
            self.readyState = payload[1].readyState
            if (typeof(payload[1].status) != "undefined") {
//                alert('status = ' + payload[1].status)
                self.status = payload[1].status
            }
            if (typeof(payload[1].responseText) != "undefined") {
//                alert('responseText += (' + payload[1].responseText.length + '): ' + payload[1].responseText)
                self.responseText += payload[1].responseText
            }
            if (typeof(payload[1].headers) != "undefined") {
                responseHeaders = payload[1]['headers']
            }
            self.onreadystatechange();
        }
    }
    self.getResponseHeader = function(key) {
        return responseHeaders[key];
    }
    self.getAllResponseHeaders = function() {
        return responseHeaders;
    }
    var queue = []
    var id = self._register(receive, queue);
    var push = function(payload) {
//        alert('push: ' + payload)
        self._state.queues[id].push(payload)
    }

    self.responseText = ""
    self.readyState = 0;
    self.status = null;
    self.onreadystatechange = function() { }
    var url = null;
    var method = null;
    var data = null;
    var requestHeaders = {};
    var responseHeaders = {}

    self.open = function(_method, _url, async) {
        if (self.readyState == 4) {
            self.responseText = ""
            self.status = null;
            self.readyState = 0;
            url = null;
            method = null;
            data = null;
            requestHeaders = {};
        }
        if (self.readyState != 0)
            throw new Error("Invalid Ready State for open")
        if (!async)
            throw new Error("Only Async XSDR supported")
        url = _url
        method = _method;
    }
    self.setRequestHeader = function(key, val) {
        if (self.readyState != 0)
            throw new Error("Invalid Ready State for setRequestHeader")
        requestHeaders[key] = val
    }
    self.send = function(_data) {
        /* TODO: auto-generate the bridgeUrl
        if (!Boolean(bridgeUrl)) {
            if (!Boolean(url.domain))
                throw new Error("invalid domain")
            var tempURL = URL(url.render())
            tempURL.path = "/
        */
        data = _data;
        if (ifr == null) {
            ifr = document.createElement("iframe")
            hideIframe(ifr);
            ifr.src = bridgeUrl + "#" + id;
            document.body.appendChild(ifr);
        }
        else {
            push([method, url, data, requestHeaders, markedHeaders])

        }
    }

    var hideIframe =function (ifr) {
        ifr.style.display = 'block';
        ifr.style.width = '0';
        ifr.style.height = '0';
        ifr.style.border = '0';
        ifr.style.margin = '0';
        ifr.style.padding = '0';
        ifr.style.overflow = 'hidden';
        ifr.style.visibility = 'hidden';
    }

}



XSubdomainRequest.prototype._state = { 
    requests: {},
    queues: {},
    id: 0
}
XSubdomainRequest.prototype._register = function(receive, queue) {
    var self = XSubdomainRequest.prototype;
    var id = ++self._state.id;
    self._state.requests[id] = receive;
//    alert('receive: ' + self._state.requests[id])
    self._state.queues[id] = queue;
//    alert(JSON.stringify(XSubdomainRequest.prototype._state))
    return id;
}

XSubdomainRequest.prototype._event = function(id, payload) {
    var self = XSubdomainRequest.prototype;
    var receive = self._state.requests[id];
    receive(payload);
}
