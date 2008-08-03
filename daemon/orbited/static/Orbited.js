(function() {

var HANDSHAKE_TIMEOUT = 30000
var RETRY_INTERVAL = 250
var RETRY_TIMEOUT = 30000

Orbited = {}

Orbited.settings = {}
Orbited.settings.hostname = document.domain
Orbited.settings.port = (location.port.length > 0) ? location.port : 80
Orbited.settings.protocol = 'http'

// Orbited CometSession Errors
Orbited.Errors = {}
Orbited.Errors.ConnectionTimeout = 101
Orbited.Errors.InvalidHandshake = 102
Orbited.Errors.UserConnectionReset = 103

Orbited.Statuses = {}
Orbited.Statuses.ServerClosedConnection = 201

if (typeof(console) != "undefined" && typeof(console.log) != "undefined") {
    Orbited.log = console.log;
}
else {
    Orbited.log = function() { }
}

Orbited.util = {}

Orbited.util.browser = null;
if (typeof(ActiveXObject) != "undefined") {
    Orbited.util.browser = 'ie'
} else if (navigator.product == 'Gecko' && window.find && !navigator.savePreferences) {
    Orbited.util.browser = 'firefox'
} else if((typeof window.addEventStream) === 'function') {
    Orbited.util.browser = 'opera'
} 

Orbited.CometTransports = {}

Orbited.util.chooseTransport = function() {
    var choices = []
    for (var name in Orbited.CometTransports) {
        var transport = Orbited.CometTransports[name];
        if (typeof(transport[Orbited.util.browser]) == "number") {
            choices.push(transport)
        }
    }
    // TODO: sort the choices by the values of transport[Orbited.util.browser]
    //       and return the transport with the highest value.
//    return XHRStream
    return choices[0]
}





Orbited.CometSession = function() {
    var self = this;

    // The readyState values
    var states = {
        INITIALIZED: 1,
        OPENING: 2,
        OPEN: 3,
        CLOSING: 4,
        CLOSED: 5
    }

    self.readyState = states.INITIALIZED
    self.onopen = function() {}
    self.onread = function() {}
    self.onclose = function() {}
    var sessionUrl = null;
    var sessionKey = null;
    var sendQueue = []
    var packetCount = 0;
    var xhr = null;
    var handshakeTimer = null;
    var cometTransport = null;
    var lastPacketId = 0
    var sending = false;

    /*
     * self.open can only be used when readyState is INITIALIZED. Immediately
     * following a call to self.open, the readyState will be OPENING until a
     * connection with the server has been negotiated. self.open takes a url
     * as a single argument which desiginates the remote url with which to
     * establish the connection.
     */
    self.open = function(_url) {
        self.readyState = states.OPENING;
        xhr = new XMLHttpRequest();
        xhr.open('GET', _url, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    sessionKey = xhr.responseText;
                    sessionUrl = new Orbited.URL(_url)
                    // START new URL way
//                    sessionUrl.extendPath(sessionKey)
                    // END: new URL way

                    // START: old URL way
                    if (sessionUrl.path[sessionUrl.path.length] != '/')
                        sessionUrl.path += '/'
                    sessionUrl.path += sessionKey
                    // END: old Url way
                    var transportClass = Orbited.util.chooseTransport()
                    cometTransport = new transportClass();
                    cometTransport.onReadFrame = transportOnReadFrame;
                    cometTransport.onclose = transportOnClose;
                    cometTransport.connect(sessionUrl.render())
                }
                
                else {
                    xhr = null;
                    self.readyState = states.CLOSED;
                    self.onclose(Orbited.Errors.InvalidHandshake)
                }
            }
        }
        xhr.send(null);
    }
    
    /* 
     * self.send is only callable when readyState is OPEN. It will queue the data
     * up for delivery as soon as the upstream xhr is ready.
     */
    self.send = function(data) {
        if (self.readyState != states.OPEN) {
            throw new Error("Invalid readyState")
        }
        sendQueue.push([++packetCount, "data", data])
        if (!sending) {
            doSend()
        }
    }

    /* 
     * self.close sends a close frame to the server, at the end of the queue.
     * It also sets the readyState to CLOSING so that no further data may be
     * sent. onclose is not called immediately -- it waits for the server to
     * send a close event.
     */
    self.close = function() {
        if (self.readyState != states.OPEN) {
            throw new Error("Invalid readyState")
        }
        // TODO: don't have a third element (remove the null).
        sendQueue.push([++packetCount, "close", null])
        if (!sending) {
            doSend()
        }
        self.readyState = states.CLOSING;
    }

    /* self.reset is a way to close immediately. The send queue will be discarded
     * and a close frame will be sent to the server. onclose is called immediately
     * without waiting for a reply from the server.
     */
    self.reset = function() {
        var origState = self.readyState
        self.readyState = states.CLOSED;
        switch(origState) {
            case states.INITIALIZED:
                self.onclose(Orbited.Errors.UserConnectionReset);
                break;
            case states.OPENING:
                xhr.onreadystatechange = function() {};
                xhr.abort();
                self.onclose();
                break;
            case states.OPEN:
                self.sendQueue = []
                self.sending = false;
                if (xhr.readyState < 4) {
                    xhr.onreadystatechange = function() {}
                    xhr.abort();
                }
                doClose(Orbited.Errors.UserConnectionReset);
                // TODO: send close frame
                //       -mcarter 7-29-08
                break;
            case states.CLOSING:
                // TODO: Do nothing here?
                //       we need to figure out if we've attempted to send the close
                //       frame yet or not If not, we do something similar to case
                //       states.OPEN. either way, we should kill the transport and
                //       trigger onclose
                //       -mcarter 7-29-08                
                break;

            case states.CLOSED:
                break
        }
    }

    var transportOnReadFrame = function(frame) {
        if (!isNaN(frame.id)) {
            lastPacketId = Math.max(lastPacketId, frame.id);
        }
        switch(frame.name) {
            case 'close':
                if (self.readyState < states.CLOSED) {
                    doClose(Orbited.Statuses.ServerClosedConnection)
                }
                break;
            case 'data':
                self.onread(frame.args[0]);
                break;
            case 'open':
                if (self.readyState == states.OPENING) {
                    self.readyState = states.OPEN;
                    self.onopen();
                }
                else {
                    //TODO Throw and error?
                }
                break;
            case 'ping':
                // TODO: don't have a third element (remove the null).
                sendQueue.push([++packetCount, "ping", null])
                if (!sending) {
                    doSend()
                }
                
        }
    }
    var transportOnClose = function() {
        Orbited.log('transportOnClose');
        if (self.readyState < states.CLOSED) {
            doClose(Orbited.Statuses.ServerClosedConnection)
        }
    }        
    var encodePackets = function(queue) {
        //TODO: optimize this.
        var packets = []
        
        for (var i =0; i < queue.length; ++i) {
            var p = queue[i];
            packets.push(p[0] + "_A" + p[1] + "_A" + p[2] + "_P")
        }
        return packets.join("")
    }

    var doSend = function(retries) {
        if (typeof(retries) == "undefined") {
            retries = 0
        }
        if (retries*RETRY_INTERVAL >= RETRY_TIMEOUT) {
            doClose(Orbited.Errors.ConnectionTimeout)
            sending = false;
            return
        }
        if (sendQueue.length == 0) {
            sending = false;
            return
        }
        
        var numSent = sendQueue.length
        sessionUrl.setQsParameter('ack', lastPacketId)
        xhr.open('POST', sessionUrl.render(), true)
        xhr.send(encodePackets(sendQueue))
        xhr.onreadystatechange = function() {
            switch(xhr.readyState) {
                case 4:
                    if (xhr.status == 200) {
                        sendQueue.splice(0, numSent)
                        return doSend();
                    }
                    else {
                        //TODO: implement retry back-off;
                        window.setTimeout(
                            function() {
                                doSend(++retries);
                            },
                            RETRY_INTERVAL
                        );
                    }
            }
        }
    }
    
    var doClose = function(code) {
        Orbited.log('doClose', code)
        self.readyState = states.CLOSED;
        cometTransport.onReadFrame = function() {}
        if (cometTransport != null && cometTransport.readyState < 2) {
            cometTransport.close()
        }
        self.onclose(code);

    }

}

