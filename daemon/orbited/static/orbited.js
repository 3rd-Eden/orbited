document.domain=document.domain
var browser = null;
if (typeof(ActiveXObject) != "undefined") {
    browser = 'ie'
} else if (navigator.product == 'Gecko' && window.find && !navigator.savePreferences) {
    browser = 'firefox'
} else if((typeof window.addEventStream) === 'function') {
    browser = 'opera'
} else {
    throw new Error("couldn't detect browser")
}


// start @include(URL.js)
URL = function(_url) {
    var self = this;
    var protocolIndex = _url.indexOf("://")
    if (protocolIndex != -1)
        self.protocol = _url.slice(0,protocolIndex)
    else
        protocolIndex = -3
    var domainIndex = _url.indexOf('/', protocolIndex+3)
    if (domainIndex == -1)
        domainIndex=_url.length
    var hashIndex = _url.indexOf("#", domainIndex)
    if (hashIndex != -1)
        self.hash = _url.slice(hashIndex+1)
    else
        hashIndex = _url.length
    var uri = _url.slice(domainIndex, hashIndex)
    var qsIndex = uri.indexOf('?')
    if (qsIndex == -1)
        qsIndex=uri.length
    self.path = uri.slice(0, qsIndex)
    self.qs = uri.slice(qsIndex+1)
    if (self.path == "")
        self.path = "/"
    var domain = _url.slice(protocolIndex+3, domainIndex)
    var portIndex = domain.indexOf(":")
    if (portIndex == -1) {
        self.port = 80
        portIndex = domain.length
    }
    else {
        self.port = parseInt(domain.slice(portIndex+1))
    }
    if (isNaN(this.port))
        throw new Error("Invalid _url")
    self.domain = domain.slice(0, portIndex)

    self.render = function() {
        var output = ""
        if (typeof(self.protocol) != "undefined")
            output += self.protocol + "://"
        output += self.domain
        if (self.port != 80 && typeof(self.port) != "undefined" && self.port != null)
            if (typeof(self.port) != "string" || self.port.length > 0)
                output += ":" + self.port
        if (typeof(self.path) == "undefined" || self.path == null)
            output += '/'
        else
            output += self.path
        if (self.qs.length > 0)
            output += '?' + self.qs
        if (typeof(self.hash) != "undefined" && self.hash.length > 0)
            output += "#" + self.hash
        return output
    }
    self.isSameDomain = function(_url) {
        _url = new URL(_url)

/*        console.log('isSame? ' + _url.render())
        console.log('self: ' + self.render())
        console.log('_url.domain: ' + _url.domain)
        console.log('self.domain: ' + self.domain) */
        if (!_url.domain || !self.domain)
            return true
        return (_url.port == self.port && _url.domain == self.domain)
    }
/*    self.isSameParentDomain = function(_url) {
        _url = new URL(_url)
        var parts = _url.domain.split('.')
        for (var i = 0; i < parts.length-1; ++i) {
            var new_domain = parts.slice(i).join(".")
            if (new_domain == self.domain)
                return true;
        }
    }
*/
    self.isSameParentDomain = function(_url) {
        _url = new URL(_url)
        if (_url.domain == self.domain) {
            return true;
        }
        var orig_domain = _url.domain;
        var parts = document.domain.split('.')
//        var orig_domain = document.domain
        for (var i = 0; i < parts.length-1; ++i) {
            var new_domain = parts.slice(i).join(".")
            if (orig_domain == new_domain)
                return true;
        }
        return false
    }

    var decodeQs = function(qs) {
    //    alert('a')
        if (qs.indexOf('=') == -1) return {}
        var result = {}
        var chunks = qs.split('&')
        for (var i = 0; i < chunks.length; ++i) {
            var cur = chunks[i]
            pieces = cur.split('=')
            result[pieces[0]] = pieces[1]
        }
        return result
    }
    var encodeQs = function(o) {
            var output = ""
            for (key in o)
                output += "&" + key + "=" + o[key]
            return output.slice(1)
        }
    self.setQsParameter = function(key, val) {
        var curQsObj = decodeQs(self.qs)
        curQsObj[key] = val
        self.qs = encodeQs(curQsObj)
    }

    self.mergeQs = function(qs) {
        var newQsObj = decodeQs(qs)
        for (key in newQsObj) {
            curQsObj[key] = newQsObj[key]
        }
    }
    self.removeQsParameter = function(key) {
        var curQsObj = decodeQs(self.qs)
        delete curQsObj[key]
        self.qs = encodeQs(curQsObj)
    }

    self.merge = function(targetUrl) {
        if (typeof(self.protocol) != "undefined" && self.protocol.length > 0) {
            self.protocol = targetUrl.protocol
        }
        if (targetUrl.domain.length > 0) {
            self.domain = targetUrl.domain
            self.port = targetUrl.port
        }
        self.path = targetUrl.path
        self.qs = targetUrl.qs
        self.hash = targetUrl.hash
    }

}

