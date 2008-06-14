CONNECT = "<stream:stream to='localhost' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams'>"
UNAME = "<iq type='set'><query xmlns='jabber:iq:auth'><username>"
PASS = "</username><password>"
LOGIN = "</password><resource>someresource</resource></query></iq>"
FROM = "<message from='"
TO = "' to='"
BODY = "' xml:lang='en'><body>"
END = "</body></message>"
XMPPClient = function() {
    var self = this
    var conn = null
    self.user = null
    self.parser = new XMLStreamParser()
    self.login = function(nick, pass) {
        self.user = nick
        send(UNAME + nick + PASS + pass + LOGIN)
    }
    self.connect = function(host, port) {
        conn = new self.transport(host, port)
        conn.onread = read
        conn.onopen = open
        conn.onclose = close
        self.parser.onread = nodeReceived
    }
    self.msg = function(to, content) {
        send(FROM + self.user + TO + to + BODY + content + END)
    }
    var nodeReceived = function(node) {
        console.log("S: "+node)
        if (node.nodeName == "message") {
            console.log("NEW MESSAGE: "+ node.getAttribute("type"))
            console.log(node.getAttribute("to") + ": " + node.firstChild.textContent)
        }
    }
    var read = function(evt) {
        var s = bytesToUTF8(evt)
        console.log('received: '+s)
        /////
        // FOR NOW
        if (s.indexOf("<?xml version='1.0'?>") == -1) {
        // OBVIOUSLY, CHANGE
        /////
            self.parser.receive(s)
        }
    }
    var open = function(evt) {
        send(CONNECT)
    }
    var close = function(evt) {
        console.log("connection closed")
    }
    var send = function(s) {
        conn.send(UTF8ToBytes(s))
        console.log("C: "+s)
    }
}
XMPPClient.prototype.transport = BinaryTCPConnection
