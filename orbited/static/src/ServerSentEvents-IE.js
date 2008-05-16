STATIC_SOURCE = "/_/static/"

var oldLoad = function() { }
if (window.onload) 
    oldLoad = window.onload

alerter = function(data) {
    alert('in parent: ' + data);
}

var newLoad = function() {
    base2.DOM.bind(document)
    sources = document.getElementsByTagName("event-source")
    for (var i = 0; i < sources.length; ++i) {
        source = sources[i]
        base2.DOM.bind(source)
        var SSEHandler = new IESSE(source);
    }
    var createElement = document.createElement
    document.createElement = function(name) {
//        print("createElement: " + name)
        var obj = null;
        if (typeof(createElement.call) == "undefined") // IE modification
            obj = createElement(name)
        else 
            obj = createElement.call(this, name)
        if (name == "event-source") {
//            alert('creating event-source');
            var SSEHandler = new IESSE(obj);
        }
        return obj
    }
}


window.onload = function() {
    newLoad()
    oldLoad()
}





IESSE = function(source) {
    var self = this;
    var id = ++IESSE.prototype._state.id
    var ifr = null;
    var retry = 3000;
    var src = null;
    var reconnectTimer = null;

    var receive = function(name, data, origin, id) {
        var e = document.createEvent("Events")
        e.initEvent(name, true, true)
        e.lastEventId = id 
        e.data = data
        e.origin = origin
        e.source = null
        source.dispatchEvent(e);
        
    }
    IESSE.prototype._state.connections[id] = self;
    IESSE.prototype._state.cbs[id] = receive;
    source.addEventSource = function(eventSrc) {
        // TODO: keep track of sources that we are already connected to
        //       check the spec for information on this
        if (src != null) {
            throw new Error("AlreadyConnected: wait for widespread adoption of SSE specification")
        }
        var testUrl = new URL(eventSrc)
        if (testUrl.qs.length > 0)
            testUrl.qs += '&ie=1'
        else
            testUrl.qs = 'ie=1'
        src = testUrl.render()
        connect()
    }
    source.removeEventSource = function(eventSrc) {
        if (eventSrc != src)
            throw new Error("NotConnected to src: " + eventSrc)
        if (reconnectTimer != null) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }
        if (ifr != null) {
            offset = 0;
            lineQueue = []
            id = null;
        }

        src = null;
    }
    var connect = function() {
        var url = new URL(src)
        if (false && url.isSameDomain(location.href)) {
            throw new Error("not implemented");
        }
        else if (url.isSameParentDomain(location.href)) {
            if (typeof(STATIC_SOURCE) == "undefined") {
                url.path = "/_/static/ServerSentEvents-IE-bridge.html"
            }
            else {
                url.path = STATIC_SOURCE + "ServerSentEvents-IE-bridge.html"
            }
            url.path += "#" +  id + "_" + escape(src)
            url.qs = ""
            ifr = document.createElement("iframe")
            ifr.src = url.render()
            ifr.style.width = 600
            ifr.style.height = 400
            document.body.appendChild(ifr);
        }
        else {
            throw new Error("Invalid url domain")
        }
    }
    var reconnect = function() {
        // TODO: reuse this xhr connection
//        xhr = null;
//        offset = 0
//        setTimeout(connect, retry)
    }

}

IESSE.prototype._state = {
    connections: {},
    cbs: {},
    id: 0
}
/*jslint evil: true */
/*extern JSON */

// timestamp: Sun, 06 Jan 2008 18:17:45
/*
  base2 - copyright 2007-2008, Dean Edwards
  http://code.google.com/p/base2/
  http://www.opensource.org/licenses/mit-license.php
  
  Contributors:
    Doeke Zanstra
*/

