if (typeof(CTAPITransports) == "undefined")
    CTAPITransports = { 
        downstream: { },
        upstream: { }
    }
CTAPITransports['downstream']['iframe_ie'] = function() {
    var self = this;
    self.url = null;
    self.cb = null;
    self.htmlfile = null;

    self.connect = function(cb, identifier, host, port, location) {
        shell.print("[iframe_ie] connect: ")
        self.cb = cb
        if (typeof(host) == "undefined")
            host = document.domain
        if (typeof(port) == "undefined")
            port = location.port
        if (port == "")
            port = 80
        if (typeof(location) == "undefined")
            location = "/"
        // TODO: use a real random id
        var random_id = "123"
        var attach_fname = '_comet_iframe_' + random_id
        self.url = 'http://' + host + ':' + port + location +
                  '?transport=iframe&js=iframe.js' +
                   '&attach_fname=' + attach_fname
        if (identifier !== null)
            self.url += "&identifier=" + identifier


        self.htmlfile = new ActiveXObject('htmlfile'); // magical microsoft object
        self.htmlfile.open();
        self.htmlfile.write('<html><script>' +
                    'document.domain="' + document.domain + '";' +
                    '</script></html>');
        self.htmlfile.parentWindow[attach_fname] = attach;
        shell.print("[iframe_ie] htmlfile:" + dir(self.htmlfile))
        
        self.htmlfile.close();
        var iframe_div = self.htmlfile.createElement('div');
        self.htmlfile.body.appendChild(iframe_div);
        iframe_div.innerHTML = '<iframe src="' + this.url + '"></iframe>';
        document.attachEvent('on'+'unload', close_htmlfile)
    }
    var attach = function(wnd) {
        shell.print("[iframe_ie] attach: " + wnd)
        wnd.e = self.cb
    }

    var close_htmlfile = function() {
        self.htmlfile = null;
        CollectGarbage();
    }
    var dir = function(obj) {
    var attributeName;
    var attributeValue;
    var str= "";
    
    for (attributeName in obj)
    {
        attributeValue= obj[attributeName];
    
        if (str)
            str+= ", ";
    
            str+= attributeName + " = " + attributeValue + "<br>";
    }
    
    if (str)
        return "{ " + str + " }";
    else
        return "{}";
    }
}

CTAPITransports['downstream']['iframe_ie'].XD = false