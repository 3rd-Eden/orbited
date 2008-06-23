Orbited = {
    connect: function (event_cb, token) {
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
    }
}
