TransportChooser = {}
TransportChooser.create = function() {
    // Browser detect by Frank Salim
    var browser = null;
    if (typeof(ActiveXObject) != "undefined") {
        browser = 'ie'
    } else if (navigator.product == 'Gecko' && window.find && !navigator.savePreferences) {
        browser = 'firefox'
    } else if((typeof window.addEventStream) === 'function') {
        browser = 'opera'
    } else {
        throw new Error("couldn't detect browser")
    }
    
    switch(browser) {
        case 'firefox':
            return new XHRStream();
        case 'ie':
            return new HTMLFile();
        case 'opera':
            return new SSE();
    }
}