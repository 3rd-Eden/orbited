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
if (isNaN(retry))
    retry = 3000;
function encodeQS(o) {
    output = ""
    for (key in o)
        output += "&" + key + "=" + o[key]
    return output.slice(1)
}

window.onload = function() {
    setTimeout(function() {
        var form = {}
        form['transport'] = 'htmlfile'
        form['retry'] = retry
        form['id'] = lastEventId
        var r = parseInt(origForm['reload'])
        if (isNaN(r))
            form['reload'] = '0'
        else
            form['reload'] = r+1
        var newUrl = base + '?' + encodeQS(form) + "#" + hash
        f("message", "reloading: " + newUrl , lastEventId, null);
//        alert(newUrl);
        location.href=newUrl;
     }, retry);
}

//alert(origDomain)
var topDomain = null;
var id = parseInt(location.hash.slice(1));
var parts = document.domain.split('.')
if (parts.length == 1) {
    try {
        document.domain = document.domain
        parent.CometTransport
        topDomain = document.domain
    }
    catch(e) {
    }
}
else {
    for (var i = 0; i < parts.length-1; ++i) {
        document.domain = parts.slice(i).join(".")
        try {
            parent.XSubdomainRequest.prototype
            topDomain = document.domain
            break;
        }
        catch(e) {
//            alert(e.name + ': ' + e.message)
        }
    }
}
if (topDomain == null)
    throw new Error("Invalid document.domain for cross-frame communication")
f = parent.CometTransport.instances[id].receive;
receive = function (name, data, _id, _retry) {
    if (_id != null) {
//        alert('set id=' + _id);
        lastEventId = _id;
    }
    if (_retry != null)
        retry = _retry;
     f(name, data, _id, _retry);
}

