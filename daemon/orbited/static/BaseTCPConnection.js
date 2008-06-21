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