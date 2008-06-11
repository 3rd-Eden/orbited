IRCClient = function() {
    var self = this;
    var conn = null;
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
        conn.send("NICK " + nickname + "\r\n")
    }
    self.ident = function(ident, modes, name) {
        conn.send("USER " + ident + " " + modes + " :" + name + "\r\n")
    }
    self.join = function(channel) {
        conn.send('JOIN ' + channel + '\r\n')
    }
    self.privmsg = function(dest, message) {
        conn.send('PRIVMSG ' + dest + ' :' + message + '\r\n')
    }
    var read = function(evt) {
        print(evt.data)
    }
    var open = function(evt) {
        self.onident();
    }
    var close = function(evt) {

    }
}

IRCClient.prototype.transport = JSONTCPConnection