Orbited.TCPSocket = function() {
    var self = this;

    // The readyState values
    var states = {
        INITIALIZED: 1,
        OPENING: 2,
        OPEN: 3,
        CLOSING: 4,
        CLOSED: 5
    }
    self.readyState = states.INITIALIZED
    self.onopen = function() { }
    self.onread = function() { }
    self.onclose = function() { }

    var session = null;
    var binary = false;
    var handshakeState = null;
    var hostname = null;
    var port = null;
    /* self.open attempts to establish a tcp connection to the specified remote
     * hostname on the specified port. When specified as true, the optional
     * argument, isBinary, will cause onread to return byte arrays, and send
     * will only accept a btye array.
     */
    self.open = function(_hostname, _port, isBinary) {
        if (self.readyState != states.INITIALIZED) {
            // TODO: allow reuse from readyState == states.CLOSED?
            //       Re-use makes sense for xhr due to memory concerns, but
            //       probably not for tcp sockets. How often do you reconnect
            //       in the same page?
            //       -mcarter 7-30-08
            throw new Error("Invalid readyState");
        }
        // handle isBinary undefined/null case
        binary = !!isBinary;
        self.readyState = states.OPENING;
        hostname = _hostname;
        port = _port;
        session = new Orbited.CometSession()
        var sessionUrl = new Orbited.URL('/tcp')
        sessionUrl.domain = Orbited.settings.hostname
        sessionUrl.port = Orbited.settings.port
        sessionUrl.protocol = Orbited.settings.protocol
        session.open(sessionUrl.render())
        session.onopen = sessionOnOpen;
        session.onread = sessionOnRead;
        session.onclose = sessionOnClose;
        handshakeState = "initial";
    }

    self.close = function() {
        if (self.readyState != states.OPEN && self.readyState != states.OPENING) {
            throw new Error("Invalid readyState");
        }
        session.close();
    }
    
    /* self.reset closes the connection from this end immediately. The server
     * may be notified, but there is no guarantee. The main purpose of the reset
     * function is for a quick teardown in the case of a user navigation.
     * if reset is not called when IE navigates, for instance, there will be 
     * potential issues with future TCPSocket communication.
     */
    self.reset = function() {
        if (self.readyState != states.OPEN && self.readyState != states.OPENING) {
            throw new Error("Invalid readyState");
        }
        session.reset();
    }

    self.send = function(data) {
        if (binary) {
            if (!(data instanceof Array)) {
                throw new Error("invalid payload: binary mode is set");
            }
            session.send(encodeBinary(data))
        }
        else {
            session.send(data)
        }
       }

    // TODO: how about base64, or at least hex encoding?
    //       -mcarter 2-30-08        
    var encodeBinary = function(data) {
        return data.join(",")
    }
    var decodeBinary = function(data) {
        data = data.split(",")
        for (var i = 0; i < data.length; ++i) {
            data[i] = parseInt(data[i])
        }
        return data
    }

    var sessionOnRead = function(data) {
        switch(self.readyState) {
            case states.OPEN:
                binary ? self.onread(decodeBinary(data)) : self.onread(data)
                break;
            case states.OPENING:
                switch(handshakeState) {
                    case 'initial':
                        var result = (data[0] == '1')
                        if (!result) {
                            var errorCode = data.slice(1,4)
                            sessionOnClose = function() {}
                            session.close()
                            session = null;
                            self.onclose(parseInt(errorCode))
                        }
                        if (result) {
                            self.readyState = states.OPEN
                            self.onopen();
                        }
                        break;
                }
                break;
        }
    }
    
    var sessionOnOpen = function(data) {
        // TODO: TCPSocket handshake
        session.send((binary ? '1' : '0') + hostname + ':' + port)
        handshakeState = 'initial'
    }
    
    var sessionOnClose = function(status) {
        Orbited.log('sessionOnClose');
        // If we are in the OPENING state, then the handshake code should
        // handle the close
        if (self.readyState >= states.OPEN) {
            self.readyState = states.CLOSED
            session = null;
            self.onclose(status);
        }
    }
}





