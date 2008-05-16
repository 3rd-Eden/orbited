//document.domain = document.domain;
CURL = function(url) {
    var self = this;
    var protocolIndex = url.indexOf("://")
    if (protocolIndex != -1)
        self.protocol = url.slice(0,protocolIndex)
    else
        protocolIndex = 0
    var domainIndex = url.indexOf('/', protocolIndex+3)
    if (domainIndex == -1)
        domainIndex=url.length
    var hashIndex = url.indexOf("#", domainIndex)
    if (hashIndex != -1)
        self.hash = url.slice(hashIndex+1)
    else
        hashIndex = url.length
    var uri = url.slice(domainIndex, hashIndex)
    var qsIndex = uri.indexOf('?')
    self.path = uri.slice(0, qsIndex)
    self.qs = uri.slice(qsIndex+1)
    if (self.path == "")
        self.path = "/"
    var domain = url.slice(protocolIndex+3, domainIndex)
    var portIndex = domain.indexOf(":")
    if (portIndex == -1) {
        self.port = 80
        portIndex = domain.length
    }
    else {
        self.port = parseInt(domain.slice(portIndex+1))
    }
    if (isNaN(this.port))
        throw new Error("Invalid url")
    self.domain = domain.slice(0, portIndex)
    self.render = function() {
        var output = ""
        if (typeof(self.protocol) != "undefined")
            output += self.protocol + "://"
        output += self.domain
        if (self.port != 80)
            output += ":" + self.port
        output += self.path
        output += '?' + self.qs
        if (typeof(self.hash) != "undefined")
            output += "#" + self.hash
        return output
    }
    self.isSameDomain = function(url) {
        url = new CURL(url)
        return (url.port == self.port && url.domain == self.domain)
    }
    self.isSameParentDomain = function(url) {
        url = new CURL(url)
        var parts = document.domain.split('.')
        var orig_domain = document.domain
        for (var i = 0; i < parts.length-1; ++i) {
            var new_domain = parts.slice(i).join(".")
            if (orig_domain == new_domain)
                return true;
        }
    }

}

