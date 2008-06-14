ENDERS = ['>','</iq>']
REPLIES = ["<iq type='get'><query xmlns='jabber:iq:auth'><username>mar</username></query></iq>","<iq type='set'><query xmlns='jabber:iq:auth'><username>mar</username><password>pass</password><resource>laptop</resource></query></iq>"]
INTRO = "<stream:stream to='localhost' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams'>"

XMPPClient = function() {
    var self = this
    var conn = null
    self.buffer = ""
    self.status = 0

    self.connect = function(host, port) {
        conn = new self.transport(host, port)
        conn.onread = read
        conn.onopen = open
        conn.onclose = close
    }
    var read = function(evt) {
        var s = bytesToUTF8(evt)
        self.buffer += s
        if (s.indexOf(ENDERS[self.status]) != -1) {
            self.status += 1
            console.log("S: "+self.buffer)
            self.buffer = ""
            send(REPLIES[self.status])
        }
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
