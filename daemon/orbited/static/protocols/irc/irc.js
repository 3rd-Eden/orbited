IRCClient = function() {
    var self = this;
    var conn = null;
    
    self.nickname = ""
    
    self.onident = function() {
    }
    self.onconnect = function() {

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
    self.privmsg = function(dest, message) {
        print("<b>" + self.nickname + "</b>" + ":" + message)
        send('PRIVMSG ' + dest + ' :' + message + '\r\n')    
    }
    var read = function(evt) {
        var msg = bytesToUTF8(evt)
        
        var parts = msg.split(" ")
        
        if (parts[1] == "PING") {
            //console.log(msg)
            conn.send("PONG " + parts[1])
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
