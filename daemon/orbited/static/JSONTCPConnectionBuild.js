document.domain=document.domain
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
        if (typeof(self.hash) != "undefined")
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

}
// end @include(URL.js)


// start @include(transports/transport.js)
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

CometTransport = function() {
    var self = this;
    CometTransport.instances[0] = self;
    var source = null;
    self.receivePayload = function(evt) { }
    self.receiveTCPOpen = function(evt) { }
    self.receiveTCPClose = function(evt) { }
    self.receiveTCPPing = function(evt) { }
    var url = null;
    var receivePayload = function(evt)  { self.receivePayload(evt)  }
    var receiveTCPOpen = function(evt)  { self.receiveTCPOpen(evt)  }
    var receiveTCPClose = function(evt) { self.receiveTCPClose(evt) }
    var receiveTCPPing = function(evt)  { self.receiveTCPPing(evt)  }
    var lastEventId = 0;
    self.connect = function(_url) {
        url = _url;
        switch(browser) {
            case 'firefox':
                source = document.createElement("event-source")
                source.addEventListener("message", receivePayload, false)
                source.addEventListener("TCPOpen", receiveTCPOpen, false)
                source.addEventListener("TCPClose", receiveTCPClose, false)
                source.addEventListener("TCPPing", receiveTCPPing, false)
                source.addEventSource(url + "?transport=sse&woot=boot&a=b#0")
                document.body.appendChild(source)
                break;
            default:
                source = document.createElement("iframe")
                source.src = url + "?transport=htmlfile&woot=boot&a=b#0"
                document.body.appendChild(source)
                break;
        }
    }

    self.destroy = function() {
        switch(browser) {
            default:
                document.body.removeChild(source)
                break;
            case 'firefox2':
                source.removeEventSource(url)
                source.removeEventListener("message", receivePayload, false)
                source.removeEventListener("TCPOpen", receiveTCPOpen, false)
                source.removeEventListener("TCPClose", receiveTCPClose, false)
                source.removeEventListener("TCPPing", receiveTCPPing, false)
                document.body.removeChild(source)
                break;
        }
    }

    self.receive = function(name, data, id, retry) {
        print('name: ' + name + ', data: ' + data + ', id: ' + id + ', retry: ' + retry)
        evt = {
            name: name,
            data: data,
            retry: retry
        }
        if (id > lastEventId) {
            lastEventId = id
        }
        evt['lastEventId'] = lastEventId
        switch(name) {
            case null:
            case 'message':
                if (data != null && data.length > 0)
                    receivePayload(evt);
                break;
            case 'TCPOpen':
                receiveTCPOpen(evt);
                break;
            case 'TCPClose':
                receiveTCPClose(evt);
                break;
            case 'TCPPing':
                receiveTCPPing(evt);
                break;
        }
    }
}
CometTransport.instances = {}
x = 1
// end @include(transports/transport.js)

