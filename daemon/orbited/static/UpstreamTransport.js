UpstreamTransport = function(url, id) {
    var self = this

    self.send = function(s) {
        /* TODO, take multiple arguments?
         *  more robust JSON encode for multiple browsers
         *  and queued messages
         */
        var qs = '?data=' + s + "&id=" + id
        
        var xhr = create_xhr()
        xhr.open('GET', url+qs, true);
        xhr.send(null);
        
        var cb = {
            success: function(data) { },
            failure: function(err) { }
        }
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    cb.success(xhr.responseText)
                }
                else {
                    cb.failure(xhr.status)
                }
            }
        }
        return cb;
    }
    
    var create_xhr = function() {
        try { return new ActiveXObject("Msxml2.XMLHTTP"); } catch (e) {}
        try { return new ActiveXObject("Microsoft.XMLHTTP"); } catch (e) {}
        try { return new XMLHttpRequest(); } catch(e) {}
        return null;
    }
}
