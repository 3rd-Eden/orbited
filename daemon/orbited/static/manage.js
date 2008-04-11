function Manage() {
    var self = this;

    self.display_result = function(result) {
	    var output = document.getElementById('output');
	    output.innerHTML=result[1];
	    var success = result[0];
	    //nice red/green indicator of whether the last call worked
	    var flag = document.getElementById('flag');
	    if (success) {
		    flag.innerHTML = 'Success';
		    flag.style.color = 'green';
	    }
	    else {
		    flag.innerHTML = 'FAIL';
		    flag.style.color = 'red';
	    }
    }

    self.load = function(result) {
        document.getElementById('plugins').innerHTML = make_links(result[1],"Manager","switch_plugin");
        self.switch_plugin([result[0],result[1][0]]);        
    }

    self.switch_plugin = function(result) {
        Plugin = new Library("/"+result[1].replace(".","/")+"/manage/");
        document.getElementById('name').innerHTML = result[1];
        self.display_result(result[0]);
    }

    var make_links = function(plugins) {
	    var links = "<ol>";
	    for (var i=0; i < plugins.length; i++) {
		    links += "<li><a href=\"javascript:";
		    links += "Manager.switch_plugin([[true,";
            links += "'plugin switched to: "+plugins[i];
            links += "'],'"+plugins[i]+"']);\">";
		    links += plugins[i]+"</a></li>";
	    }
	    links += "</ol>";
	    return links;
    }
}

Manager = new Manage();
