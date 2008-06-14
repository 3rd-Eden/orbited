CONNECT = "<stream:stream to='localhost' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams'>"
UNAME = "<iq type='set'><query xmlns='jabber:iq:auth'><username>"
PASS = "</username><password>"
LOGIN = "</password><resource>someresource</resource></query></iq><iq from='juliet@example.com/balcony' type='get' id='get_roster'><query xmlns='jabber:iq:roster'/></iq>"
FROM = "<message from='"
TO = "' to='"
BODY = "' xml:lang='en' type='chat'><body>"
END = "</body></message>"
XMPPClient = function() {
    var self = this;
    var conn = null;
    self.user = null;
    self.parser = new XMLStreamParser();
    self.connect = function(host, port) {
        conn = new self.transport(host, port);
        conn.onread = read;
        conn.onopen = open;
        conn.onclose = close;
        self.parser.onread = nodeReceived;
    }
    self.login = function(nick, pass) {
        self.user = nick;
        self.send(UNAME + nick + PASS + pass + LOGIN);
    }
    self.msg = function(to, content) {
        self.send(FROM + self.user + TO + to + BODY + content + END);
    }
    self.send = function(s) {
        conn.send(UTF8ToBytes(s));
        console.log("C: "+s);
    }
    var nodeReceived = function(node) {
        console.log("S: "+node.nodeName+" - "+node.getAttribute("type"));
        if (node.nodeName == "message") {
            console.log("NEW MESSAGE");
            var from = node.getAttribute("from");
            var body = node.firstChild.textContent;
            console.log(from + ": " + body);
            onMessage(from, from, body);
        }
        else if (node.getAttribute("id") == "get_roster") {
            var r = node.firstChild.childNodes;
            for (var x = 0; x < r.length; x++) {
                console.log(r[x]);
                var uname = r[x].getAttribute("jid");
                userList.onUserAvailable(uname, uname);
//                if (r[x].getAttribute("subscription") != "from") {
 //                   console.log("add to buddy list")
  //              }
            }
        }
    }
    var read = function(evt) {
        var s = bytesToUTF8(evt);
        console.log('received: '+s);
        /////
        // FOR NOW
        if (s.indexOf("<?xml version='1.0'?>") == -1) {
        // OBVIOUSLY, CHANGE
        /////
            self.parser.receive(s);
        }
    }
    var open = function(evt) {
        self.send(CONNECT);
    }
    var close = function(evt) {
        console.log("connection closed");
    }
}
XMPPClient.prototype.transport = BinaryTCPConnection;