/* Comet Transports!
 */

Orbited.CometTransports.XHRStream = function() {
    var self = this;
    var HEARTBEAT_TIMEOUT = 15000;
    // Support Browsers

    var ESCAPE = "_"
    var PACKET_DELIMITER = "_P"
    var ARG_DELIMITER = "_A"
    var url = null;
    xhr = null;
    var ackId = null;
    var offset = 0;
    var heartbeatTimer = null;
    var retryTimer = null;
    retryInterval = 50
    self.readyState = 0
    self.onReadFrame = function(frame) {}
    self.onread = function(packet) { self.onReadFrame(packet); }
    self.onclose = function() { }

    self.close = function() {
        if (self.readyState != 1) {
            throw new Error("Invalid readyState to close XHRStream")
        }
        if (xhr != null && (xhr.readyState > 1 || xhr.readyState < 4)) {
            xhr.onreadystatechange = function() { }
            xhr.abort()
            xhr = null;        
        }
        self.readyState = 2
        window.clearTimeout(heartbeatTimer);
        window.clearTimeout(retryTimer);
        self.onclose();
    }

    self.connect = function(_url) {
        if (self.readyState == 1) {
            throw new Error("Already Connected")
        }
        url = new Orbited.URL(_url)
        if (xhr == null) {
            if (url.isSameDomain(location.href)) {
                xhr = new XMLHttpRequest();
            }
            else {
                xhr = new XSubdomainRequest(url.domain, url.port);
            }
        }
        url.path += '/xhrstream'
//        url.setQsParameter('transport', 'xhrstream')
        self.readyState = 1
        open()
    }
    open = function() {
        try {
            if (typeof(ackId) == "number") {
                url.setQsParameter('ack', ackId)
            }
    
            xhr.open('GET', url.render(), true)
            xhr.onreadystatechange = function() {
                Orbited.log(xhr.readyState);
                switch(xhr.readyState) {
                    case 2:
//                        heartbeatTimer = window.setTimeout(heartbeatTimeout, HEARTBEAT_TIMEOUT);                    
                        // If we can't get the status, then we didn't actually
                        // get a valid xhr response -- we got a network error
                        try {
                            var status = xhr.status
                        }
                        catch(e) {
                            return
                        }
                        // If we got a 200, then we're in business
                        if (status == 200) {
                            heartbeatTimer = window.setTimeout(heartbeatTimeout, HEARTBEAT_TIMEOUT);
                            var testtimer = heartbeatTimer;
                        }
                        // Otherwise, case 4 should handle the reconnect,
                        // so do nothing here.
                        break;
                    case 3:
                        // If we can't get the status, then we didn't actually
                        // get a valid xhr response -- we got a network error
                        try {
                            var status = xhr.status
                        }
                        catch(e) {
                            return
                        }
                        // We successfully established a connection, so put the
                        // retryInterval back to a short value
                        if (status == 200) {
                            retryInterval = 50;
                            process();
                        }
                        break;
                    case 4:
                        try {
                            xhr.status
                        }
                        catch(e) {
                            // Expoential backoff: Every time we fail to 
                            // reconnect, double the interval. 
                            retryInterval *= 2;
                            Orbited.log('retryInterval', retryInterval)
                            window.clearTimeout(heartbeatTimer);
                            window.setTimeout(reconnect, retryInterval)
                            return;
                        }

                        switch(xhr.status) {
                            case 200:
                                process();
                                offset = 0;
                                setTimeout(open, 0)
                                window.clearTimeout(heartbeatTimer);
                                break;
                            case 404:
                                self.close();
                            default:
                                self.close();
                        }
                }
            }
            xhr.send(null);
        }
        catch(e) {
            self.close()
        }
    }

    var reconnect = function() {
        Orbited.log('reconnect...')
        if (xhr.readyState < 4 && xhr.readyState > 0) {
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4) {
                    reconnect();
                }
            }
            Orbited.log('do abort..')
            xhr.abort();
            window.clearTimeout(heartbeatTimer);            
        }
        else {
            Orbited.log('open...')
            offset = 0;
            setTimeout(open, 0)
        }
    }
    var process = function() {
        var stream = xhr.responseText;
        Orbited.log('buffer', stream.slice(offset).length, stream.slice(offset))
        xkcd = stream.slice(offset)
        while (true) {
            if (stream.length <= offset) {
                return;
            }
            // Any data counts as a heartbeat
            receivedHeartbeat()

            // ignore leading whitespace, such as at the start of an xhr stream
            while (stream[offset] == ' ') {
                offset += 1
            }
            // If a frame starts with an 'x', then its an actual heartbeat
            // so discard it.
            if (stream[offset] == 'x') {
                Orbited.log('heartbeat')
                offset += 1
                continue
            }
            
            else {
                Orbited.log('activity', stream[offset])
            }
            var nextBoundary = stream.indexOf(PACKET_DELIMITER, offset);
            Orbited.log('partial', stream.slice(offset, nextBoundary));
            if (nextBoundary == -1)
                return;
            var packet = stream.slice(offset, nextBoundary);
            offset = nextBoundary + PACKET_DELIMITER.length
            receivedPacket(packet)
        }
    }
    var receivedHeartbeat = function() {
        window.clearTimeout(heartbeatTimer);
        Orbited.log('clearing heartbeatTimer', heartbeatTimer)
        heartbeatTimer = window.setTimeout(function() { Orbited.log('timer', testtimer, 'did it'); heartbeatTimeout();}, HEARTBEAT_TIMEOUT);
        var testtimer = heartbeatTimer;

        Orbited.log('heartbeatTimer is now', heartbeatTimer)
    }
    var heartbeatTimeout = function() {
        Orbited.log('heartbeat timeout... reconnect')
        reconnect();
    }
    var receivedPacket = function(packetData) {
        var args = packetData.split(ARG_DELIMITER)
        var testAckId = parseInt(args[0])
        if (!isNaN(testAckId)) {
            ackId = testAckId
        }
        packet = {
            id: testAckId,
            name: args[1],
            args: args.slice(2)
        }
        self.onread(packet)
    }
}
// XHRStream supported browsers
Orbited.CometTransports.XHRStream.firefox = 1.0


/* This is an old implementation of the URL class. Jacob is cleaning it up
 * mcarter, 7-30-08
 */
Orbited.URL = function(_url) {
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
        _url = new Orbited.URL(_url)

        if (!_url.domain || !self.domain)
            return true
        return (_url.port == self.port && _url.domain == self.domain)
    }
    self.isSameParentDomain = function(_url) {
        _url = new Orbited.URL(_url)
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



})();
