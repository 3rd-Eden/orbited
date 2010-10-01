jsio('from base import Class');
jsio('import logging');
jsio('from net.protocols.mspp import MSPPStream, MSPPProtocol');

exports.logging = logging;

// autodetect host + port!!!
exports.settings = { 'host': 'localhost', 'port': 8000, 'path': '/csp'};

var multiplexer = null;
exports.TCPSocket = Class(MSPPStream, function() {
    this.init = function() {
        this.setEncoding('plain');
        if (multiplexer == null) {
            multiplexer = new MSPPProtocol();
            multiplexer.setTransport('csp', {"url": "http://" + exports.settings.host + ":" + exports.settings.port + exports.settings.path});
        }
        this.setMultiplexer(multiplexer);
    }
});
