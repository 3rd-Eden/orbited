TCPConnection = function() {
    var self = this;
    self.readyState = -1
    self.onopen = function(evt) {}
    self.onread = function(evt) {}
    self.onclose = function(evt) {}    
    var url = null;
    var tcpUrl = null;
    var session = null;
    var source = null;
    var xhr = null;
    var lastEventId = null;

    self.connect = function(_url, _session) {
//        alert('connecting: ' + _url + ', ' + _session)
        if (self.readyState != -1 && self.readyState != 2)
            throw new Error("connect may only be called on a closed socket");
        self.readyState = 0
        var testUrl = new URL(_url);
        if (testUrl.isSameDomain(location.href)) {
            xhr = createXHR();
        }
        else if (testUrl.isSameParentDomain(location.href)) {
//            alert('using XSubdomainRequest')
            xhr = new XSubdomainRequest(testUrl.domain, testUrl.port)
        }
        else {
            throw new Error("Invalid domain. TCPConnection instances may only connect to same-domain or sub-domain hosts.")
        }
        session = _session;
//        source = document.createElement("event-source")
        url = testUrl.render()
        if (session == null || typeof(session) == "undefined") {
//            alert('getSession')
            getSession()
        }
        else {
//            alert('attachSSE')
            attachSSE()
        }
    }
    
    var getSession = function() {
        xhr.open('POST', url, true)
        xhr.onreadystatechange = function() {
            switch(xhr.readyState) {
                case 4:
                    if (xhr.status != 200) {
//                        alert('no good');
                        self.readyState = 2
                        self.onclose(null) // TODO: pass an event
                    }
                    else {
                        session = xhr.responseText;
//                        alert('got session: ' + session)
                        attachSSE();
                    }
            }
        }
        xhr.send(null)
    }
    var attachSSE = function() {
        var path = url.split('?', 1)[0]
        var qs = url.slice(path.length+1)
        if (path[path.length-1] != "/")
            path += '/'
        tcpUrl = path + session
        if (qs.length > 0)
            tcpUrl += "?" + qs

        source = document.createElement("event-source")
        source.addEventListener("message", receivePayload, false)
        source.addEventListener("TCPOpen", receiveTCPOpen, false)
        source.addEventListener("TCPClose", receiveTCPClose, false)
        source.addEventListener("TCPPing", receiveTCPPing, false)
        source.addEventSource(tcpUrl)
        document.body.appendChild(source)
    }

    self.send = function(data) {
        var payload = ""
        xhr.open('POST', tcpUrl, true);
        xhr.setRequestHeader('Content-Type', 'text/event-stream')
        var payload = "data:" + data.split("\n").join("\ndata:") + "\n\n"
        if (lastEventId != null && typeof(lastEventId) != "undefined") {
            payload += "event:TCPAck\ndata:" + lastEventId + "\n\n"
        } 
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

    self.ack_only = function() {
        var payload = ""
        xhr.open('POST', tcpUrl, true);
        xhr.setRequestHeader('Content-Type', 'text/event-stream')
        payload = "event:TCPAck\ndata:" + lastEventId + "\n\n"
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

    var receiveTCPPing = function(evt) {
        lastEventId = evt.lastEventId;
        self.ack_only();
    }
    var receiveTCPOpen = function(evt) {
        // TODO: use the EventListener interface if available (handleEvent)
        lastEventId = evt.lastEventId;
        self.readyState = 1
        self.onopen(evt)
    }
    var receiveTCPClose = function(evt) {
        // TODO: use the EventListener interface if available (handleEvent)
        lastEventId = evt.lastEventId;
        self.readyState = 2
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
