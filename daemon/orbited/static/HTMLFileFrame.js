var origDomain = document.domain
var pieces = location.href.split("#")
var full = pieces[0]
var hash = pieces[1]
pieces = full.split('?')
var base = pieces[0]
//var newUrl = pieces[0] +  "&x=y" + "#" + pieces[1]
function decodeQS(qs) {
//    alert('a')
    if (qs.indexOf('=') == -1) return {}
    var result = {}
    var chunks = qs.split('&')
    for (var i = 0; i < chunks.length; ++i) {
        var cur = chunks[i]
        pieces = cur.split('=')
        result[pieces[0]] = pieces[1]
    }
    return result
}
//alert('b: ' + pieces[1]);
var origForm = decodeQS(pieces[1])
lastEventId = parseInt(origForm['id'])
if (isNaN(lastEventId)) {
    lastEventId = 0
}
retry = parseInt(origForm['retry'])
id = parseInt(origForm['frameID']);

if (isNaN(retry))
    retry = 50;
function encodeQS(o) {
    output = ""
    for (key in o)
        output += "&" + key + "=" + o[key]
    return output.slice(1)
}

window.onload = function() {
    // TODO: Implement some kind of fault tolerance. That is, if a stream
    //       closes, (we get onload), this reconnect happens, but that fails.
    //       No part of the code is left running to cause a reconnect. We
    //       need to interface that with parent.Orbited.singleton.HTMLFile.instances[id]
    //       somehow.
    return
    var form = {}
    form['ack'] = lastEventId
    form['frameID'] = id
    var r = parseInt(origForm['reload'])
    if (isNaN(r))
        form['reload'] = '0'
    else
        form['reload'] = r+1
    var newUrl = base + '?' + encodeQS(form)
    location.href=newUrl;
}
//alert(origDomain)
try {
    parent.Orbited
//    alert('same domain.');
}
catch(e) {
// TODO: test out cross-domain stuff... :-(
    alert('no parent.Orbited')
    alert('document.domain is ' + document.domain);
    var topDomain = null;
    var parts = document.domain.split('.')
    if (parts.length == 1) {
        try {
            document.domain = document.domain
            parent.Orbited
            topDomain = document.domain
        }
        catch(e) {
        }
    }
    else {
        for (var i = 0; i < parts.length-1; ++i) {
            document.domain = parts.slice(i).join(".")
            try {
                parent.Orbited
                topDomain = document.domain
                break;
            }
            catch(e) {
    //            alert(e.name + ': ' + e.message)
            }
        }
    }
    if (topDomain == null) {
        alert('invalid document.domain.')
        throw new Error("Invalid document.domain for cross-frame communication")
    }
}
//alert('worked out?');
f = parent.Orbited.singleton.HTMLFile.instances[id].receive;
e = function(packets) {
//    alert('packets! ' + packets);
    for (var i =0; i < packets.length; ++i) {
        var packet = packets[i]
        var _id = packet[0]
        if (_id != null) {
    //        alert('set id=' + _id);
            lastEventId = _id;
        }

        f(packet[0], packet[1], packet[2])
    }
}

h = function() {
    // TODO: heartbeats and timing out the connection!
}