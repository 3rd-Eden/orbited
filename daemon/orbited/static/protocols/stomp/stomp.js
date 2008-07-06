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
        var data = bytesToUTF8(msg)
        self.buffer += data
        parse_buffer()
    }

    var parse_buffer = function () {
        var msgs = self.buffer.split('\0\n')
        self.buffer = msgs[msgs.length-1]
        for (var i=0; i<msgs.length-1; i++)
            dispatch(msgs[i])
    }
    
    /* parse_message()
     * STOMP frames consist of a type, 0 or more headers, and possibly a body
     */
    var parse_frame = function(s) {
        var headers_end = s.search("\n\n")
        var headers = s.slice(0, headers_end)
        var type = headers.slice(0, headers.search("\n"))
        headers = headers.slice(headers.search("\n") +1)
        var body = s.slice(headers_end + 2)
        headers = parse_headers(headers)
        var frame = {}
        frame['type'] = type
        frame['headers']= headers
        frame['body'] = body
        
        return frame
    }
    
    var parse_headers = function(s) {
        var lines = s.split("\n")
        var headers = {}
        for (var i=0; i<lines.length; i++) {
            var sep = lines[i].search(":")
            var key = lines[i].slice(0,sep)
            var value = lines[i].slice(sep+1)
            
            headers[key] = value
        }
        return headers
    }
    
    var dispatch = function(msg) {
        
        msg = parse_frame(msg)
        
        switch (msg.type) {
            case ('CONNECTED'):
                self.onopen()
                break
            case ('MESSAGE'):
                self.onmessage(msg)
                break
            case ('RECEIPT'):
                // TODO: receipts and acking modes
                break
            case ('ERROR'):
                self.onerror(msg)
                break
            default:
                throw("Unknown STOMP frame type " + msg.type)
        }
    
    }

    /* Messaging methods
     *
     */
     var send_frame = function(type, headers, body) {
        var frame = ""
        frame += type + "\n"
        for (var key in headers)
            frame += key + ": " + headers[key] + "\n"
        frame += "\n"                   // end of headers
        if (body)
            frame += body
        frame += "\0"                   // frame delineator
        var data = UTF8ToBytes(frame)
        conn.send(UTF8ToBytes(frame))
     }
    self.send_frame = send_frame

    /* Client Actions
     *
     */
    self.connect = function(domain, port, user, password) {
        self.buffer = ""                     // reset buffer state
        self.user = user
        var onsockopen = function() {
            send_frame("CONNECT", {'login': user, 'passcode':password})
        }
        conn = new BinaryTCPSocket(domain, port)
        conn.onopen = onsockopen
        conn.onread = self.messageReceived
    }

    self.disconnect = function() {
        send_frame("DISCONNECT", {})
    }

    self.send = function(msg, destination, custom_headers) {
        var headers = {"destination": destination}
        if (custom_headers)
            for (var key in custom_headers)
                headers[key] = custom_headers[key]
            
        send_frame("SEND", headers, msg)
    }

    self.subscribe = function(destination) {
        send_frame("SUBSCRIBE", {"destination": destination})
    }
    
    self.unsubscribe = function(destination) {
        send_frame("UNSUBSCRIBE", {"destination": destination})
    }

    /* Transactions and acking
     *
     */
    self.begin = function(id) {
        send_frame("BEGIN", {"transaction": id})
    }

    self.commit = function(id) {
        send_frame("COMMIT", {"transaction": id})
    }

    // Rolls back the given transaction
    self.abort = function(id) {
        send_frame("ABORT", {"transaction": id})
    }

    self.ack = function(message_id, transaction_id) {
        //throw("ack: not implemented")
    }
    

}

