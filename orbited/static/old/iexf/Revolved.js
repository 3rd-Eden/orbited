Revolved = function() {
    var self = this
    var num_sent = 0;
    var conn = null;
    self.readyState = 0
    self.onopen = null;
    self.onpublish = null;
    self.onreceive = null;
    self.onclose = null;
    self.onsuccess = null;
    self.onerror = null;
    
    self.connect = function(user_key, credentials) {
        // TODO: only allow valid user_Key objects
        var onopen = function() {
            self.readyState = 1
            send_frame("AUTH", [user_key, credentials])
        }

        conn = new TCPConnection()
        conn.connect("/revolved")
        conn.onopen = onopen
        conn.onread = onread
        conn.onclose = onclose
    }
    
    
    var onread = function(data) {
        var frame = eval(data)
        var type = frame[0]
        var args = frame[1]
        switch(type) {
            case "PUBLISH":
                if (self.onpublish == null)
                    break
                var channel = args[0]
                var sender = args[1]
                var payload = args[2]
                self.onpublish(channel, sender, payload)
                break
            case "SEND":
                if (self.onreceive == null)
                    break
                var sender = args[0]
                var payload = args[1]
                self.onreceive(sender, payload)
                break
            case "OK":
                var msg_id = args[0]
                if (msg_id == 1) {
                    if (self.onopen != null)
                        self.onopen()
                    break   
                }
                
                if (self.onsuccess != null)
                    self.onsuccess(msg_id)
                break
    
            case "ERR":
                if (self.onerror == null)
                    break
                var msg_id = args[0]
                var info = args[1]
                self.onerror(msg_id, info)
                break
            
            default:
                throw "Invalid Revolved Frame: " + frame
        }
    }
    
    var onclose = function() {
        if (self.onclose != null)
            self.onclose()            
    }
    
    self.publish = function(channel, data) {
        send_frame("PUBLISH", [channel, data])
    }
    
    self.subscribe = function(channel) {
        send_frame("SUBSCRIBE", [channel])
    }
    self.unsubscribe = function(channel) {
        send_frame("UNSUBSCRIBE", [channel])
    }
    self.send = function(id, data) {
        return send_frame("SEND", [id, data])
    }
    
    self.disconnect = function() {
        self.readyState = 2
        conn.disconnect()
    }
    var send_frame = function(type, payload) {
        num_sent+=1;
        send([num_sent, type, payload])
        return num_sent;
    }
    var send = function(s) {
        conn.send(JSON.stringify(s))
    }
}

