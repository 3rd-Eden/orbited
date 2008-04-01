// shell.js

Shell = function(output){
    var self = this
    self.output = output
    
    self.print = function(s) {
        s = self.escape(s)
        self.output.innerHTML += "&rarr; " + s + "<br>"
    	self.output.scrollTop = self.output.scrollHeight     
    }
    
    
    self.escape = function(s)
    {
        return s   
        s = s.replace("&", "&amp;", "g")
        s = s.replace("<", "&lt;", "g")
        s = s.replace(">", "&gt;", "g")
        s = s.replace(" ", "&nbsp;", "g")

        return s
    }
    
}