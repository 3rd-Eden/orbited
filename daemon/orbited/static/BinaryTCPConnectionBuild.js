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
            output = ""
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
        
        var connUrl = new URL(_url)
        switch(browser) {
//            case 'firefox':
            default:
                source = document.createElement("event-source")
                source.addEventListener("message", receivePayload, false)
                source.addEventListener("TCPOpen", receiveTCPOpen, false)
                source.addEventListener("TCPClose", receiveTCPClose, false)
                source.addEventListener("TCPPing", receiveTCPPing, false)
                connUrl.setQsParameter('transport', 'sse')
//                connUrl.hash = "0"
                url = connUrl.render()
                console.log('addEventsource: ' + url)
                source.addEventSource(url)
                document.body.appendChild(source)
                break;
/*            default:
                source = document.createElement("iframe")
                source.src = url + "?transport=htmlfile#0"
                document.body.appendChild(source)
                break;
*/
        }
    }

    self.destroy = function() {
        switch(browser) {
/*            default:
                document.body.removeChild(source)
                break;
            case 'firefox2': */
            default:
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
isOpera = false
if((typeof window.addEventStream) === 'function') {
//    console = {}
//    console.log = function(data) { alert(data); print(data) }
    isOpera = true
}
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
        if (name == "event-source") {
            alert('createElehttp://operawiki.info/OperaPerformancement')
            var SSEHandler = new FxSSE(obj);
        }
        return obj
    }
}, true);