switch(browser) {
    case 'ie':
        
// start @include(transports/IEHtmlFile.js)

// end @include(transports/IEHtmlFile.js)

        break;
    case 'firefox':
        
// start @include(transports/ServerSentEvents.js)
window.addEventListener("load", function() {
    sources = document.getElementsByTagName("event-source")
    for (var i = 0; i < sources.length; ++i) {
        source = sources[i]
        var SSEHandler = new FxSSE(source);
        // TODO: removeEventSource
    }
    var createElement = document.createElement
    document.createElement = function(name) {
        var obj = createElement.call(this, name)
        if (name == "event-source")
            var SSEHandler = new FxSSE(obj);
        return obj
    }
}, false);

FxSSE = function(source) {
    var self = this;
    var xhr = null;
    var retry = 3000;
    var id = null;
    var offset = 0;
//    var next_boundary = -1;
    var boundary = "\n"
    var lineQueue = []
    var origin = "" // TODO: derive this from the src argument 
    var src = null;
    var origSrc = null;
    var reconnectTimer = null;
//    source.lastEventId = null;
    
    source.addEventSource = function(eventSrc) {
        // TODO: keep track of sources that we are already connected to
        //       check the spec for information on this
        if (src != null) {
            throw new Error("AlreadyConnected: wait for widespread adoption of SSE specification")
        }
        src = eventSrc
        origSrc = src
        connect()
    }
    
    source.removeEventSource = function(eventSrc) {
        if (eventSrc != origSrc)
            throw new Error("NotConnected to src: " + eventSrc)
        if (reconnectTimer != null) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }
        if (xhr != null) {
            xhr.onreadystatechange = function() { };
            xhr.abort()
//            xhr = null;
            offset = 0;
            lineQueue = []
            id = null;
//            source.lastEventId = null;
        }
        src = null;
        origSrc = null;
    }
    var connect = function() {
//        console.log('connect!')
        if (reconnectTimer != null) {
            reconnectTimer = null;
        }
        // TODO: re-use this xhr connection
        var testUrl = new URL(src);
//        console.log('? ' + src)
        if (xhr == null) {
            if (testUrl.isSameDomain(location.href)) {
    //            console.log('a');
                xhr = new XMLHttpRequest();
            }
            else if (testUrl.isSameParentDomain(location.href)) {
    //            console.log('b')
                xhr = new XSubdomainRequest(testUrl.domain, testUrl.port)
            }
        }
//        console.log('xhr.open')
//        xhr = new XSubdomainRequest("http://sub.www.test.local:7000/echo/static/xdr/sub.html");
//        xhr = new XMLHttpRequest();
        xhr.open('GET', src, true);
        if (id != null) {
            xhr.setRequestHeader('Last-Event-ID', id)
        }
        else {
        }
        xhr.onreadystatechange = function() {
            switch (xhr.readyState) {
                case 4: // disconnect case
                    switch(xhr.status) {
                        // NOTE: This implementation accepts status code 201 as a 301
                        //       replacement for Permenantly Moved.
                        case 201:
//                            console.log('201!');
                            var r = xhr.getAllResponseHeaders()
//                            console.log(r)
//                            console.log('kk')
//                            for (key in r)
//                                console.log(key + ': ' + r[key])
//                            console.log('jj')
                            var newSrc = xhr.getResponseHeader('Location')
//                            console.log('newSrc: ' + newSrc)
                            if (newSrc == null)
                                throw new Error("Invalid 201 Response -- Location missing")
                            var newUrl = new URL(newSrc)
                            var oldUrl = new URL(src);
                            oldUrl.qs = newUrl.qs
                            oldUrl.path = newUrl.path
                            src = oldUrl.render()
//                            console.log('new src: ' + src)
                            dispatch()
                            reconnect()
                            break;
                        case 200:
                            dispatch()
                            reconnect()
                            break
                        default:
                            source.removeEventSource(src)
                    }
                    break
                case 3: // new data
                    process()
                    break
            }
        }
        xhr.send(null);
    }
    var reconnect = function() {
//        console.log('reconnect!')
        // TODO: reuse this xhr connection
//        xhr = null;
        offset = 0
        reconnectTimer = setTimeout(connect, retry)
    }

    var process = function() {
        var stream = xhr.responseText
        if (stream.length < offset) // in safari the offset starts at 256
            return 
        var next_boundary = stream.indexOf(boundary, offset);
        if (next_boundary == -1)
            return
        var line = stream.slice(offset, next_boundary)
        offset = next_boundary + boundary.length
        if (line.length == 0 || line == "\r")
            dispatch()
        else
            lineQueue.push(line) // TODO: is this cross-browser?                
        // TODO: use a while loop here. We don't want a stack overflow
        process() // Keep going until we run out of new lines
    }

    var dispatch = function() {
        var data = "";
        var name = "message";
        lineQueue.reverse() // So we can use pop which removes elements from the end
        while (lineQueue.length > 0) {
            line = lineQueue.pop()
            if (line.slice(-1) == "\r")
                line = line.slice(0, -1)
            var field = null;
            var value = "";
            var j = line.indexOf(':')
            if (j == -1) {
                field = line
                value = ""
            }
            else if (j == 0) {
                continue // This line must be a comment
            }
            else {
                field = line.slice(0, j)
                value = line.slice(j+1)
            }
            if (field == "event")
                name = value
            if (field == "id") {
                id = value
//                source.lastEventId = id;
            }
            if (field == "retry") {
                value = parseInt(value)
                if (!isNaN(value))
                    retry = value
            }
            if (field == "data") {
                if (data.length > 0)
                    data += "\n"
                data += value
            }
        }
        var e = document.createEvent("Events")
        if (data.length > 0 || (name != "message" && name.length > 0)) {
            e.initEvent(name, true, true)
            e.lastEventId = id
            e.data = data
            e.origin = document.domain
            e.source = null
            source.dispatchEvent(e);
        }

    }

}

