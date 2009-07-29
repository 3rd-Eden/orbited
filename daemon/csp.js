var id = 0;
var csp = {
    'readyState': {
        'initial': 0,
        'opening': 1,
        'open':    2,
        'closing': 3,
        'closed':  4
    }
};

csp._cb = {};
csp._cb.add = function(cspId, transport) {
    csp._cb["i"+cspId] = {};
    csp._cb["i"+cspId].handshake = function() {
        transport.cbHandshake.apply(transport, arguments);
    }
    csp._cb["i"+cspId].send = function() {
        transport.cbSend.apply(transport, arguments);
    }
    csp._cb["i"+cspId].comet = function() {
        transport.cbComet.apply(transport, arguments);
    }
}

csp.CometSession = function() {
    var self = this;
    self.id = ++id;
    self.url = null;
    self.readyState = csp.readyState.initial;
    self.sessionKey = null;
    var transport = null;

    self.write = function() { throw new Error("invalid readyState"); }

    self.onopen = function() {
        console.log('onopen', self.sessionKey);
    }

    self.onclose = function(code) {
        console.log('onclose', code);
    }

    self.onread = function(data) {
        console.log('onread', data);
    }

    self.connect = function(url) {
        self.readyState = csp.readyState.opening;
        self.url = url;
        transport = new transports.jsonp(self.id, url);
        csp._cb.add(self.id, transport);
        transport.onHandshake = function(key) {
            self.readyState = csp.readyState.open;
            self.sessionKey = key;
            self.write = transport.send;
            transport.onPacket = self.onread;
            transport.resume(key, 0);
            self.onopen();
        }
        transport.handshake();
    }
}

var Transport = function(cspId, url) {
    this.cspId = cspId;
    this.url = url;
    this.sessionKey = null;
    this.lastEventId = null;
    this.processPackets = function(packets) {
        for (var i = 0; i < packets.length; i++) {
            var p = packets[i];
            if (p === null)
                return this.doClose();
            var ackId = p[0];
            var data = p[1];
            if (this.lastEventId != null && ackId <= this.lastEventId)
                continue;
            if (this.lastEventId != null && ackId != this.lastEventId+1)
                throw new Error("CSP Transport Protocol Error");
            this.lastEventId = ackId;
            this.onPacket(data);
        }
    }
    this.resume = function(sessionKey, lastEventId) {
        this.sessionKey = sessionKey;
        this.lastEventId = lastEventId;
        this.reconnect();
    }
    this.cbHandshake = function(data) {
//        console.log("HAND SHOOK:", data);
        this.onHandshake(data);
    }
    this.cbSend = function(data) {
//        console.log("SEND STATUS:", data);
    }
    this.cbComet = function(data) {
//        console.log("RECEIVED:", data);
        this.processPackets(data);
        this.reconnect();
    }
}

var transports = {};

transports.jsonp = function(cspId, url) {
    var self = this;
    Transport.call(self, cspId, url);

    var makeIframe = function() {
        var i = document.createElement("iframe");
        i.style.display = 'block';
        i.style.width = '0';
        i.style.height = '0';
        i.style.border = '0';
        i.style.margin = '0';
        i.style.padding = '0';
        i.style.overflow = 'hidden';
        i.style.visibility = 'hidden';
        return i;
    }
    var ifr = {};
    ifr.bar = makeIframe();
    ifr.send = makeIframe();
    ifr.comet = makeIframe();

    var killLoadingBar = function() {
        window.setTimeout(function() {
            document.body.appendChild(ifr.bar);
            document.body.removeChild(ifr.bar);
        }, 0);
    }
    var cspRequest = function(rType, url) { // add timeout?
        var i = ifr[rType].contentDocument;
        var s = i.createElement("script");
        s.src = self.url + url;
        i.getElementsByTagName('head')[0].appendChild(s);
        killLoadingBar();
    }
    self.handshake = function() {
        window.setTimeout(function() {
            cspRequest("send", "/handshake?rs=;&rp=parent.csp._cb.i" + self.cspId + ".handshake");
        }, 0);
    }
    self.send = function(data) {
        cspRequest("send", "/send?s=" + self.sessionKey + "&rs=;&rp=parent.csp._cb.i" + self.cspId + ".send&d=" + data);
    }
    self.reconnect = function() {
        window.setTimeout(function() {
            cspRequest("comet", "/comet?bs=;&bp=parent.csp._cb.i" + self.cspId + ".comet&s=" + self.sessionKey + "&a=" + self.lastEventId);
        }, 0);
    }

    document.body.appendChild(ifr.send);
    document.body.appendChild(ifr.comet);
    killLoadingBar();
}
