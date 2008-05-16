URL = function(url) {
    var self = this;
    var protocolIndex = url.indexOf("://")
    if (protocolIndex != -1)
        self.protocol = url.slice(0,protocolIndex)
    else
        protocolIndex = 0
    var domainIndex = url.indexOf('/', protocolIndex+3)
    if (domainIndex == -1)
        domainIndex=url.length
    var hashIndex = url.indexOf("#", domainIndex)
    if (hashIndex != -1)
        self.hash = url.slice(hashIndex+1)
    else
        hashIndex = url.length
    var uri = url.slice(domainIndex, hashIndex)
    var qsIndex = uri.indexOf('?')
    print('qsIndex: ' + qsIndex);
    if (qsIndex == -1)
        qsIndex=uri.length
    self.path = uri.slice(0, qsIndex)
    self.qs = uri.slice(qsIndex+1)
    print('qs is: ' + self.qs)
    if (self.path == "")
        self.path = "/"
    var domain = url.slice(protocolIndex+3, domainIndex)
    var portIndex = domain.indexOf(":")
    if (portIndex == -1) {
        self.port = 80
        portIndex = domain.length
    }
    else {
        self.port = parseInt(domain.slice(portIndex+1))
    }
    if (isNaN(this.port))
        throw new Error("Invalid url")
    self.domain = domain.slice(0, portIndex)
    self.render = function() {
        var output = ""
        if (typeof(self.protocol) != "undefined")
            output += self.protocol + "://"
        output += self.domain
        if (self.port != 80 && typeof(self.port) != "undefined" && self.port != null)
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
    self.isSameDomain = function(url) {
        url = new URL(url)
        return (url.port == self.port && url.domain == self.domain)
    }
/*    self.isSameParentDomain = function(url) {
        url = new URL(url)
        var parts = url.domain.split('.')
        for (var i = 0; i < parts.length-1; ++i) {
            var new_domain = parts.slice(i).join(".")
            if (new_domain == self.domain)
                return true;
        }
    }
*/
    self.isSameParentDomain = function(url) {
        url = new URL(url)
        var parts = document.domain.split('.')
        var orig_domain = document.domain
        for (var i = 0; i < parts.length-1; ++i) {
            var new_domain = parts.slice(i).join(".")
            if (orig_domain == new_domain)
                return true;
        }
    }

}