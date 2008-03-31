if (typeof(CTAPITransports) == "undefined")
    CTAPITransports = { 
        downstream: { },
        upstream: { }
    }
CTAPITransports['downstream']['iframe_fxcx'] = function() {
    var self = this;
    self.url = null;
    self.cb = null;
    var load_kill_ifr = null;
    var ifr = null;

    self.connect = function(cb, identifier, host, port, location) {
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
        window.location[attach_fname] = attach
        self.url = 'http://' + host + ':' + port + location +
                  '?transport=iframe&js=iframe_fxcx.js' +
                   '&attach_fname=' + attach_fname
        if (identifier !== null)
            self.url += "&identifier=" + identifier
        ifr = document.createElement('iframe');
        hide_iframe(ifr)
        ifr.setAttribute('src', self.url);
        document.body.appendChild(ifr);
    }

    var message_cb = function(msg) {
        window.setTimeout(function() {        
            self.cb(msg)
            kill_load_bar(ifr)
        }, 0)
    }

    var attach = function(wnd) {
        wnd.location.e = message_cb
        shell
        kill_load_bar()
    }
    var hide_iframe = function (ifr) {
        ifr.style.display = 'block';
        ifr.style.width = '0';
        ifr.style.height = '0';
        ifr.style.border = '0';
        ifr.style.margin = '0';
        ifr.style.padding = '0';
        ifr.style.overflow = 'hidden';
        ifr.style.visibility = 'hidden';
    }

    var kill_load_bar = function () {
        if (load_kill_ifr === null) {
            load_kill_ifr = document.createElement('iframe');
            hide_iframe(load_kill_ifr);
    //      document.body.appendChild(load_kill_ifr);
        }
    //    load_kill_ifr.src = "about:blank"
        document.body.appendChild(load_kill_ifr);
        document.body.removeChild(load_kill_ifr);
    }
    

}