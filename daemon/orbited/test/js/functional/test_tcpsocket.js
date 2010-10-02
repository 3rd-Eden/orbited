
var EchoTest = function (queue, socket, text, binary) {
    var success = false;
    var buffer = "";
    
    socket.onopen = function() {
        socket.send(text);
    };
    
    queue.defer("Wait for onread to be fired", function (pool) {
	
	socket.onread = pool.add(function(data) {
            buffer += data;
	    if (buffer == text) {
                success = true;
                socket.close();
            }
        });	
    });
    
    queue.defer("The socket shouldn't be closed until the message is read", function (pool) {
        socket.onclose = pool.add(function() {
            if (!success) {
                throw new Error("socket closed before receiving message");	    
	    }
        });
    });
    
    socket.onerror = function(error) {
	throw error;
    };
    
    socket.open("localhost", 8001, binary);
    
};

var TCPSocketTest = AsyncTestCase('TCPSocketTest');

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

TCPSocketTest.prototype.testSimpleEcho = function(queue) {
    assertNotNull(queue.defer);
    EchoTest(queue, this.socket, "fleegle", false);
};

TCPSocketTest.prototype.testFailure = function(queue) {
    assertNull(queue, typeof queue);
};