/*
get all.js
check document.domain: are we xD?
    if we have any non xD in all.js
        does crossPost work
*/

/*
Orbited.require("ctapi/downstream/iframe.js")
Orbited.require("ctapi/downstream/iframe_fxcx.js")
Orbited.require("ctapi/downstream/sse.js")
Orbited.require("ctapi/downstream/iframe_ie.js")
*/

alljs = new function() {
    var firefox = ['iframe_fxcx', 'iframe']
    var ie = ['iframe_ie', 'iframe']
    var safari = ['iframe']
    var opera = ['sse']

    if (typeof(ActiveXObject) != "undefined") {
        var browser = ie
    } else if (navigator.product == 'Gecko' && window.find && !navigator.savePreferences) {
        var browser = firefox
    } else if((typeof window.addEventStream) === 'function') {
        var browser = opera
    } else {
        var browser = ["iframe"]    
    }
        
    document.writeln("browser has "+ browser)

    for (var i=0; i<browser.length; i++)
        Orbited.require("ctapi/downstream/" + browser[i] + ".js")
        
}
