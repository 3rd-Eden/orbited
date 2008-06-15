HTMLFile = function() {
    var self = this;
//    HTMLFile.prototype.i +=1 
    HTMLFile.prototype.instances[HTMLFile.prototype.i] = self

    self.onread = function(packet) { }

    self.connect = function(_url) {
        if (self.readyState == 1) {
            throw new Error("Already Connected")
        }
        url = new URL(_url)
        url.setQsParameter('transport', 'htmlfile')
        url.hash = "0"
        self.readyState = 1
        open()
    }

    open = function() {
        source = document.createElement("iframe")
        source.src = url.render()
        document.body.appendChild(source)
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

HTMLFile.prototype.i = 0
HTMLFile.prototype.instances = {}