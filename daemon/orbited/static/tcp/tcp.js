TCPConnection = function(url, reliable) {
    // TODO: does Boolean() return false for undefined on all platforms?
    var self = this
    self.reliable = Boolean(reliable)
        
    self.readyState = -1
    self.onopen = function(evt) {}
    self.onread = function(evt) {}
    self.onclose = function(evt) {}

    var source = null;
    // NOTE: connect doesn't appear in the html5 spec. We include it here as an
    //       improvement suggestion to be more explicit in when actions such as
    //       attaching the onopen callback should occur. In the spec, connect
    //       is implied when the TCPConnection is instantiated.
    self.connect = function() {
        if (self.readyState != -1)
            throw new Error("connect may only be called once");
        self.readyState = 0
        source = document.createElement("event-source")
        source.addEventListener("message", receivePayload, false)
        source.addEventListener("TCPOpen", receiveTCPOpen, false)
        source.addEventListener("TCPClose", receiveTCPClose, false)
        source.addEventSource(url)
        document.body.appendChild(source)
    }
    self.disconnect = function() {
        if (self.readyState == 1) {
            source.removeEventSource(url)
            self.readyState = 2
            self.onclose(null) //TODO: pass an event
            xhr = new XMLHttpRequest()
            xhr.open('DELETE', url, true)
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
        xhr.open('POST', url, true);
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
    var createXHR = function() {
        try { return new ActiveXObject("Msxml2.XMLHTTP"); } catch (e) {}
        try { return new ActiveXObject("Microsoft.XMLHTTP"); } catch (e) {}
        try { return new XMLHttpRequest(); } catch(e) {}
        return null;
    };
    
}