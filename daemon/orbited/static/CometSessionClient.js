function() {

if (typeof(Orbited) == "undefined") {
    Orbited = {}
}

HANDSHAKE_TIMEOUT = 30000


if (typeof(Orbited.Errors) == "undefined") {
    Orbited.Errors = {}
}
// Orbited CometSession Errors

Orbited.Errors.ConnectTimeout = 101
Orbited.Errors.InvalidHandshake = 102


// The readyState values
var states = {
    INITIALIZED: 1,
    OPENING: 2,
    OPEN: 3,
    CLOSING: 4,
    CLOSED: 5
}

Orbited.CometSession = function() {
    var self = this;
    self.readyState = states.INITIALIZED
    self.onopen = function() {}
    self.onread = function() {}
    self.onclose = function() {}
    
    var sessionKey = null;
    var sendQueue = []
    var packetCount = 0;
    var xhr = null;
    var handshakeTimer = null;
    var cometTransport = null;

    /*
     * self.open can only be used when readyState is INITIALIZED. Immediately
     * following a call to self.open, the readyState will be OPENING until a
     * connection with the server has been negotiated. self.open takes a url
     * as a single argument which desiginates the remote url with which to
     * establish the connection.
     */
    self.open = function() {
        xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    sessionKey = xhr.responseText;
                    cometTransport = Orbited.CometTransport.choose();
                    
                    cometTransport.connect()
                    cometTransport.onread = 
                }
                else {
                    xhr = null;
                    self.readyState = states.CLOSED;
                    self.onclose(Orbited.Errors.InvalidHandshake)
                }
            }
        }   
    }

    /* 
     * self.send is only callable when readyState is OPEN. It will queue the data
     * up for delivery as soon as the upstream xhr is ready.
     */
    self.send = function(data) {
        
    }

    /* 
     * self.close sends a close frame to the server, at the end of the queue.
     * It also sets the readyState to CLOSING so that no further data may be
     * sent. onclose is not called immediately -- it waits for the server to
     * send a close event.
     */
    self.close = function() {
        
    }

    /* self.reset is a way to close immediately. The send queue will be discarded
     * and a close frame will be sent to the server. onclose is called immediately
     * without waiting for a reply from the server.
     */
    self.reset = function() {

    }    

    var 

}

})();