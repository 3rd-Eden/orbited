ENDERS = ['>','</iq>']
REPLIES = ["<iq type='get'><query xmlns='jabber:iq:auth'><username>mar</username></query></iq>","<iq type='set'><query xmlns='jabber:iq:auth'><username>mar</username><password>pass</password><resource>laptop</resource></query></iq>"]
INTRO = "<stream:stream to='localhost' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams'>"
XMPPClient = function() {
    var self = this
    var conn = null
    self.parser = new XMLStreamParser()

    self.connect = function(host, port) {
        conn = new self.transport(host, port)
        conn.onread = read
        conn.onopen = open
        conn.onclose = close
        self.parser.onread = nodeReceived
    }
    var nodeReceived = function(node) {
        console.log("S: "+node)
    }
    var read = function(evt) {
        var s = bytesToUTF8(evt)
        self.parser.receive(s)
    }
    var open = function(evt) {
        send(INTRO)
        console.log("C: "+INTRO)
    }
    var close = function(evt) {
        console.log("connection closed")
    }
    var send = function(s) {
        conn.send(UTF8ToBytes(s))
    }
}
XMPPClient.prototype.transport = BinaryTCPConnection
xmpp = new XMPPClient()
