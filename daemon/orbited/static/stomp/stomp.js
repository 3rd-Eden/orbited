/* stomp.js
 *
 * JavaScript implementation of the STOMP (Streaming Text Oriented Protocol)
 *  for use with TCPConnection or a facsimile
 *
 * Frank Salim (frank.salim@gmail.com) (c) 2008 Orbited (orbited.org)
 */

STOMPClient = function() {
    var self = this
    var conn = null
    self.buffer = ""    
    self.user = null
    
    /* Callbacks
     */
    self.onopen = null
    self.onmessage = null
    self.onerror = null
    
    self.messageReceived = function(msg) {
        var data = bytesToUTF8(msg.data)             // TCPConnn msg has data as a property
        self.buffer += data
        parse_buffer()
    }

    var parse_buffer = function () {
        var msgs = self.buffer.split('\n\0')
        self.buffer = msgs.splice(-1)[0]

        for (i=0; i<msgs.length; i++)
            dispatch(msgs[i])
    }
    
    
    /* parse_message()
     * FIXME:
     * STOMP frames consist of a type, 0 or more headers, and possibly a body
     *
     */
    var parse_message = function(msg) {
        var parts = msg.split("\n")
        
        var frame = []
        
        return frame
    }
    
    var dispatch = function(msg) {
        //parse message
        var parts = msg.split("\n")

        var frame = []
        for (var i=0; i<parts.length; i++)
            if(parts[i])
                frame.push(parts[i])
        
        switch (frame[0]) {
            case ('CONNECTED'):
                self.onopen()
                break
            case ('MESSAGE'):
                // FIXME: handle messages with double newlines in the body
                self.onmessage(msg.split("\n\n").slice(-1)[0])
                break
            case ('RECEIPT'):
                
                break
            case ('ERROR'):
                self.onerror(msg)
                break
            default:
                throw("Unknown STOMP command " + frame[0])
        }
    
    }

    /* Messaging methods
     *
     */
     var send_frame = function(msg, headers, body) {
        var frame = ""
        frame += msg + "\n"
        for (var i=0; i< headers.length; i++)
            frame += headers[i][0] + ": " + headers[i][1] + "\n"

        if (body)
            frame += "\n" + body
        frame += "\n\0"                 // frame delineator
        conn.send(UTF8ToBytes(frame))
     }

    /* Client Actions
     *
     */
    self.connect = function(domain, port, user, password) {
        buffer = ""                     // reset buffer state
        self.user = user
        
        var onsockopen = function() {
            alert('connected')
            send_frame("CONNECT", [["login", user]])
        }
        alert('new binary tcp connection')
        conn = new BinaryTCPConnection(domain, port)
        conn.onopen = onsockopen
        conn.onread = self.messageReceived
        alert('okay...')

    }

    self.disconnect = function() {
        send_frame("DISCONNECT", [])
    }

    self.send = function(msg, destination, transaction_id) {
        var headers = [["destination", destination]]
        if (transaction_id)
            headers.push(['transaction', transaction_id])
            
        send_frame("SEND", headers, msg)
    }

    self.subscribe = function(destination) {
        send_frame("SUBSCRIBE", [["destination", destination]])
    }
    
    self.unsubscribe = function(destination) {
        send_frame("UNSUBSCRIBE", [["destination", destination]])
    }

    /* Transactions and acking
     *
     */
    self.begin = function(id) {
        send_frame("BEGIN", [["transaction", id]])
    }

    self.commit = function(id) {
        send_frame("COMMIT", [["transaction", id]])
    }

    // Rolls back the given transaction
    self.abort = function(id) {
        send_frame("ABORT", [["transaction", id]])
    }

    self.ack = function(message_id, transaction_id) {
        //throw("ack: not implemented")
    }

}

