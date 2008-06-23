Orbited = {
    connect: function (event_cb /* args 1-3 are token parts */) {
        var tokens = Array.prototype.slice.call(arguments, 1)
        if (tokens.length == 3)
            var token = tokens[0] + ", " + tokens[2] + ', ' + tokens[1]
        else
            var token = tokens[0]
    
        var conn = new BaseTCPConnection()
        var connUrl = new URL(location.href)
        if (typeof(ORBITED_DOMAIN) != "undefined") 
            connUrl.domain = ORBITED_DOMAIN
        if (typeof(ORBITED_PORT) != "undefined")
            connUrl.port = ORBITED_PORT
        connUrl.path = "/legacy"
        connUrl.qs = ""
        conn.onread = event_cb
        conn.onopen = function(data) {
            conn.send(token);
        }
        conn.connect(connUrl.render())
    },

    create_xhr: function () {
        try { return new ActiveXObject('MSXML3.XMLHTTP'); } catch(e) {}
        try { return new ActiveXObject('MSXML2.XMLHTTP.3.0'); } catch(e) {}
        try { return new ActiveXObject('Msxml2.XMLHTTP'); } catch(e) {}
        try { return new ActiveXObject('Microsoft.XMLHTTP'); } catch(e) {}
        try { return new XMLHttpRequest(); } catch(e) {}
        throw new Error('Could not find XMLHttpRequest or an alternative.');
  }

    
}
