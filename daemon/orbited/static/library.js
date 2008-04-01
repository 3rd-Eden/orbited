Library = function() {
    var self = this
    
    self.modules = {}
    
    self.require = function(url) {
        if(url in self.modules) {
            return
        }
        else {
            self.modules[url] = true
            var script = get(url)
            eval(script)
        }
    }
    
    var get = function(url) {
        var xhr = create_xhr()
        xhr.open('GET', url, false)
        xhr.send(null)
        return xhr.responseText
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