function test() {
    var s = document.getElementById("ssedom");
    s.addEventSource("http://localhost:8000/?identifier=test&transport=sse2");
    return s;
}
// end @include(transports/ServerSentEvents.js)

        break;
}

// start @include(BaseTCPConnection.js)

BaseTCPConnection = function() {
    var PING_TIMEOUT = 45000;
    var self = this;
    self.readyState = -1
    self.onopen = function(evt) {}
    self.onread = function(evt) {}
    self.onclose = function(evt) {}    
    var url = null;
    var tcpUrl = null;
    var session = null;
    var transport = null;
    var xhr = null;
    var lastEventId = null;
    var sendQueue = [];
    var sending = false;
    var pingTimer = null;
    var numSendPackets = null;

    self.connect = function(_url) {
        if (self.readyState != -1 && self.readyState != 2)
            throw new Error("connect may only be called on a closed socket");
        self.readyState = 0
        var testUrl = new URL(_url);
        
        if (testUrl.isSameDomain(location.href)) {
            xhr = createXHR();
        }

        else if (testUrl.isSameParentDomain(location.href)) {
//            alert('using XSubdomainRequest')
//            document.domain = document.domain
            var path = testUrl.path
            if (path[path.length-1] != '/')
                path += '/'
            path += 'static/XSubdomainBridge.html'
            console.log('xdr path: ' + path)
            xhr = new XSubdomainRequest(testUrl.domain, testUrl.port, path)
        }
        else {
            throw new Error("Invalid domain. BaseTCPConnection instances may only connect to same-domain or sub-domain hosts.")
        }
        url = testUrl.render()
        attachTransport();
    }
    

    var attachTransport = function() {
        tcpUrl = url
        transport = new CometTransport()
        transport.receivePayload = receivePayload;
        transport.receiveTCPOpen = receiveTCPOpen;
        transport.receiveTCPClose = receiveTCPClose;
        transport.receiveTCPPing = receiveTCPPing;
        transport.connect(tcpUrl);
    }

    self.send = function(data) {
        sendQueue.push(data);
        if (!sending)
            doSend();
    }
    var doSend = function() {
        if (sendQueue.length == 0) {
            sending = false;
            return
        }
        numSendPackets = sendQueue.length
        sending = true;
//        var data = sendQueue[0]
        var payload = ""
        xhr.open('POST', tcpUrl, true);
        xhr.setRequestHeader('Content-Type', 'text/event-stream; charset=utf-8')
        var payload = ""
        for (var i = 0; i < sendQueue.length; ++i) {
            var data = sendQueue[i]
            payload += "data:" + data.split("\n").join("\r\ndata:") + "\r\n\r\n"
        }
        // TODO: don't to this here.
        if (lastEventId != null && typeof(lastEventId) != "undefined") {
            payload += "event:TCPAck\r\ndata:" + lastEventId + "\r\n\r\n"
        } 
        xhr.onreadystatechange = function() {
            switch(xhr.readyState) {
                case 4:
                    if (xhr.status == 200) {
                        sendQueue = sendQueue.slice(numSendPackets);
                        doSend();
                    }
                    else {
                        // TODO: retry?
                    }
                    
            }
        }
        xhr.send(payload);
        resetPingTimer()
    }

    self.ack_only = function() {
        var payload = ""
        xhr.open('POST', tcpUrl, true);
        xhr.setRequestHeader('Content-Type', 'text/event-stream; charset=utf-8')
        payload = "event:TCPAck\r\ndata:" + lastEventId + "\r\n\r\n"
        xhr.onreadystatechange = function() {
            switch(xhr.readyState) {
                case 4:
                    if (xhr.status != 200) {
                        // TODO: retry?
                    }
            }
        }
        xhr.send(payload);
    }

    var onTimeout = function() {
        doClose();
        self.onclose(null);
    }
    var resetPingTimer = function() {
        if (pingTimer != null) {
            clearTimeout(pingTimer)
        }
        pingTimer = setTimeout(onTimeout, PING_TIMEOUT)
    }
    var receiveTCPPing = function(evt) {
//        print('received TCPPing in BaseTCPConnection')
        lastEventId = evt.lastEventId;
        resetPingTimer();
        self.ack_only();
    }
    var receiveTCPOpen = function(evt) {
//        console.log('receiveTCPOpen');
//        console.log(evt.data);
        // TODO: use the EventListener interface if available (handleEvent)
        lastEventId = evt.lastEventId;
        self.readyState = 1
        if (evt.data != null && evt.data.length > 0) {
            var newUrl = new URL(evt.data);
            var oldUrl = new URL(tcpUrl);
            oldUrl.qs = newUrl.qs
            oldUrl.path = newUrl.path
            tcpUrl = oldUrl.render()
        }
        self.onopen(evt);
        resetPingTimer();
//        window.setTimeout(tcp.onopen, 1000)
//        window.setTimeout("tcp.onopen()", 0)//function() { self.onopen(evt) }, 0)
    }
    var receiveTCPClose = function(evt) {
        // TODO: use the EventListener interface if available (handleEvent)
        lastEventId = evt.lastEventId;
        doClose();
        self.onclose(evt)
    }
    var doClose = function() {
        self.readyState = 2
        transport.destroy();
    }
    var receivePayload = function(evt) {
        // TODO: use the EventListener interface if available (handleEvent)
        lastEventId = evt.lastEventId;
        if (self.readyState == 1) {
            self.onread(evt)
        }
        // NOTE: raise an exception if the server misbehaves
        //       this is not in the html5 specification
    
        else 
            throw new Error("Unexpected Data")
        // TODO: throw an exception if we get data we shouldn't?
    }

    var createXHR = function() {
        try { return new ActiveXObject("Msxml2.XMLHTTP"); } catch (e) {}
        try { return new ActiveXObject("Microsoft.XMLHTTP"); } catch (e) {}
        try { return new XMLHttpRequest(); } catch(e) {}
        return null;
    }
};

