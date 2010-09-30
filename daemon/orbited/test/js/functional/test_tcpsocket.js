EchoTest = function (socket, text, binary) {
    var success = false;
    var buffer = "";
    
    socket.onopen = function() {
        socket.send(text);
    };
    
    socket.onread = function(data) {
        buffer += data;
        testlog.info("buffer contains: ", buffer, 'text is', text);
        if (buffer == text) {
            success = true;
            socket.close();
        }
    };
    
    socket.onclose = function() {
        if (!success) {
            throw new Error("socket closed before receiving message");	    
	}
    };
    
    socket.onerror = function(error) {
	throw error;
    };
    
    socket.open("localhost", 8001, binary);
    
};

TCPSocketTest = TestCase('TCPSocketTest');

TCPSocketTest.prototype.setUp = function () {
    this.socket = new Orbited.TCPSocket();    
};

TCPSocketTest.prototype.tearDown = function () {
    try {
        var readyState = this.socket.readyState;
        if (readyState != this.socket.READY_STATE_CLOSED && readyState != this.socket.READY_STATE_INITIALIZED) {
            jstestdriver.console.log("going to reset a non closed socket with readyState=", this.socket.readyState);	    
	}
        this.socket.reset();
    } catch (e) {
        jstestdriver.console.log("unable to reset socket (further tests might be fubar because of this): ", e);
    }
};

TCPSocketTest.