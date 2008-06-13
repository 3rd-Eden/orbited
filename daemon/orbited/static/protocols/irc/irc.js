IRCClient = function() {
    var self = this;
    var conn = null;
    
    self.nickname = ""
    
    self.onident = function() {
    }
    self.onconnect = function() {

    }
    self.onnames = function(names) {
        print(names)
    }

    self.connect = function(host, port) {
        conn = new self.transport(host, port)
        conn.onread = read
        conn.onopen = open
        conn.onclose = close
    }
    self.nick = function(nickname) {
        self.nickname = nickname
        send("NICK " + nickname + "\r\n")
    }
    self.ident = function(ident, modes, name) {
        send("USER " + ident + " " + modes + " :" + name + "\r\n")
    }
    self.join = function(channel) {
        send('JOIN ' + channel + '\r\n')
    }
    self.names = function(channel) {
        send('WHO ' + channel)
        console.log("who sent")
    }
    self.privmsg = function(dest, message) {
        print("<b>" + self.nickname + "</b>" + ":" + message)
        send('PRIVMSG ' + dest + ' :' + message + '\r\n')    
    }
    
    var read = function(evt) {
        var s = bytesToUTF8(evt)
        var msgs = s.split("\r\n")
        for (var i=0; i<msgs.length; i++)
            dispatch(msgs[i])
    }
    
    var dispatch = function(msg) {
        var parts = msg.split(" ")
        
        console.log(msg)
        
        if (parts[3] == "@") {
            var namelist = msg.split(":").slice(-1)[0].split(" ")
            console.log(namelist)
        
            self.onnames(namelist)
        }
        
        if (parts[0] == "PING") {
            conn.send(msg.replace("PING","PONG"))
        }
        
        if (parts[1] == "PRIVMSG" && parts[2] != self.nickname) {
            var identity = parts[0].slice(1)
            var ident_name = identity.split("!",1)[0]
            print("<b>" + ident_name +"</b>" + parts.slice(3).join(" "))
        }
    }
    var open = function(evt) {
        self.onident();
    }
    var close = function(evt) {

    }

    var send = function(s) {
        conn.send(UTF8ToBytes(s))
    }
}

IRCClient.prototype.transport = BinaryTCPConnection