// end @include(URL.js)


// start @include(transports/TransportChooser.js)
TransportChooser = {}
TransportChooser.create = function() {
    // Browser detect by Frank Salim
    var browser = null;
    if (typeof(ActiveXObject) != "undefined") {
        browser = 'ie'
    } else if (navigator.product == 'Gecko' && window.find && !navigator.savePreferences) {
        browser = 'firefox'
    } else if((typeof window.addEventStream) === 'function') {
        browser = 'opera'
    } else {
        throw new Error("couldn't detect browser")
    }
    
    switch(browser) {
        case 'firefox':
            return new XHRStream();
        case 'ie':
            return new HTMLFile();
        case 'opera':
            return new SSE();
    }
}
// end @include(transports/TransportChooser.js)

switch(browser) {
    case 'firefox': // this is also case 'safari'
        
// start @include(transports/XHRStream.js)
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
// end @include(transports/XHRStream.js)

        break;
    case 'ie':
        
// start @include(transports/HTMLFile.js)
HTMLFile = function() {
    var self = this;
    id = ++HTMLFile.prototype.i;
    HTMLFile.prototype.instances[id] = self
    var htmlfile2 = null
    var url = null;
    self.onread = function(packet) { }

    self.connect = function(_url) {
        if (self.readyState == 1) {
            throw new Error("Already Connected")
        }
        url = new URL(_url)
        url.setQsParameter('transport', 'htmlfile')
        url.setQsParameter('frameID', id.toString())
//        url.hash = id.toString()
        self.readyState = 1
        doOpen()
    }

    var doOpenIfr = function() {
        
        var ifr = document.createElement('iframe')
        ifr.src = url.render()
        document.body.appendChild(ifr)
    }

    var doOpen = function() {
        htmlfile = new ActiveXObject('htmlfile'); // magical microsoft object
        htmlfile.open();
        htmlfile.write('<html><script>' + 'document.domain="' + document.domain + '";' + '</script></html>');
        htmlfile.parentWindow.HTMLFile = HTMLFile;
        htmlfile.close();
        var iframe_div = htmlfile.createElement('div');
        htmlfile.body.appendChild(iframe_div);
        iframe_div.innerHTML = "<iframe src=\"" + url.render() + "\"></iframe>";
    }
    
    self.receive = function(id, name, args) {
        packet = {
            id: id,
            name: name,
            args: args
        }
        self.onread(packet)
    }
}

HTMLFile.prototype.i = 8
HTMLFile.prototype.instances = {}
// end @include(transports/HTMLFile.js)

        break;
    case 'opera':
        
// start @include(transports/SSEAppXDom.js)
SSE = function() {
    var self = this;
    self.onread = function(packet) { }
    var source = null
    var url = null;
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
//      TODO: uncomment this line to work in opera 8 - 9.27.
//            there should be some way to make this work in both.
//        document.body.appendChild(source);
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

// end @include(transports/SSEAppXDom.js)

        break;
}

// start @include(BaseTCPConnection.js)
BaseTCPConnection = function() {
    var self = this;
    transport = null;
    var url = null;
    var sendUrl = null;
    var xhr = null;
    var sendQueue = []
    var sending = false;
    var numSent = null;
    var ackId = 0;
    self.readyState = 0;
    
    self.connect = function(_url) {
        if (self.readyState != 0 && self.readyState != 3) {
            throw new Error("Invalid readyState for connect");
        }
        url = new URL(_url);
        if (url.isSameDomain(location.href)) {
            xhr = createXHR();
        }
        else {
            xhr = new XSubdomainRequest(url.domain, url.port);
        }
        self.readyState = 1;
        getSession();
    }
        
    self.send = function(data) {
        sendQueue.push(data)
        if (!sending) {
            doSend();
        }
    }
    
    var doSend = function() {
        if (sendQueue.length == 0) {
            sending = false;
            return
        }
        sending = true;
        numSent = sendQueue.length
        xhr.open('POST', url.render(), true)
        xhr.setRequestHeader('ack', ackId)
        xhr.setRequestHeader('Tcp-Encoding', 'text')
        xhr.onreadystatechange = function() {
            switch(xhr.readyState) {
                case 4:
                    switch(xhr.status) {
                        case 200:
                            sendQueue = sendQueue.slice(numSent)
                            return doSend();
                    }
                    break;
            }
        }
        xhr.send(sendQueue.join(""))
    
    }

    var sendPingResponse = function() {
        xhr.open('POST', url.render(), true)
        xhr.setRequestHeader('ack', ackId)
        xhr.onreadystatechange = function() {
            switch(xhr.readyState) {
                case 4:
                    switch(xhr.status) {
                        case 200:
                    }
                    break;
            }
        }
        xhr.send(null)
    }

    var getSession = function() {
        xhr.open('GET', url.render(), true)
        xhr.onreadystatechange = function() {
            switch(xhr.readyState) {
                case 4:
                    switch(xhr.status) {
                        case 200:
                            var key = xhr.responseText
                            if (url.path[url.path.length-1] != '/') {
                                url.path += '/'
                            }
                            url.path += key
                            sendUrl = new URL(url.render())
                            connectTransport()
                            break;                    
                    }
                    break;
            }
        }
        xhr.send(null);
    }
    
    var connectTransport = function()  {
        transport = TransportChooser.create();
        transport.connect(url.render())
        transport.onread = packetReceived
    }

    var packetReceived = function(packet) {
        if (!isNaN(packet.id) && packet.id > ackId) {
            ackId = packet.id
        }
        switch(packet.name) {
            case 'open':
                doOpen();
                break;
            case 'close':
                doClose();
                break;
            case 'data':
                doRead(packet.args)
                break;
            case 'ping':
                sendPingResponse();
                break;
        }
    }

    var doOpen = function() {
        if (self.readyState != 1) {
            throw new Error("Received invalid open")
        }
        self.readyState = 2;
        self.onopen();
    }
    var doClose = function() {
        if (self.readyState == 3) {
            throw new Error("already closed")
        }
        self.readyState = 3;
        self.onclose();
    }
    var doRead = function(args) {
        var data = args[0]
        self.onread(data);
    }

    var createXHR = function () {
        try { return new ActiveXObject('MSXML3.XMLHTTP'); } catch(e) {}
        try { return new ActiveXObject('MSXML2.XMLHTTP.3.0'); } catch(e) {}
        try { return new ActiveXObject('Msxml2.XMLHTTP'); } catch(e) {}
        try { return new ActiveXObject('Microsoft.XMLHTTP'); } catch(e) {}
        try { return new XMLHttpRequest(); } catch(e) {}
        throw new Error('Could not find XMLHttpRequest or an alternative.');
    }
}
// end @include(BaseTCPConnection.js)


// start @include(XSubdomainRequest.js)
XSubdomainRequest = function(bridgeDomain, bridgePort, bridgePath, markedHeaders) {
    var self = this;
    if (!Boolean(bridgeDomain))
        throw new Error("Invalid bridge domain")
    if (!Boolean(bridgePath))
        bridgePath = "/static/XSubdomainBridge.html"
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

// end @include(XSubdomainRequest.js)


// start @include(OrbitedLegacyWrapper.js)
Orbited = {
    connect: function (event_cb /* args 1-3 are token parts */) {
        var tokens = Array.prototype.slice.call(arguments, 1)
        if (tokens.length == 3)
            var token = tokens[0] + ", " + tokens[2] + ', ' + tokens[1]
        else
            var token = tokens[0]
    
        var conn = new BaseTCPConnection()
        var connUrl = new URL(location.href)
        if (typeof(ORBITED_DOMAIN) != "undefined") 
            connUrl.domain = ORBITED_DOMAIN
        if (typeof(ORBITED_PORT) != "undefined")
            connUrl.port = ORBITED_PORT
        connUrl.path = "/legacy"
        connUrl.qs = ""
        conn.onread = event_cb
        conn.onopen = function(data) {
            conn.send(token);
        }
        conn.connect(connUrl.render())
    },

    create_xhr: function () {
        try { return new ActiveXObject('MSXML3.XMLHTTP'); } catch(e) {}
        try { return new ActiveXObject('MSXML2.XMLHTTP.3.0'); } catch(e) {}
        try { return new ActiveXObject('Msxml2.XMLHTTP'); } catch(e) {}
        try { return new ActiveXObject('Microsoft.XMLHTTP'); } catch(e) {}
        try { return new XMLHttpRequest(); } catch(e) {}
        throw new Error('Could not find XMLHttpRequest or an alternative.');
  }

    
}

// end @include(OrbitedLegacyWrapper.js)
