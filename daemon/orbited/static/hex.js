hexToBytes = function(str) {
//  str = str.toUpperCase()
    if (str.length == 0)
        return []
    if (str.length % 2 != 0)
        throw new Error ("Invalid Hex String (must be pairs)")
    var output = []
    for (var i =0; i < str.length; i+=2) {
        target = str.charAt(i) + str.charAt(i+1)
        output.push(parseInt(target, 16))
    }
    return output
}


// TODO: why doesn't this work? 
bytesToHex = function(bytes) {
    var output = []
    for (var i = 0; i < bytes.length; ++i) {
        var val = bytes[i].toString(16)
        if (val.length == 1)
            output.push("0")
        output.push(val)
    }
    return output.join("")
}