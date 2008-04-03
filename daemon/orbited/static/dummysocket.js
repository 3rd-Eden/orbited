Orbited.require("json.js")

TCPConnection = function(location, onopen, onread, onclose) {
    var self = this
    self.network = true
    self.readyState = 0
    var _channels = {}
    var _onconnect = function() {
        self.readyState = 1
        onopen()
    }
    var _onread = function(message, channel) {
        onread.handleEvent("read", [message, channel])
    }
    var _maybe_read = function() {
        if (Math.random()*10 > 7) {
            _onread("someone said something", "nochannel")
        }
    }
    self.send = function(s) {
        var action = s[0]
        var channel = s[1][0]
        switch (action) {
            case "PUBLISH":
                if (channel in _channels) {
                    var message = s[1][1]
                    _onread(message, channel)
                }
                break
            case "SUBSCRIBE":
                _channels[channel] = true
                break
            case "UNSUBSCRIBE":
                if (channel in _channels) {
                    delete _channels[channel]
                }
                break
            case "SEND":
                break
            default:
                throw "invalid DummyConn fake revolved action"
        }
    }
    self.disconnect = function() {
        self.readyState = 2
        onclose()
    }
    setInterval(_maybe_read,1000)
}