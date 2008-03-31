if (typeof(CSPTransports) == "undefined")
    CSPTransports = { }

CSPTransports['iframe'] = function() {
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
        window[attach_fname] = attach
        self.url = 'http://' + host + ':' + port + location +
                   '?transport=iframe&js=iframe.js&' +
                   '&attach_fname=' + attach_fname
        if (identifier !== null)
            self.url += "&identifier=" + identifier
        ifr = document.createElement('iframe');
        hide_iframe(ifr)
        ifr.setAttribute('src', self.url);
        document.body.appendChild(ifr);
        document.domain = extract_xss_domain(document.domain)
    }

    var message_cb = function(msg) {
        
        window.setTimeout(function() {        
            self.cb(msg)
            kill_load_bar(ifr)
        }, 0)
    }

    var attach = function(wnd) {
        wnd.e = message_cb
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
    
    var extract_xss_domain = function(old_domain) {
        domain_pieces = old_domain.split('.');
        if (domain_pieces.length === 4) {
            var is_ip = !isNaN(Number(domain_pieces.join('')));
            if (is_ip)
                return old_domain;
        }
        return domain_pieces.slice(-2).join('.');
    }
}