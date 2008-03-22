/* CSP
 *
 */

//stub for testing
CometWire = function() {
    var self = this
    if(typeof(arguments[0]) == "function")
        self.cb = arguments[0]
        
    self.send = function(s) {
        console.log(s)
    }
}

CSP = function() {
    var self = this
    
    //set callback if passed one as an argument
    if(typeof(arguments[0]) == "function")
        self.cb = arguments[0]

    var num_dispatched  = 0
    var num_sent        = 0
    var up_queue        = []
    var down_queue      = []


    self.connect = function() {
        self.conn = new CometWire(recv_cb)
    }
    
    self.disconnect = function() {
        delete self.conn
        /* TODO:
         *  zero the rest of the state
         */
    }
    
    self.send = function(data) {
        num_sent++
        var frame = [up_count, 'PAYLOAD', data]
        up_queue.push(frame)
        self.conn.send(frame)
    }

    var recv_cb = function(frame) {
        down_queue.push(frame)
        // TODO: check for consistency, send back acks?
        
        dispatch()
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
                self.cb(data)
                break
            case "PING":
                throw "unimplemented"
                break
            case "PONG":
                throw "unimplemented"
                break
            case "ACK:"
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