TCPConnection = function() {
//    var BRIDGE_LOCATION = location.href ... split of /tcp.js
//    var BRIDGE_LOCATION = "/_/static/tcp/tcpbridgeiframe.html"
    var self = this;
    self.readyState = -1
    self.onopen = function(evt) {}
    self.onread = function(evt) {}
    self.onclose = function(evt) {}    
    var url = null;
    var session = null;
    var pull_queue = null;
    var ifr = null;
    var communicator = null;
    var lastEventId = null;
    self.connect = function(_url, _session) {
        if (self.readyState != -1 && self.readyState != 2)
            throw new Error("connect may only be called on a closed socket");
        url = new CURL(_url);
        session = _session;
        if (url.isSameDomain(location.href)) {
            communicator = new TCPConnection.Communicator(true, receive);
            communicator.connect(url.render(), _session)
        }
        else if (url.isSameParentDomain(location.href)) {
            print("a")
            if (typeof(TCPConnection.count) == "undefined") {
                TCPConnection.count = 0
                TCPConnection.connections = {}
            }
            print("b")
            TCPConnection.count += 1
            pull_queue = []
            TCPConnection.connections[TCPConnection.count] = {
                pull_queue: pull_queue,
                receive: receive
            }
            print("c")
            ifr = document.createElement("iframe")
            var ifrSrc = new CURL(url.render())
            if (ifrSrc.path.slice(ifrSrc.path.length-1) != "/")
                ifrSrc.path += "/"
            print("c")
            ifrSrc.path += "static/bridge.html"
            ifrSrc.hash = TCPConnection.count
            ifr.src = ifrSrc.render()
            ifr.style.width=800
            ifr.style.height=300
            print(ifr.src)
            print("d")
//            hideIframe(ifr)
            document.body.appendChild(ifr)
            print("e")
            // TODO: set timeout on disconnect
        }
        else {
            throw new Error("Fully Cross-domain TCPConnection is not supported")
        }
    }
    self.disconnect = function() {
        if (self.readyState != 1 && self.readyState != 0)
            throw new Error("Invalid readyState to disconnect")
        push(["disconnect", []])
    }
    self.send = function(data) {
        if (self.readyState != 1) {
            throw new Error("Invalid readyState to send")
        }
        // TODO: in firefox, we can directly access the iframe internals when we are doing
        //       cross subdomain, so we should remove this.
        push(["send", [data]])
    }
    
    var push = function(data) {
        if (communicator != null) {
            communicator.onpull(data)
        }
        else {
            pull_queue.push(data)
        }
    }

    var receive = function(data) {
        print("receive: " + data)
//        console.log("recieved: " + data)
        switch(data[0]) {
            case "INIT":
                push(["connect", [url.render(), session]])
                break;
            case "onopen":
                self.readyState = 1
                self.onopen(data[1])
                break;
            case "onread":
                self.onread(data[1])
                break;
            case "onclose":
                self.readyState = 2
                self.onclose(data[1])
                break;
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

TCPConnection.Communicator = function(direct, receiveFunction) {
    print('a');
    var self = this;
    var direct = Boolean(direct)
    if (direct && typeof(receiveFunction) == "undefined")
        throw new Error("must provide direct connection")
    var tcpUrl = null;
    var source = null;
    var url = null;
    var session = null;
    var id = location.hash.slice(1)
    var lastEventId = null;
    self.readyState = -1
    self.onopen = function(evt) {
        push(["onopen", evt])
    }
    self.onread = function(evt) {
        push(["onread", evt])
    }
    self.onclose = function(evt) {
        push(["onclose", evt])
    }
    print('b');


    // widen domain until it works
    if (!direct) {
        var new_domain = null;
        var parts = document.domain.split('.')
        var orig_domain = document.domain
        for (var i = 0; i < parts.length; ++i) {
            document.domain = parts.slice(i).join(".")
            try {
    //            console.log("trying: " + document.domain)
                parent.TCPConnection
                new_domain = document.domain
                break;
            }
            catch(e) {
                
            }
        }
        if (new_domain == null)
            throw new Error("Invalid document.domain for cross-frame communication")
    }
    print('c');
    
    var push = function(data) {
    print('push (direct=' + direct + '):' + data);
        if (direct)
            receiveFunction(data)
        else
            parent.TCPConnection.connections[id].receive(data)
            
    }

    self.onpull = function(data) {
        print("receive: " + data)
        var fname = data[0]
        var args = data[1]
//        console.log("apply: " + self + ", " + args)
        self[fname].apply(self, args)
    }

    var pull = function(data) {
        var queue = parent.TCPConnection.connections[id].pull_queue 
        while (queue.length > 0) {
//            console.log(parent.TCPConnection[token].pull_queue)
            var data = queue.shift()
            self.onpull(data)
        }
    }
    
    self.connect = function(_url, _session) {
        url = _url;
        session = _session;
        if (self.readyState != -1)
            throw new Error("connect may only be called once");
        self.readyState = 0
        if (session == null || typeof(session) == "undefined")
            getSession()
        else
            attachSSE()
    }

    var getSession = function() {
        var xhr = createXHR();
        xhr.open('POST', url, true)
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
        print('attachSSE');
//        console.log("url: " + url)
//        console.log("domain: " + document.domain)
        var path = url.split('?', 1)[0]
        var qs = url.slice(path.length+1)
        if (path[path.length-1] != "/")
            path += '/'
        tcpUrl = path + session
        if (qs.length > 0)
            tcpUrl += "?" + qs

        source = document.createElement("event-source")
        print("source: " + source.addEventSource)
        source.addEventListener("message", receivePayload, false)
        source.addEventListener("TCPOpen", receiveTCPOpen, false)
        source.addEventListener("TCPClose", receiveTCPClose, false)
        source.addEventListener("TCPPing", receiveTCPPing, false)
        source.addEventSource(tcpUrl)
        document.body.appendChild(source)
    }
    
    self.disconnect = function() {
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
    self.send = function(data) {
        var xhr = createXHR()
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
        var xhr = createXHR()
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
    };

    if (!direct) {
        setInterval(pull, 50)    
        push(["INIT", []])
    }

}
