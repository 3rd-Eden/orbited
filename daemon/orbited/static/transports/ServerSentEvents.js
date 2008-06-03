window.addEventListener("load", function() {
    sources = document.getElementsByTagName("event-source")
    for (var i = 0; i < sources.length; ++i) {
        source = sources[i]
        var SSEHandler = new FxSSE(source);
        // TODO: removeEventSource
    }
    var createElement = document.createElement
    document.createElement = function(name) {
        var obj = createElement.call(this, name)
        if (name == "event-source")
            var SSEHandler = new FxSSE(obj);
        return obj
    }
}, false);

FxSSE = function(source) {
    var self = this;
    var xhr = null;
    var retry = 3000;
    var id = null;
    var offset = 0;
//    var next_boundary = -1;
    var boundary = "\n"
    var lineQueue = []
    var origin = "" // TODO: derive this from the src argument 
    var src = null;
    var origSrc = null;
    var reconnectTimer = null;
//    source.lastEventId = null;
    
    source.addEventSource = function(eventSrc) {
        // TODO: keep track of sources that we are already connected to
        //       check the spec for information on this
        if (src != null) {
            throw new Error("AlreadyConnected: wait for widespread adoption of SSE specification")
        }
        src = eventSrc
        origSrc = src
        connect()
    }
    
    source.removeEventSource = function(eventSrc) {
        if (eventSrc != origSrc)
            throw new Error("NotConnected to src: " + eventSrc)
        if (reconnectTimer != null) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }
        if (xhr != null) {
            xhr.onreadystatechange = function() { };
            xhr.abort()
//            xhr = null;
            offset = 0;
            lineQueue = []
            id = null;
//            source.lastEventId = null;
        }
        src = null;
        origSrc = null;
    }
    var connect = function() {
//        console.log('connect!')
        if (reconnectTimer != null) {
            reconnectTimer = null;
        }
        // TODO: re-use this xhr connection
        var testUrl = new URL(src);
//        console.log('? ' + src)
        if (xhr == null) {
            if (testUrl.isSameDomain(location.href)) {
    //            console.log('a');
                xhr = new XMLHttpRequest();
            }
            else if (testUrl.isSameParentDomain(location.href)) {
    //            console.log('b')
                xhr = new XSubdomainRequest(testUrl.domain, testUrl.port)
            }
        }
//        console.log('xhr.open')
//        xhr = new XSubdomainRequest("http://sub.www.test.local:7000/echo/static/xdr/sub.html");
//        xhr = new XMLHttpRequest();
        xhr.open('GET', src, true);
        if (id != null) {
            xhr.setRequestHeader('Last-Event-ID', id)
        }
        else {
        }
        xhr.onreadystatechange = function() {
            switch (xhr.readyState) {
                case 4: // disconnect case
                    switch(xhr.status) {
                        // NOTE: This implementation accepts status code 201 as a 301
                        //       replacement for Permenantly Moved.
                        case 201:
//                            console.log('201!');
                            var r = xhr.getAllResponseHeaders()
//                            console.log(r)
//                            console.log('kk')
//                            for (key in r)
//                                console.log(key + ': ' + r[key])
//                            console.log('jj')
                            var newSrc = xhr.getResponseHeader('Location')
//                            console.log('newSrc: ' + newSrc)
                            if (newSrc == null)
                                throw new Error("Invalid 201 Response -- Location missing")
                            var newUrl = new URL(newSrc)
                            var oldUrl = new URL(src);
                            oldUrl.qs = newUrl.qs
                            oldUrl.path = newUrl.path
                            src = oldUrl.render()
//                            console.log('new src: ' + src)
                            dispatch()
                            reconnect()
                            break;
                        case 200:
                            dispatch()
                            reconnect()
                            break
                        default:
                            source.removeEventSource(src)
                    }
                    break
                case 3: // new data
                    process()
                    break
            }
        }
        xhr.send(null);
    }
    var reconnect = function() {
//        console.log('reconnect!')
        // TODO: reuse this xhr connection
//        xhr = null;
        offset = 0
        reconnectTimer = setTimeout(connect, retry)
    }

    var process = function() {
        var stream = xhr.responseText
        if (stream.length < offset) // in safari the offset starts at 256
            return 
        var next_boundary = stream.indexOf(boundary, offset);
        if (next_boundary == -1)
            return
        var line = stream.slice(offset, next_boundary)
        offset = next_boundary + boundary.length
        if (line.length == 0 || line == "\r")
            dispatch()
        else
            lineQueue.push(line) // TODO: is this cross-browser?                
        // TODO: use a while loop here. We don't want a stack overflow
        process() // Keep going until we run out of new lines
    }

    var dispatch = function() {
        var data = "";
        var name = "message";
        lineQueue.reverse() // So we can use pop which removes elements from the end
        while (lineQueue.length > 0) {
            line = lineQueue.pop()
            if (line.slice(-1) == "\r")
                line = line.slice(0, -1)
            var field = null;
            var value = "";
            var j = line.indexOf(':')
            if (j == -1) {
                field = line
                value = ""
            }
            else if (j == 0) {
                continue // This line must be a comment
            }
            else {
                field = line.slice(0, j)
                value = line.slice(j+1)
            }
            if (field == "event")
                name = value
            if (field == "id") {
                id = value
//                source.lastEventId = id;
            }
            if (field == "retry") {
                value = parseInt(value)
                if (!isNaN(value))
                    retry = value
            }
            if (field == "data") {
                if (data.length > 0)
                    data += "\n"
                data += value
            }
        }
        var e = document.createEvent("Events")
        if (data.length > 0 || (name != "message" && name.length > 0)) {
            e.initEvent(name, true, true)
            e.lastEventId = id
            e.data = data
            e.origin = document.domain
            e.source = null
            source.dispatchEvent(e);
        }

    }

}

function test() {
    var s = document.getElementById("ssedom");
    s.addEventSource("http://localhost:8000/?identifier=test&transport=sse2");
    return s;
}