FxSSE = function(source) {
    var self = this;
    xhr = null;
    var retry = 3000;
    var id = null;
    var offset = 0;
//    var next_boundary = -1;
    var boundary = "\n"
    var lineQueue = []
    var origin = "" // TODO: derive this from the src argument 
    var src = null;http://operawiki.info/OperaPerformance
    var origSrc = null;
    var reconnectTimer = null;
    var operaTimer = null;
//    source.lastEventId = null;
    
    source.addEventSource = function(eventSrc) {
//        console.log('addEventSource: ' + eventSrc);
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
//        console.log('open to src: ' + src)
        xhr.open('GET', src, true);
        if (id != null) {
            xhr.setRequestHeader('Last-Event-ID', id)
        }
        else {
        }
        xhr.onreadystatechange = function() {
            console.log(xhr.readyState)
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
        console.log('setting timer and sending');
        operaTimer = setInterval(process, 50)
        xhr.send(null);
    }
    var reconnect = function() {
        console.log('reconnect!')
        clearInterval(operaTimer)
        operaTimer = null;
        // TODO: reuse this xhr connection
//        xhr = null;
        offset = 0
        reconnectTimer = setTimeout(connect, retry)
    }

    var process = function() {
//        console.log('process')
        try {
            var stream = xhr.responseText
        }
        catch(e) {
//            console.log('stream not ready...')
            return
        }
//        if (stream.slice(offset).length > 0)
//            console.log('stream: ' + stream.slice(offset))
        if (stream.length < offset) { // in safari the offset starts at 256 {
//            console.log('offset not met')
            return 
        }
        var next_boundary = stream.indexOf(boundary, offset);
        if (next_boundary == -1) {
//            console.log('no more boundaries')
            return
        }
        var line = stream.slice(offset, next_boundary)
        offset = next_boundary + boundary.length
        if (line.length == 0 || line == "\r")
            dispatch()
        else
            lineQueue.push(line) // TODO: is this cross-browser?                
        // TODO: use a while loop here. We don't want a stack overflow
//        console.log('reschedule process')
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
        console.log('url: ' + _url)
        if (self.readyState != -1 && self.readyState != 2)
            throw new Error("connect may only be called on a closed socket");
        self.readyState = 0
        var testUrl = new URL(_url);
        
        if (testUrl.isSameDomain(location.href)) {
            alert('same domain');
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
        alert('attach transport')
        tcpUrl = url
        transport = new CometTransport()
        transport.receivePayload = receivePayload;
        transport.receiveTCPOpen = receiveTCPOpen;
        transport.receiveTCPClose = receiveTCPClose;
        transport.receiveTCPPing = receiveTCPPing;
        console.log('transport.connect: ' + tcpUrl)
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


// start @include(hex.js)
hexChars = '0123456789ABCDEF'

hexToBase10 = { }
base10ToHex = { }
for (var i = 0; i < hexChars.length; ++i) {
    hexToBase10[hexChars[i]] = i
    base10ToHex[i] = hexChars[i]
}

hexToBytes = function(str) {
    if (str.length == 0)
        return []
    if (str.length % 2 != 0)
        throw new Error ("Invalid Hex String (must be pairs)")
    var output = []
    for (var i =0; i < str.length; i+=2) {
        var val = (hexToBase10[str[i]] << 4) + (hexToBase10[str[i+1]])
        output.push(val)
    }
    return output
}


// TODO: why doesn't this work? 
bytesToHex = function(bytes) {
    var output = []
    for (var i = 0; i < bytes.length; ++i) {
        var val = bytes[i].toString(16)
        if (val.length == 1)
            output.push("0")
        output.push(val)
    }
    return output.join("")
}
/*
bytesToHex = function(bytes) {
    var output = []
    for (var i = 0; i < bytes.length; ++i) {
        var byte = bytes[i]
        var hex1 = byte >> 4
        output.push(base10ToHex[hex1])
        output.push(base10ToHex[byte - (hex1 << 4)])
    }
    return output.join("")
}
*/
// end @include(hex.js)


// start @include(unicode.js)
fromBin = function(bin) { val = 0; for (var i = bin.length-1; i >= 0; i--) { if (bin[bin.length-i-1] == '1') { val += Math.pow(2, i) } } return val }

charByteLength = function(byte) {
    if ((byte & 128) == 0)
        return 1
    if ((byte & 240) == 240)
        return 4
    if ((byte & 224) == 224)
        return 3
    if ((byte & 192) == 192)
        return 2
    throw new Error("Invalid UTF-8 encoded data...")
}

bytesToUTF8 = function(bytes) {
    var output = []
    for (var i = 0; i < bytes.length; ++i) {
        var startByte = bytes[i]
        var val = null;
        var len = charByteLength(startByte) 
        switch (len) {
            case 1:
                val = bytes[i];
                break;
            case 2:
                val = ((bytes[i] - 192) << 6)  + (bytes[i+1] - 128)
                break
            case 3:
                val = ((bytes[i] - 224) << 12) + ((bytes[i+1] - 128) << 6) + (bytes[i+2] - 128)
                break
            case 4:
                val = ((bytes[i] - 240) << 18) + ((bytes[i+1] - 128) << 12) + ((bytes[i+2] - 128) << 6) + (bytes[i+3] - 128)
                break
        }
        i += (len -1)
        output.push(String.fromCharCode(val))
    }
    return output.join("")
}


UTF8ToBytes = function(str) {
    var output = []
    for (var i = 0; i < str.length; ++i) {
        var val = str.charCodeAt(i)
        if (val < 128) { // largest 1-byte unicode value
            output.push(val)
            continue
        }
        if (val < 2047) { // largest 2-byte unicode value
            var firstByte = (val >> 6) + 192
            var secondByte = val - (firstByte << 6)
            output.push(firstByte)
            output.push(secondByte)
            continue
        }
        if (val < 65535) { // largest 3-byte unicode value
            var firstChunk = (val >> 12)
            var temp1 = (firstChunk << 12)
            var secondChunk = (val - temp1) >> 6
            var thirdChunk = (val - temp1 - (secondChunk << 6))
            var firstByte = firstChunk + 224
            var secondByte = secondChunk + 128
            var thirdByte = thirdChunk + 128
            output.push(firstByte)
            output.push(secondByte)
            output.push(thirdByte)
            continue
        }
        if (val < 2097151 ) { // largest 4-byte unicode value
            var firstChunk = (val >> 18)
            var temp1 = (firstChunk << 18)
            var secondChunk = (val - temp1) >> 12
            var temp2 = secondChunk << 12
            var thirdChunk = (val - temp1 - temp2) >> 6
            var fourthChunk = (val - temp1 - temp2 - (thirdChunk << 6))
            var firstByte = firstChunk + 240
            var secondByte = secondChunk + 128
            var thirdByte = thirdChunk + 128
            var fourthByte = fourthChunk + 128
            output.push(firstByte)
            output.push(secondByte)
            output.push(thirdByte)
            output.push(fourthByte)
            continue
        }
        throw new Error("Invalid UTF-8 string")
    }
    return output
}

    orig = "당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 "
orig2 = orig + orig
//orig2 = orig2 + orig2 + orig2
//orig2 = orig2 + orig2
orig3 = UTF8ToBytes(orig2)
benchmark = function(f, arg) {
    start = new Date()
        f(arg);
    end = new Date();
    return end - start
}

translateKorean = function(orig) {
//    for (var i = 0; i < 1; ++i) {
        bytesToUTF8(UTF8ToBytes(orig))
//    }
}

translateKorean1 = function(orig) {
//    for (var i = 0; i < 1; ++i) {
        UTF8ToBytes(orig)
//    }
}
translateKorean2 = function(orig) {
//    for (var i = 0; i < 1; ++i) {
        bytesToUTF8(orig)
//    }
}

onload = function() {
    alert('starting tests')
    document.body.innerHTML += benchmark(translateKorean, orig2) + '<br>\n'
    document.body.innerHTML += benchmark(translateKorean1, orig2) + '<br>\n'
    document.body.innerHTML += benchmark(translateKorean2, orig3) + '<br>\n'    
    alert('tests finished')
}

// end @include(unicode.js)


// start @include(BinaryTCPConnection.js)
BinaryTCPConnection = function(domain, port) {
    var self = this;
    self.onopen = function() { }
    self.onclose = function() { }
    self.onread = function() { }
    self.readyState = 0

    var conn = new BaseTCPConnection()

    self.send = function(data) {
        conn.send(bytesToHex(data));
    }
    conn.onread = function(evt) {
        evt.data = hexToBytes(evt.data);
        self.onread(evt);
    }
    conn.onclose = function(evt) {
        self.readyState = conn.readyState
        self.onclose(evt);
    }
    conn.onopen = function(evt) {
        console.log('onopen!')
        self.readyState = conn.readyState
        conn.send(domain + ":" + port)
        self.onopen(evt)
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
    alert('connecting to: ' + connUrl.render())
    conn.connect(connUrl.render())
}

// end @include(BinaryTCPConnection.js)