// end @include(BaseTCPConnection.js)


// start @include(XSubdomainRequest.js)
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

// end @include(XSubdomainRequest.js)


// start @include(JSON.js)
/*jslint evil: true */
/*extern JSON */

if (!this.JSON) {

    JSON = function () {

        function f(n) {    // Format integers to have at least two digits.
            return n < 10 ? '0' + n : n;
        }

        Date.prototype.toJSON = function () {

// Eventually, this method will be based on the date.toISOString method.

            return this.getUTCFullYear()   + '-' +
                 f(this.getUTCMonth() + 1) + '-' +
                 f(this.getUTCDate())      + 'T' +
                 f(this.getUTCHours())     + ':' +
                 f(this.getUTCMinutes())   + ':' +
                 f(this.getUTCSeconds())   + 'Z';
        };


        var m = {    // table of character substitutions
            '\b': '\\b',
            '\t': '\\t',
            '\n': '\\n',
            '\f': '\\f',
            '\r': '\\r',
            '"' : '\\"',
            '\\': '\\\\'
        };

        function stringify(value, whitelist) {
            var a,          // The array holding the partial texts.
                i,          // The loop counter.
                k,          // The member key.
                l,          // Length.
                r = /["\\\x00-\x1f\x7f-\x9f]/g,
                v;          // The member value.

            switch (typeof value) {
            case 'string':

// If the string contains no control characters, no quote characters, and no
// backslash characters, then we can safely slap some quotes around it.
// Otherwise we must also replace the offending characters with safe sequences.

                return r.test(value) ?
                    '"' + value.replace(r, function (a) {
                        var c = m[a];
                        if (c) {
                            return c;
                        }
                        c = a.charCodeAt();
                        return '\\u00' + Math.floor(c / 16).toString(16) +
                                                   (c % 16).toString(16);
                    }) + '"' :
                    '"' + value + '"';

            case 'number':

// JSON numbers must be finite. Encode non-finite numbers as null.

                return isFinite(value) ? String(value) : 'null';

            case 'boolean':
            case 'null':
                return String(value);

            case 'object':

// Due to a specification blunder in ECMAScript,
// typeof null is 'object', so watch out for that case.

                if (!value) {
                    return 'null';
                }

// If the object has a toJSON method, call it, and stringify the result.

                if (typeof value.toJSON === 'function') {
                    return stringify(value.toJSON());
                }
                a = [];
                if (typeof value.length === 'number' &&
                        !(value.propertyIsEnumerable('length'))) {

// The object is an array. Stringify every element. Use null as a placeholder
// for non-JSON values.

                    l = value.length;
                    for (i = 0; i < l; i += 1) {
                        a.push(stringify(value[i], whitelist) || 'null');
                    }

// Join all of the elements together and wrap them in brackets.

                    return '[' + a.join(',') + ']';
                }
                if (whitelist) {

// If a whitelist (array of keys) is provided, use it to select the components
// of the object.

                    l = whitelist.length;
                    for (i = 0; i < l; i += 1) {
                        k = whitelist[i];
                        if (typeof k === 'string') {
                            v = stringify(value[k], whitelist);
                            if (v) {
                                a.push(stringify(k) + ':' + v);
                            }
                        }
                    }
                } else {

// Otherwise, iterate through all of the keys in the object.

                    for (k in value) {
                        if (typeof k === 'string') {
                            v = stringify(value[k], whitelist);
                            if (v) {
                                a.push(stringify(k) + ':' + v);
                            }
                        }
                    }
                }

// Join all of the member texts together and wrap them in braces.

                return '{' + a.join(',') + '}';
            }
        }

        return {
            stringify: stringify,
            parse: function (text, filter) {
                var j;

                function walk(k, v) {
                    var i, n;
                    if (v && typeof v === 'object') {
                        for (i in v) {
                            if (Object.prototype.hasOwnProperty.apply(v, [i])) {
                                n = walk(i, v[i]);
                                if (n !== undefined) {
                                    v[i] = n;
                                }
                            }
                        }
                    }
                    return filter(k, v);
                }


// Parsing happens in three stages. In the first stage, we run the text against
// regular expressions that look for non-JSON patterns. We are especially
// concerned with '()' and 'new' because they can cause invocation, and '='
// because it can cause mutation. But just to be safe, we want to reject all
// unexpected forms.

// We split the first stage into 4 regexp operations in order to work around
// crippling inefficiencies in IE's and Safari's regexp engines. First we
// replace all backslash pairs with '@' (a non-JSON character). Second, we
// replace all simple value tokens with ']' characters. Third, we delete all
// open brackets that follow a colon or comma or that begin the text. Finally,
// we look to see that the remaining characters are only whitespace or ']' or
// ',' or ':' or '{' or '}'. If that is so, then the text is safe for eval.

                if (/^[\],:{}\s]*$/.test(text.replace(/\\./g, '@').
replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(:?[eE][+\-]?\d+)?/g, ']').
replace(/(?:^|:|,)(?:\s*\[)+/g, ''))) {

// In the second stage we use the eval function to compile the text into a
// JavaScript structure. The '{' operator is subject to a syntactic ambiguity
// in JavaScript: it can begin a block or an object literal. We wrap the text
// in parens to eliminate the ambiguity.

                    j = eval('(' + text + ')');

// In the optional third stage, we recursively walk the new structure, passing
// each name/value pair to a filter function for possible transformation.

                    return typeof filter === 'function' ? walk('', j) : j;
                }

// If the text is not JSON parseable, then a SyntaxError is thrown.

                throw new SyntaxError('parseJSON');
            }
        };
    }();
}

// end @include(JSON.js)


// start @include(JSONTCPConnection.js)
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
    if (typeof(ORBITED_DOMAIN) != "undefined") 
        connUrl.domain = ORBITED_DOMAIN
    // Otherwise use the href domain
    if (typeof(ORBITED_PORT) != "undefined")
        connUrl.port = ORBITED_PORT
    else
        connUrl.port = 7000
    connUrl.path = "/jsonproxy"
    connUrl.qs = ""
    conn.connect(connUrl.render())
//    conn.connect("http://www.test.local:7000/proxy")
}

// end @include(JSONTCPConnection.js)
