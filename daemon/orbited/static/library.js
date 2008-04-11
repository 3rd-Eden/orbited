Library = function() {
    var self = this
    self.modules = {}

    if(typeof(arguments[0]) != "undefined")
        var baseurl = arguments[0]

    self.require = function(url) {
        if(url in self.modules) {
            return
        }
        else {
            self.modules[url] = true            
            self.get(url)
        }
    }

    self.get = function(url, cb) {
        if (typeof(cb) == 'undefined') {
            var cb = function(x) { return x; }
        }
        if (url.substring(0,7) != "http://") {
            url = baseurl + url;
        }
        var xhr = create_xhr()
        xhr.open('GET', url, false)
        xhr.send(null)
        return cb(eval(xhr.responseText))
    }

    var create_xhr = function () {
        try { return new ActiveXObject('MSXML3.XMLHTTP') } catch(e) {}
        try { return new ActiveXObject('MSXML2.XMLHTTP.3.0') } catch(e) {}
        try { return new ActiveXObject('Msxml2.XMLHTTP') } catch(e) {}
        try { return new ActiveXObject('Microsoft.XMLHTTP') } catch(e) {}
        try { return new XMLHttpRequest() } catch(e) {}
        throw new Error('Could not find XMLHttpRequest or an alternative.')
    }
}

Orbited = new Library("/_/static/")
