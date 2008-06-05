
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
