var testData = null;
xhr = new XMLHttpRequest()
xhr.open('GET', '/_/static/protocols/xmpp/dev/testData.xml', true)
xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
        testData = xhr.responseText
        startTimer()
    }
}
xhr.send(null);
var index = 0;
var READ_INCREMENT = 10000;
var TIMER_INCREMENT = 100;
var timer = null;
function startTimer() {
    timer = setInterval(doRead, TIMER_INCREMENT )
}


// How to use the parser Start
var parser = new XMLStreamParser()
parser.onread = function(node) {
    console.log('receivedNode: ', node)
}
// End


function doRead() {
    var data = testData.slice(index, index+READ_INCREMENT);
    index+= READ_INCREMENT;
    parser.receive(data);
    if (index > testData.length) {
        clearInterval(timer);
    }
}
