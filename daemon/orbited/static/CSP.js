/* CSP
 *
 */

CSP = function() {
    var self = this

    var num_dispatched  = 0
    var num_sent        = 0
    var up_queue        = []
    var down_queue      = []


    self.connect = function(connect_cb, args) {
        self.conn = new CometWire()
        self.connect_cb = [connect_cb, args]
        self.conn.connect("/_/csp/up", connected_cb)
    }
    var closed_cb = function() {
    }

    var connected_cb = function() {
        console.log("in CSP connected", self.conn)
        self.conn.set_receive_cb(received_cb)
        self.conn.set_close_cb(closed_cb)
        console.log('cb', self.connect_cb)
        var conn_cb = self.connect_cb[0]
        var args = self.connect_cb[1]
        console.log(conn_cb, args)
        delete self.connect_cb
        return conn_cb(args)
    }

    var received_cb = function(data) {
        console.log("RECEIVE", data)
        // TODO: real JSON
        try {
            frame = eval(data)
            down_queue.push(frame)
            // TODO: check for consistency, send back acks?
            
            dispatch()
        }
        catch(e) {
            console.log(e)
        }
    }

    self.disconnect = function() {
        delete self.conn
        /* TODO:
         *  zero the rest of the state
         */
    }
    
    self.send = function(data) {
        num_sent++
        var frame = [num_sent, 'PAYLOAD', data]
        up_queue.push(frame)
        self.conn.send(escape(JSON.stringify(frame)))
    }


    var dispatch = function() {
        //make the queue consecutive
        if (!check_queue())
            return
        
        var frame = down_queue[0]
        
        var tag = frame[0]
        var type = frame[1]
        var data = frame[2]
          
        /*
         *   [x] payload
         *   [ ] ping
         *   [ ] pong
         *   [ ] ack
         *   [ ] welcome
         *   [ ] unwelcome
         *   [x] disconnect
         */
        switch (type) {
            case "PAYLOAD":
                self.receive_cb(data)
                break
            case "PING":
                throw "unimplemented"
                break
            case "PONG":
                throw "unimplemented"
                break
            case "ACK":
                throw "unimplemented"
                break
            case "WELCOME":
                throw "unimplemented"
                break
            case "UNWELCOME":
                self.disconnect()
                // TODO: do something else?
                break
            case "DISCONNECT":
                self.disconnect()
                break
            
            default:
                throw "unknown type"
        }
    }

}


/* Firefox test code */
cspstart = function() {
    c = new CSP()
    c.connect(cspccb, c)
    return c
}
cspccb = function(conn) {    
    console.log("CSP: connected", conn)
    conn.receive_cb = [csprcb, conn]
    conn.close_cb = [cspclcb, conn]
    conn.send('"hello"')
}
csprcb = function(data, conn) {
    console.log("CSP: received", data, "on", conn)
}
cspclcb = function(conn) {
    console.log("CSP: closed", conn)
}
/* End test code */