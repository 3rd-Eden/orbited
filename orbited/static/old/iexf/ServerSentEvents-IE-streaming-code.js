version = 1.0
onload = function() {
//    alert('loaded!');
// TODO: sse reconnecting!
}
origDomain = document.domain
offset = 0
lastLength = 0
boundary = '\r\n'
lineQueue = []
dummyTextNode = null;

var poll = function() {
//    alert('polling')
    var bodyLen = null;
    try {
        bodyLen = document.body.childNodes[0].innerText.length
    }
    catch(e) {
        return
    }
//    alert('bodyLen: ' + bodyLen)
    if (dummyTextNode == null) {
        dummyTextNode = document.createTextNode(".")
    }
    if (bodyLen > lastLength) {
        lastLength = bodyLen
        process()
    }
    else { 
        document.body.childNodes[0].appendChild(dummyTextNode)
        var bodyLen2 = document.body.childNodes[0].innerText.length
        if (bodyLen2 >= bodyLen+5) {
            lastLength = bodyLen2-1
            process()
            var t1 = document.body.childNodes[0].childNodes[0]
//            document.body.childNodes[0].removeChild(t1)
//            offset = 0;
        }
        document.body.childNodes[0].removeChild(dummyTextNode)
    }
}

var process = function() {
    stream = document.body.childNodes[0].innerText
    if (stream.length < offset) // in safari the offset starts at 256 
        return 
    var next_boundary = stream.indexOf(boundary, offset);
    var line = null;
    if (next_boundary == -1)
        return
    line = stream.slice(offset, next_boundary)
    offset = next_boundary + boundary.length
    if (line.length == 0) {
        return dispatch()
    }
    else {
        lineQueue.push(line) // TODO: is this cross-browser?                
    }
    // TODO: use a while loop here. We don't want a stack overflow
    process() // Keep going until we run out of new lines
}
id = null;
var dispatch = function() {
    var data = "";
    var name = "message";
    lineQueue.reverse() // pop removes elements from the end
    while (lineQueue.length > 0) {
        line = lineQueue.pop()
        var field = null;
        var value = "";
        var j = line.indexOf(':')
        if (j == -1) {
            field = line
            value = ""
        }
        else if (j == 0) {
            continue 
        }
        else {
            field = line.slice(0, j)
            value = line.slice(j+1)
        }
        if (field == "event")
            name = value
        if (field == "id") {
            id = value
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
    if (data.length > 0 || (name != "message" && name.length > 0)) {
        parent.receive(name, data, origDomain, id)
    }
}
widen = function() {
    var newDomain = null;
    var parts = document.domain.split('.')
    origDomain = document.domain
    for (var i = 0; i < parts.length-1; ++i) {
        document.domain = parts.slice(i).join(".")
//        alert('trying: ' + document.domain)
        try {
            parent.document
            newDomain = document.domain
            break;
        }
        catch(e) {
//            alert(e.name + ': ' + e.message)
        }
    }
    if (newDomain == null)
        throw new Error("XXInvalid document.domain for cross-frame communication")    
}
widen();
timer = setInterval(poll, 20)
//alert('code set');