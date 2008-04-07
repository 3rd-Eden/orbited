/* CSP
 *
 */
Orbited.require("json.js")
Orbited.require("cometwire.js")

CSP = function() {
    var self = this

    var num_dispatched  = 0
    var num_sent        = 0
    var sent_frames     = {}
    var received_frames = {}
    
    var RESEND_TIMEOUT = 2000
    var total_roundtrip_ms = 0
    var num_ack_back    = 0

    self.connect = function(id, connect_cb, domain, port, args) {
        self.id = id
        if (typeof(domain) == "undefined" || domain == null)
            domain = "internal"
        if (typeof(port) == "undefined" || port == null)
            port = 80
        self.domain = domain
        self.port = port
        self.conn = new CometWire()
        self.connect_cb = [connect_cb, args]
        self.conn.connect(connected_cb)
    }
    
    var closed_cb = function() {
        self.disconnect()
    }

    var connected_cb = function() {
        if(self.id == null)
            self.id = self.conn.id

        self.conn.set_receive_cb(received_cb)
        self.conn.set_close_cb(closed_cb)
        identify()
    }

    var received_cb = function(data) {
//        shell.print("[CSP] " + data)
        try {
            var frame = JSON.parse(data)
//            var frame = data
            if (frame[0] == "ACK") {
                var tag = frame[1]
                clearInterval(sent_frames[tag].timeout)
                
                var now = new Date().getTime()
                num_ack_back++
                total_roundtrip_ms += now-sent_frames[tag].time_sent
                RESEND_TIMEOUT = Math.round(total_roundtrip_ms/num_ack_back)
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
         for (frame in sent_frames) {
             clearInterval(frame.timeout)
         }
         delete sent_frames
         
         /* TODO:
          *  call close callback
          */
          var cb = self.close_cb[0]
          cb()
    }

    self.send = function(data) {
        var frame = [num_sent, 'PAYLOAD', data]
        send_frame('PAYLOAD', data)   
    }
    
    var send_frame = function(type, payload) {
        num_sent++
        var frame = [num_sent, type, payload]
        
        var retry = function() {
            send(frame)
            frame.attempt += 1
            if (frame.attempt > 10)
                self.disconnect()
        }
        
        frame.timeout = setInterval(retry, RESEND_TIMEOUT)
        frame.time_sent = new Date().getTime()
        frame.attempt = 1
        sent_frames[num_sent] = frame
        send(frame)
    }

    var send_ack = function(tag) {
        var frame = ["ACK", tag]
        send(frame)
    }
    
    var send = function(data) {
        self.conn.send(escape(JSON.stringify(data)))
    }

    var identify = function() {
        send_frame("ID", [self.id, self.domain, self.port])
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
                throw "unknown type of CSP message"
        }
    }

}
