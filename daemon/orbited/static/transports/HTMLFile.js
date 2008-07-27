HTMLFile = function() {
    var self = this;
    id = ++HTMLFile.prototype.i;
    HTMLFile.prototype.instances[id] = self
    var htmlfile = null
    var url = null;
    self.onread = function(packet) { }

    self.connect = function(_url) {
        if (self.readyState == 1) {
            throw new Error("Already Connected")
        }
        url = new URL(_url)
        url.setQsParameter('transport', 'htmlfile')
        url.setQsParameter('frameID', id.toString())
//        url.hash = id.toString()
        self.readyState = 1
        doOpen()
    }
    self.close = function() {
        // TODO: I think this works -- couldn't test in IE. Will someone do that?
        //       -mcarter 7-26-08
        htmlfile = null;
        CollectGarbage();
    }
    var doOpenIfr = function() {
        
        var ifr = document.createElement('iframe')
        ifr.src = url.render()
        document.body.appendChild(ifr)
    }

    var doOpen = function() {
        htmlfile = new ActiveXObject('htmlfile'); // magical microsoft object
        htmlfile.open();
        htmlfile.write('<html><script>' + 'document.domain="' + document.domain + '";' + '</script></html>');
        htmlfile.parentWindow.HTMLFile = HTMLFile;
        htmlfile.close();
        var iframe_div = htmlfile.createElement('div');
        htmlfile.body.appendChild(iframe_div);
        iframe_div.innerHTML = "<iframe src=\"" + url.render() + "\"></iframe>";
    }
    
    self.receive = function(id, name, args) {
        packet = {
            id: id,
            name: name,
            args: args
        }
        self.onread(packet)
    }
}

HTMLFile.prototype.i = 8
HTMLFile.prototype.instances = {}