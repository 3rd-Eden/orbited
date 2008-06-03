hexChars = '0123456789ABCDEF'

hexToBase10 = { }
base10ToHex = { }
for (var i = 0; i < hexChars.length; ++i) {
    hexToBase10[hexChars[i]] = i
    base10ToHex[i] = hexChars[i]
}

hexToBytes = function(str) {
    if (str.length == 0)
        return []
    if (str.length % 2 != 0)
        throw new Error ("Invalid Hex String (must be pairs)")
    var output = []
    for (var i =0; i < str.length; i+=2) {
        var val = (hexToBase10[str[i]] << 4) + (hexToBase10[str[i+1]])
        output.push(val)
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
/*
bytesToHex = function(bytes) {
    var output = []
    for (var i = 0; i < bytes.length; ++i) {
        var byte = bytes[i]
        var hex1 = byte >> 4
        output.push(base10ToHex[hex1])
        output.push(base10ToHex[byte - (hex1 << 4)])
    }
    return output.join("")
}
*/