/* CSP
 *
 */

if (typeof(CSPTransports) == "undefined")
    CSPTransports = { }

CSP = function() {
    var self = this

    var num_dispatched  = 0
    var num_sent        = 0
    var sent_frames     = {}
    var received_frames = {}
    
    var RESEND_TIMEOUT = 2000
    var total_roundtrip_ms = 0
    var num_ack_back    = 0

    self.connect = function(id, connect_cb, args) {
        self.id = id
        self.conn = new CometWire()
        self.connect_cb = [connect_cb, args]
        self.conn.connect("/_/csp/up", connected_cb)
    }
    
    var closed_cb = function() {
    }

    var connected_cb = function() {
        self.conn.set_receive_cb(received_cb)
        self.conn.set_close_cb(closed_cb)
        identify()
    }

    var received_cb = function(data) {
        // TODO: real JSON
        try {
            var frame = eval(data)
            
            if (frame[0] == "ACK") {
                var tag = frame[1]
                clearInterval(sent_frames[tag].timeout)
                
                var now = new Date().getTime()
                num_ack_back++
                total_roundtrip_ms += now-sent_frames[tag].time_sent
                ROUNDTRIP_TIME = Math.round(total_roundtrip_ms/num_ack_back)
                shell.print(ROUNDTRIP_TIME + " roundtrip")
                delete sent_frames[tag]
            }
            else {
                var id = frame[0]
                if (typeof(received_frames[id]) == "undefined")
                    received_frames[id] = frame
            }
            process_queue()
        }
        catch(e) {
//            console.log(e)
        }
    }

    self.disconnect = function() {
        delete self.conn
        /* TODO:
         *  zero the rest of the state
         *  call close callback
         */
    }
    
    self.send = function(data) {
        num_sent++
        if(arguments[1] == "ID")
            var frame = [num_sent, 'ID', [self.id]]
        else
            var frame = [num_sent, 'PAYLOAD', data]
        
        frame.timeout = setInterval(function(){send(frame)}, RESEND_TIMEOUT)
        frame.time_sent = new Date().getTime()
        sent_frames[num_sent] = frame

        send(frame)
    }
    
    var send = function(data) {
        self.conn.send(escape(JSON.stringify(data)))
    }

    var identify = function() {
        self.send("", "ID")
    }

    var send_ack = function(tag) {
        var frame = ["ACK", tag]
        send(frame)
    }

    var process_queue = function() {
        while(received_frames[num_dispatched+1]) {
            num_dispatched++
            var frame = received_frames[num_dispatched]
            send_ack(num_dispatched)
            dispatch(frame)
            delete received_frames[num_dispatched]
        }
    }

    var dispatch = function(frame) {
        var tag = frame[0]
        var type = frame[1]
        var data = frame[2]
          
        /*
         *   [x] payload
         *   [x] ping
         *   [moved] ack
         *   [x] welcome
         *   [o] unwelcome
         *   [x] disconnect
         */
        switch (type) {
            case "PAYLOAD":
                var cb = self.receive_cb[0]
                var args = self.receive_cb[1]
                cb(data, args)
                break
            case "PING":
                break
            case "WELCOME":
                var conn_cb = self.connect_cb[0]
                var args = self.connect_cb[1]
                delete self.connect_cb
                conn_cb(args)
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
    c.connect("max", cspccb, c)
    return c
}
cspccb = function(conn) {    
    conn.receive_cb = [csprcb, conn]
    conn.close_cb = [cspclcb, conn]
}
csprcb = function(data, conn) {
    shell.print("CSP: received: " +  data +  "on" + conn)
}
cspclcb = function(conn) {
}
/* End test code */