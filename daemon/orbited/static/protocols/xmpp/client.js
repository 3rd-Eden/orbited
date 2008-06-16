CONNECT = ["<stream:stream to='","' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams'>"];
REGISTER = ["<iq type='set'><query xmlns='jabber:iq:register'><username>","</username><password>","</password></query></iq>"];
LOGIN = ["<iq type='set'><query xmlns='jabber:iq:auth'><username>","</username><password>","</password><resource>Orbited</resource></query></iq>"];
ROSTER = ["<iq from='","' type='get'><query xmlns='jabber:iq:roster'/></iq><presence/>"];
MSG = ["<message from='","' to='","' xml:lang='en' type='chat'><body>","</body></message>"];
PRESENCE = ["<presence from='","' to='","' type='","'/>"];

XMPPClient = function() {
    var self = this;
    var host = null;
    var port = null;
    var conn = null;
    var user = null;
    var domain = null;
    var bare_jid = null;
    var full_jid = null;
    var parser = new XMLStreamParser();
    self.connect = function(h, p) {
        host = h;
        port = p;
        reconnect();
    }
    self.msg = function(to, content) {
        self.send(construct(MSG, [user, to, content]));
    }
    self.remove = function(buddy) {
        self.send(construct(PRESENCE, [bare_jid, buddy.slice(0, buddy.indexOf('/')), "unsubscribe"]));
        userList.onUserUnavailable(buddy);
    }
    self.add = function(buddy) {
        self.send(construct(PRESENCE, [bare_jid, buddy, "subscribe"]));
        alert("Buddy request sent.");
    }
    self.send = function(s) {
        /////////
        // send raw xml to jabber server with this function
        /////////
        conn.send(UTF8ToBytes(s));
//        console.log("sent: "+s);
    }
    self.quit = function() {
        self.send(PRESENCE[0] + full_jid + PRESENCE[2] + "unavailable" + PRESENCE[3]);
    }
    var construct = function(list1, list2) {
        var return_str = "";
        for (var i = 0; i < list2.length; i++) {
            return_str += list1[i] + list2[i];
        }
        return return_str + list1[i];
    }
    var reconnect = function() {
        conn = new self.transport(host, port);
        conn.onread = setDomain;
        conn.onopen = open;
        conn.onclose = close;
        parser.onread = nodeReceived;
//        console.log("connection opened");
    }
    var register = function(nick, pass) {
        user = nick;
        bare_jid = nick + "@" + domain;
        full_jid = bare_jid + "/Orbited";
        self.send(construct(REGISTER, [user, pass]));
    }
    var login = function(nick, pass) {
        user = nick;
        bare_jid = nick + "@" + domain;
        full_jid = bare_jid + "/Orbited";
        self.send(construct(LOGIN, [user, pass]));
    }
    var nodeReceived = function(node) {
//        console.log("received node: "+node.nodeName);
        var a = node.attributes;
        for (var i = 0; i < a.length; i++) {
//            console.log("   " + a[i].localName + ": " + a[i].value);
        }
        if (node.nodeName == "message") {
            var from = node.getAttribute("from");
            var c = node.childNodes;
            for (var i = 0; i < c.length; i++) {
                if (c[i].nodeName == "body") {
                    onMessage(from, from, c[i].textContent);
                }
            }
        }
        else if (node.nodeName == "presence") {
            var ntype = node.getAttribute("type");
            var from = node.getAttribute("from");
            if (! ntype) {
                userList.onUserAvailable(from, from);
            }
            else if (ntype == "unavailable") {
                userList.onUserUnavailable(from);
            }
            else if (ntype == "subscribe") {
                self.send(construct(PRESENCE, [node.getAttribute("to"), from, "subscribed"]));
            }
            else if (ntype == "subscribed") {
                alert(from + " added to your buddy list!");
            }
            else if (ntype == "unsubscribed") {
                userList.onUserUnavailable(from);
            }
        }
    }
    var prompt_login = function() {
        var u = prompt("User name","frank");
        if (u) {
            var p = prompt("Password","pass");
            if (p) {
                login(u,p);
            }
        }
    }
    var prompt_register = function() {
        var u = prompt("New user name","ariel");
        if (u) {
            var p = prompt("New password","pass");
            if (p) {
                register(u,p);
            }
        }
    }
    var read = function(evt) {
        var s = bytesToUTF8(evt);
//        console.log('received: '+s);
        parser.receive(s);
    }
    var setDomain = function(evt) {
        var s = bytesToUTF8(evt);
//        console.log('setDomain received: '+s);
        if (s.indexOf("<?xml version='1.0'?>") == 0) {
            s = s.slice(s.indexOf("'>")+2);
        }
        if (s.indexOf("host-unknown") != -1) {
            alert("Unknown domain");
        }
        else {
            conn.onread = setUser;
            prompt_login();
        }
    }
    var regUser = function(evt) {
        var s = bytesToUTF8(evt);
//        console.log('regUser received: '+s);
        if (s.indexOf("conflict") != -1) {
            if (confirm("That user name is taken. Try again?")) {
                prompt_register();
            }
        }
        else {
            conn.onread = read;
            alert("Welcome, " + user + "!");
        }
    }
    var setUser = function(evt) {
        var s = bytesToUTF8(evt);
//        console.log('setUser received: '+s);
        if (s.indexOf("not-authorized") != -1) {
            if (confirm("Login failed. Register a new user account?")) {
                conn.onread = regUser;
                prompt_register();
            }
            else {
                prompt_login();
            }
        }
        else {
            conn.onread = read;
            self.send(construct(ROSTER, [bare_jid]));
        }
    }
    var open = function(evt) {
        domain = prompt("Domain","localhost");
        if (domain) {
            self.send(construct(CONNECT, [domain]));
        }
    }
    var close = function(evt) {
//        console.log("connection closed");
        reconnect();
    }
}
XMPPClient.prototype.transport = BinaryTCPConnection;
