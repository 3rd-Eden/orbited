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
                source.addEventListener("TCPClose", receiveTCPClose, false)
                source.addEventListener("TCPPing", receiveTCPPing, false)
//                connUrl.setQsParameter('transport', 'sse')
//                connUrl.hash = "0"
                url = connUrl.render()
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