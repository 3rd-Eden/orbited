
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
    var postId = 0;
    self.connect = function(_url) {
        if (self.readyState != -1 && self.readyState != 2)
            throw new Error("connect may only be called on a closed socket");
        self.readyState = 0
        url = new URL(_url);
        
        if (url.isSameDomain(location.href)) {
            xhr = createXHR();
        }

        else if (url.isSameParentDomain(location.href)) {
            var path = url.path
            if (path[path.length-1] != '/')
                path += '/'
            path += 'static/XSubdomainBridge.html'
            xhr = new XSubdomainRequest(url.domain, url.port, path)
        }
        else {
            throw new Error("Invalid domain. BaseTCPConnection instances may only connect to same-domain or sub-domain hosts.")
        }
        getSession();
    }

   var getSession = function() {
       xhr.open('POST', url.render(), true);
       xhr.onreadystatechange = function() {
            switch(xhr.readyState) {
                case 4:
                    switch(xhr.status) {
                        case 201:
                            var newUrl = new URL(xhr.getResponseHeader('Location'))
                            tcpUrl = newUrl.render()
                            receiveTCPOpen();
                            attachTransport();
                            break;
                        // 200 "redirect" is Untested
                        case 200:
                            var newUrl = new URL(xhr.getResponseHeader('Location'))
                            var curUrl = new URL(url)
                            curUrl.merge(newUrl)
                            tcpUrl = curUrl.render()
                            getSession();
                            break;
                        default:
                            doClose();
                            break;
                    }
            }
        }
        xhr.send(null)
    }
    var attachTransport = function() {
        transport = new CometTransport()
        transport.receivePayload = receivePayload;
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
            payload += "data:" + data.split("\n").join("\r\ndata:") + "\r\n" + "id: " + (++postId).toString() + "\r\n\r\n"
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
        // TODO: use the EventListener interface if available (handleEvent)
        lastEventId = evt.lastEventId;
        self.readyState = 1
        self.onopen(evt);
        resetPingTimer();
    }
    var receiveTCPClose = function(evt) {
        // TODO: use the EventListener interface if available (handleEvent)
        lastEventId = evt.lastEventId;
        doClose(evt);
    }
    var doClose = function(evt) {
        self.readyState = 2
        if (transport != null)
            transport.destroy();
        self.onclose(evt)
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
