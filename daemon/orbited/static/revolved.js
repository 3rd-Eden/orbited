Orbited.require("socket.js")

Revolved = function() {
    var self = this
    
    self.readyState = 0
    
    self.connect = function() {
        self.conn = new TCPConnection(null, onopen, onread, onclose)
    }
    
    
    var onopen = function() {
        self.readyState = 1
    }
    
    var onread = function(s) {
        shell.print("REVOLVED got: " + s)
    }
    
    var onclose = function() {
        
    }
    

    self.auth = function() {
        
        send(["AUTH", []])
    }

    
    self.publish = function(channel, s) {
        send(["PUBLISH", [channel, s]])
    }
    
    self.subscribe = function(channel) {
        send(["SUBSCRIBE", [channel]])
    }
    
    self.send = function(id, s) {
        send(["SEND", [id, s]])
    }
    
    self.disconnect = function() {
        self.readyState = 2
        conn.disconect()
    }
    
    var send = function(s) {
        conn.send(JSON.stringify(s))
    }
    
}

