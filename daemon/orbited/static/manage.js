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
        document.getElementById('functions').innerHTML = make_links(['status','start','stop'],"Plugin.get('","',Manager.display_result);\">");
        document.getElementById('plugins').innerHTML = make_links(result[1],"Manager.switch_plugin([[true,'plugin switched to: ","'],'","'])\">");
        self.switch_plugin([result[0],result[1][0]]);
    }

    self.switch_plugin = function(result) {
        if (typeof(result[1]) != "undefined") {
            Plugin = new Library("/_/"+result[1]+"/manage/");
            document.getElementById('name').innerHTML = result[1];
        }
        else {
            document.getElementById('name').innerHTML = "(none)";
        }
        self.display_result(result[0]);
    }

    var make_links = function(items, prescript, midscript, postscript) {
        if ( ! items.length ) {
            return "no active plugins";
        }
	    var links = "<ol>";
        for (var i=0; i < items.length; i++) {
            links += "<li><a href=\"javascript:";
            links += prescript + items[i];
            links += midscript + items[i];
            if ( postscript ) {
                links += postscript + items[i];
            }
            links += "</a></li>";
        }
	    links += "</ol>";
	    return links;
    }
}

Manager = new Manage();
