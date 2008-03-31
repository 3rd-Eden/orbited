if (typeof(CTAPITransports) == "undefined")
    CTAPITransports = { 
        downstream: { },
        upstream: { }
    }

CTAPITransports['upstream']['xhr'] = function(url, id) {
    var self = this;

    self.connect = function(cb, args) {
        cb(args)
    },

    self.send = function(s) {
        /* TODO, take multiple arguments?
         *  more robust JSON encode for multiple browsers
         *  and queued messages
         */
        var qs = '?payload=' + s + "&identifier=" + id;
        
        var xhr = create_xhr();
        xhr.open('GET', url+qs, false);
        xhr.send(null);
        
        var cb = {
            success: function(data) { },
            failure: function(err) { }
        };
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    cb.success(xhr.responseText)
                }
                else {
                    cb.failure(xhr.status)
                }
            }
        };
        return cb;
    };
    
    var create_xhr = function() {
        try { return new ActiveXObject("Msxml2.XMLHTTP"); } catch (e) {}
        try { return new ActiveXObject("Microsoft.XMLHTTP"); } catch (e) {}
        try { return new XMLHttpRequest(); } catch(e) {}
        return null;
    };
};