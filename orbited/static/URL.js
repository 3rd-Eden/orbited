URL = function(_url) {
    var self = this;
    var protocolIndex = _url.indexOf("://")
    if (protocolIndex != -1)
        self.protocol = _url.slice(0,protocolIndex)
    else
        protocolIndex = 0
    var domainIndex = _url.indexOf('/', protocolIndex+3)
    if (domainIndex == -1)
        domainIndex=_url.length
    var hashIndex = _url.indexOf("#", domainIndex)
    if (hashIndex != -1)
        self.hash = _url.slice(hashIndex+1)
    else
        hashIndex = _url.length
    var uri = _url.slice(domainIndex, hashIndex)
    var qsIndex = uri.indexOf('?')
    if (qsIndex == -1)
        qsIndex=uri.length
    self.path = uri.slice(0, qsIndex)
    self.qs = uri.slice(qsIndex+1)
    if (self.path == "")
        self.path = "/"
    var domain = _url.slice(protocolIndex+3, domainIndex)
    var portIndex = domain.indexOf(":")
    if (portIndex == -1) {
        self.port = 80
        portIndex = domain.length
    }
    else {
        self.port = parseInt(domain.slice(portIndex+1))
    }
    if (isNaN(this.port))
        throw new Error("Invalid _url")
    self.domain = domain.slice(0, portIndex)
    self.render = function() {
        var output = ""
        if (typeof(self.protocol) != "undefined")
            output += self.protocol + "://"
        output += self.domain
        if (self.port != 80 && typeof(self.port) != "undefined" && self.port != null)
            if (typeof(self.port) != "string" || self.port.length > 0)
                output += ":" + self.port
        if (typeof(self.path) == "undefined" || self.path == null)
            output += '/'
        else
            output += self.path
        if (self.qs.length > 0)
            output += '?' + self.qs
        if (typeof(self.hash) != "undefined")
            output += "#" + self.hash
        return output
    }
    self.isSameDomain = function(_url) {
        _url = new URL(_url)
        return (_url.port == self.port && _url.domain == self.domain)
    }
/*    self.isSameParentDomain = function(_url) {
        _url = new URL(_url)
        var parts = _url.domain.split('.')
        for (var i = 0; i < parts.length-1; ++i) {
            var new_domain = parts.slice(i).join(".")
            if (new_domain == self.domain)
                return true;
        }
    }
*/
    self.isSameParentDomain = function(_url) {
        _url = new URL(_url)
        var parts = document.domain.split('.')
        var orig_domain = document.domain
        for (var i = 0; i < parts.length-1; ++i) {
            var new_domain = parts.slice(i).join(".")
            if (orig_domain == new_domain)
                return true;
        }
    }

}