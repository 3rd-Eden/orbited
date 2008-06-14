var testData = null;
xhr = new XMLHttpRequest()
xhr.open('GET', '/_/static/protocols/xmpp/dev/testData.xml', true)
xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
        testData = xhr.responseText
        console.log("got testData, " + testData.length + " bytes")
        startTimer()
    }
}
xhr.send(null);
var index = 0;
var READ_INCREMENT = 100;
var TIMER_INCREMENT = 100;
var timer = null;
function startTimer() {
    timer = setInterval(doRead, TIMER_INCREMENT )
}

function doRead() {
    var data = testData.slice(index, index+READ_INCREMENT);
    index+= READ_INCREMENT;
    dataReceived(data);
    if (index > testData.length) {
        clearInterval(timer);
        console.log('finished reading data');
    }
}

var buffer = ""
function dataReceived(data) {
    buffer += data
    // CODE HERE
    console.log('read! buffer.length: ' + buffer.length)
    if (false) {
        elementReceived(element);
    }
}


function elementReceived(rootNode) {
    console.log("Element Received:", rootNode)
}