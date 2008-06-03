fromBin = function(bin) { val = 0; for (var i = bin.length-1; i >= 0; i--) { if (bin[bin.length-i-1] == '1') { val += Math.pow(2, i) } } return val }

charByteLength = function(byte) {
    if ((byte & 128) == 0)
        return 1
    if ((byte & 240) == 240)
        return 4
    if ((byte & 224) == 224)
        return 3
    if ((byte & 192) == 192)
        return 2
    throw new Error("Invalid UTF-8 encoded data...")
}

bytesToUTF8 = function(bytes) {
    var output = []
    for (var i = 0; i < bytes.length; ++i) {
        var startByte = bytes[i]
        var val = null;
        var len = charByteLength(startByte) 
        switch (len) {
            case 1:
                val = bytes[i];
                break;
            case 2:
                val = ((bytes[i] - 192) << 6)  + (bytes[i+1] - 128)
                break
            case 3:
                val = ((bytes[i] - 224) << 12) + ((bytes[i+1] - 128) << 6) + (bytes[i+2] - 128)
                break
            case 4:
                val = ((bytes[i] - 240) << 18) + ((bytes[i+1] - 128) << 12) + ((bytes[i+2] - 128) << 6) + (bytes[i+3] - 128)
                break
        }
        i += (len -1)
        output.push(String.fromCharCode(val))
    }
    return output.join("")
}


UTF8ToBytes = function(str) {
    var output = []
    for (var i = 0; i < str.length; ++i) {
        var val = str.charCodeAt(i)
        if (val < 128) { // largest 1-byte unicode value
            output.push(val)
            continue
        }
        if (val < 2047) { // largest 2-byte unicode value
            var firstByte = (val >> 6) + 192
            var secondByte = val - (firstByte << 6)
            output.push(firstByte)
            output.push(secondByte)
            continue
        }
        if (val < 65535) { // largest 3-byte unicode value
            var firstChunk = (val >> 12)
            var temp1 = (firstChunk << 12)
            var secondChunk = (val - temp1) >> 6
            var thirdChunk = (val - temp1 - (secondChunk << 6))
            var firstByte = firstChunk + 224
            var secondByte = secondChunk + 128
            var thirdByte = thirdChunk + 128
            output.push(firstByte)
            output.push(secondByte)
            output.push(thirdByte)
            continue
        }
        if (val < 2097151 ) { // largest 4-byte unicode value
            var firstChunk = (val >> 18)
            var temp1 = (firstChunk << 18)
            var secondChunk = (val - temp1) >> 12
            var temp2 = secondChunk << 12
            var thirdChunk = (val - temp1 - temp2) >> 6
            var fourthChunk = (val - temp1 - temp2 - (thirdChunk << 6))
            var firstByte = firstChunk + 240
            var secondByte = secondChunk + 128
            var thirdByte = thirdChunk + 128
            var fourthByte = fourthChunk + 128
            output.push(firstByte)
            output.push(secondByte)
            output.push(thirdByte)
            output.push(fourthByte)
            continue
        }
        throw new Error("Invalid UTF-8 string")
    }
    return output
}

    orig = "당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 새로운 가정에 환영당신의 "
orig2 = orig + orig
//orig2 = orig2 + orig2 + orig2
//orig2 = orig2 + orig2
orig3 = UTF8ToBytes(orig2)
benchmark = function(f, arg) {
    start = new Date()
        f(arg);
    end = new Date();
    return end - start
}

translateKorean = function(orig) {
//    for (var i = 0; i < 1; ++i) {
        bytesToUTF8(UTF8ToBytes(orig))
//    }
}

translateKorean1 = function(orig) {
//    for (var i = 0; i < 1; ++i) {
        UTF8ToBytes(orig)
//    }
}
translateKorean2 = function(orig) {
//    for (var i = 0; i < 1; ++i) {
        bytesToUTF8(orig)
//    }
}

onload = function() {
    alert('starting tests')
    document.body.innerHTML += benchmark(translateKorean, orig2) + '<br>\n'
    document.body.innerHTML += benchmark(translateKorean1, orig2) + '<br>\n'
    document.body.innerHTML += benchmark(translateKorean2, orig3) + '<br>\n'    
    alert('tests finished')
}
