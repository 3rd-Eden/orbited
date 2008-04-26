TCPConnection = function(url, session) {
    var self = this
        
    self.readyState = -1
    self.onopen = function(evt) {}
    self.onread = function(evt) {}
    self.onclose = function(evt) {}
    var tcpUrl = null;
    var source = null;
    // NOTE: connect doesn't appear in the html5 spec. We include it here as an
    //       improvement suggestion to be more explicit in when actions such as
    //       attaching the onopen callback should occur. In the spec, connect
    //       is implied when the TCPConnection is instantiated. To make this
    //       implementation work like the spec, just call self.connect() in this
    //       constructor.
    self.connect = function() {
//        if (isSameDomain()) {
            if (self.readyState != -1)
                throw new Error("connect may only be called once");
            self.readyState = 0
            if (session == null || typeof(session) == "undefined")
                getSession()
            else
                attachSSE()
//        }
//        else {
//            var ifr = document.createElement("iframe")
//            ifr.src = "http://www.test.local:8000/_/static/tcp/bridge.html"
//        }
    }
    var getSession = function() {
        var xhr = new XMLHttpRequest();
        xhr.open('PUT', url, true)
        xhr.onreadystatechange = function() {
            switch(xhr.readyState) {
                case 4:
                    if (xhr.status != 200) {
                        self.readyState = 2
                        self.onclose(null) // TODO: pass an event
                    }
                    else {
                        session = xhr.responseText;
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
    
    self.disconnect = function() {
        if (self.readyState == 1) {
            source.removeEventListener("message", receivePayload, false)
            source.removeEventListener("TCPOpen", receiveTCPOpen, false)
            source.removeEventListener("TCPClose", receiveTCPClose, false)
            source.removeEventListener("TCPPing", receiveTCPClose, false)
            source.removeEventSource(tcpUrl)
            document.body.removeChild(source)
            self.readyState = 2
            self.onclose(null) //TODO: pass an event
            xhr = new XMLHttpRequest()
            xhr.open('DELETE', tcpUrl, true)
            xhr.send(null);
        }
        // TODO: disconnect in readyState 0 should also be allowed.
        else {
            throw new Error("not connected")
        }
    }
    self.send = function(data) {
        // TODO: should we hold on to the data until we're sure it went?
        if (self.readyState != 1)
            throw new Error("Invalid readyState to send")
        var xhr = createXHR()
        xhr.open('POST', tcpUrl, true);
        if (source.lastEventId != null && typeof(source.lastEventId) != "undefined") {
            xhr.setRequestHeader('Last-Event-ID', source.lastEventId)
        } 
        xhr.onreadystatechange = function() {
            switch(xhr.readyState) {
                case 4:
                    if (xhr.status != 200) {
                        // TODO: retry?
                    }
            }
        }
        xhr.send(data);
    }
    self.ack_only = function() {
        if (self.readyState != 1)
            throw new Error("Invalid readyState to send")
        var xhr = createXHR()
        xhr.open('POST', tcpUrl, true);
        xhr.setRequestHeader('Tcp', 'ping-response')
        if (source.lastEventId != null && typeof(source.lastEventId) != "undefined") {
            xhr.setRequestHeader('Last-Event-ID', source.lastEventId)
        }
        xhr.onreadystatechange = function() {
            switch(xhr.readyState) {
                case 4:
                    if (xhr.status != 200) {
                        // TODO: retry?
                    }
            }
        }
        xhr.send(null);
    }
    
    var receiveTCPPing = function(evt) {
        self.ack_only();
    }
    var receiveTCPOpen = function(evt) {
        // TODO: use the EventListener interface if available (handleEvent)
        self.readyState = 1
        self.onopen(evt)
    }
    
    var receiveTCPClose = function(evt) {
        // TODO: use the EventListener interface if available (handleEvent)
        self.readyState = 2
        self.onclose(evt)
    }
    
    var receivePayload = function(evt) {
        // TODO: use the EventListener interface if available (handleEvent)
        if (self.readyState == 1)
            self.onread(evt)
        // NOTE: raise an exception if the server misbehaves
        //       this is not in the html5 specification
    
        else 
            throw new Error("Unexpected Data")
        // TODO: throw an exception if we get data we shouldn't?
    }
    
    
    var isSameDomain = function() {
        var origDomain = document.domain
        var targetDomain = extractDomain(url); 
        if (targetDomain == origDomain)
            return true
        var subIndex = targetDomain.indexOf(origDomain)
        if (subIndex == -1)
            throw new Error("Invalid domain")
        return false
    }
    
    var extractDomain = function(url) {
        var protocolIndex = url.indexOf("://")
        if (protocolIndex != -1)
            url = url.slice(protocolIndex+3)
        return url.split("/")[0]
    }    
    var createXHR = function() {
        try { return new ActiveXObject("Msxml2.XMLHTTP"); } catch (e) {}
        try { return new ActiveXObject("Microsoft.XMLHTTP"); } catch (e) {}
        try { return new XMLHttpRequest(); } catch(e) {}
        return null;
    };
    
}