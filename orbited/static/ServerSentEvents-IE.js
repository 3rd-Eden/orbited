var oldLoad = function() { }
if (window.onload) 
    oldLoad = window.onload

var newLoad = function() {
    base2.DOM.bind(document)
    sources = document.getElementsByTagName("event-source")
    for (var i = 0; i < sources.length; ++i) {
        source = sources[i]
        base2.DOM.bind(source)
        var SSEHandler = new IESSE(source);
    }
    var createElement = document.createElement
    document.createElement = function(name) {
        var obj = null;
        if (typeof(createElement.call) == "undefined") // IE modification
            obj = createElement(name)
        else 
            obj = createElement.call(this, name)
        if (name == "event-source")
            var SSEHandler = new IESSE(obj);
        return obj
    }
}
window.onload = function() {
    newLoad()
    oldLoad()
}

function repr(d) {
    while (d.indexOf('\r') > -1 || d.indexOf('\n') > -1) {
        d = d.replace('\r', '\\r').replace('\n', '\\n')
    }     
    return d
}

IESSE = function(source) {
    var self = this;
    var ifr = null;
    var retry = 3000;
    var id = null;
    var offset = 0;
    var lastLength = 0;
//    var next_boundary = -1;
    var boundary = "\r\n"
    var lineQueue = []
    var origin = "" // TODO: derive this from the src argument 
    var src = null;
    var ifrInitialized = false;
    var ifrInitialized2 = false;
    dummyTextNode = null;
//    source.lastEventId = null;
    
    source.addEventSource = function(eventSrc) {
        // TODO: keep track of sources that we are already connected to
        //       check the spec for information on this
        if (src != null) {
            throw new Error("AlreadyConnected: wait for widespread adoption of SSE specification")
        }
        src = eventSrc
        connect()
    }
    source.removeEventSource = function(eventSrc) {
        if (eventSrc != src)
            throw new Error("NotConnected to src: " + eventSrc)
        if (xhr != null) {
            xhr.onreadystatechange = function() { };
            xhr.abort()
//            xhr = null;
            offset = 0;
            lineQueue = []
            id = null;
//            source.lastEventId = null;
        }
        src = null;
    }
    var poll = function() {
        var bodyLen = null;
/*        if (!ifrInitialized) {
            if (ifr.contentWindow.document) {
                print ('setting iframe document.domain')
                var s = ifr.contentWindow.document.createElement("<script src='alert.js'>")
                ifr.contentWindow.document.body.insertBefore(s)
                ifrInitialized = true;
                print ('iframe document.domain set')
                print ('setting document.domain')
                document.domain = document.domain;
            }
            return;
        }

        if (!ifrInitialized2) {
            
            ifrInitialized2 = true;
            print ('accessing iframe document.domain')
            print('iframe document.domain: ' + ifr.contentWindow.document.domain)
            print('initialized');
        }
        else
            print('what?')
//            catch (e) {
//                return
//            }
//        } */
        try {
//            print('ala')
//            print("ifr domain: " + ifr.contentWindow.document.domain)
            bodyLen = ifr.contentWindow.document.body.childNodes[0].innerText.length
//            print ("bodyLen: " + bodyLen)
        }
        catch(e) {
            return
        }

        if (dummyTextNode == null) {
            dummyTextNode = ifr.contentWindow.document.createTextNode(".")
        }
        if (bodyLen > lastLength) {
            lastLength = bodyLen
            process()
        }
        else { /*408 234 1363*/
            ifr.contentWindow.document.body.childNodes[0].appendChild(dummyTextNode)
            var bodyLen2 = ifr.contentWindow.document.body.childNodes[0].innerText.length
            if (bodyLen2 >= bodyLen+5 && false) {
                lastLength = bodyLen2-1
                process()
//                toDelete = dummyTextNode.replaceAdjacentText("beforeBegin", ":woot\r\n")
//                var t2 = ifr.contentWindow.document.createTextNode("")
                var t1 = ifr.contentWindow.document.body.childNodes[0].childNodes[0]
//                ifr.contentWindow.document.body.childNodes[0].replaceChild(t1, t2)
                ifr.contentWindow.document.body.childNodes[0].removeChild(t1)
//                print("child length: " + ifr.contentWindow.document.body.childNodes.length)
//                print ("data reset to: " + JSON.stringify(ifr.contentWindow.document.body.childNodes[0].innerHTML))
                offset = 0;
            }
            ifr.contentWindow.document.body.childNodes[0].removeChild(dummyTextNode)
        }
        
    }
    var connect = function() {
        ifr = document.createElement("iframe")
        ifr.src = src
//        ifr.setAttribute("id","tehifr")
        ifr.style.width = 600
        ifr.style.height= 400
        document.body.appendChild(ifr)
        setInterval(poll, 200)
    }
    var reconnect = function() {
        // TODO: reuse this xhr connection
//        xhr = null;
//        offset = 0
//        setTimeout(connect, retry)
    }

    var buffer_check = function() {
        
    }

    var process = function() {
//        print("process")
        // FIXME: add a var here
        stream = ifr.contentWindow.document.body.childNodes[0].innerText
        stream2 = repr(stream)
        if (stream.length < offset) { // in safari the offset starts at 256 
//            print ("no.")
            return 
        }
        var next_boundary = stream.indexOf(boundary, offset);
        var line = null;
        if (next_boundary == -1)
            return
        line = stream.slice(offset, next_boundary)
        offset = next_boundary + boundary.length
        if (line.length == 0) {
            dispatch()
        }
        else {
            lineQueue.push(line) // TODO: is this cross-browser?                
        }
        // TODO: use a while loop here. We don't want a stack overflow
        process() // Keep going until we run out of new lines
    }

    var dispatch = function() {
        var data = "";
        var name = "message";
        lineQueue.reverse() // So we can use pop which removes elements from the end
        while (lineQueue.length > 0) {
            line = lineQueue.pop()
            var field = null;
            var value = "";
            var j = line.indexOf(':')
            if (j == -1) {
                field = line
                value = ""
            }
            else if (j == 0) {
                continue // This line must be a comment
            }
            else {
                field = line.slice(0, j)
                value = line.slice(j+1)
            }
            if (field == "event")
                name = value
            if (field == "id") {
                id = value
//                source.lastEventId = id;
            }
            if (field == "retry") {
                value = parseInt(value)
                if (!isNaN(value))
                    retry = value
            }
            if (field == "data") {
                if (data.length > 0)
                    data += "\n"
                data += value
            }
        }
        var e = document.createEvent("Events")
        if (data.length > 0 || (name != "message" && name.length > 0)) {
            e.initEvent(name, true, true)
            e.lastEventId = id
            e.data = data
            e.origin = document.domain
            e.source = null
            source.dispatchEvent(e);
        }
    }
}
/*jslint evil: true */
/*extern JSON */

if (!this.JSON) {

    JSON = function () {

        function f(n) {    // Format integers to have at least two digits.
            return n < 10 ? '0' + n : n;
        }

        Date.prototype.toJSON = function () {

// Eventually, this method will be based on the date.toISOString method.

            return this.getUTCFullYear()   + '-' +
                 f(this.getUTCMonth() + 1) + '-' +
                 f(this.getUTCDate())      + 'T' +
                 f(this.getUTCHours())     + ':' +
                 f(this.getUTCMinutes())   + ':' +
                 f(this.getUTCSeconds())   + 'Z';
        };


        var m = {    // table of character substitutions
            '\b': '\\b',
            '\t': '\\t',
            '\n': '\\n',
            '\f': '\\f',
            '\r': '\\r',
            '"' : '\\"',
            '\\': '\\\\'
        };

        function stringify(value, whitelist) {
            var a,          // The array holding the partial texts.
                i,          // The loop counter.
                k,          // The member key.
                l,          // Length.
                r = /["\\\x00-\x1f\x7f-\x9f]/g,
                v;          // The member value.

            switch (typeof value) {
            case 'string':

// If the string contains no control characters, no quote characters, and no
// backslash characters, then we can safely slap some quotes around it.
// Otherwise we must also replace the offending characters with safe sequences.

                return r.test(value) ?
                    '"' + value.replace(r, function (a) {
                        var c = m[a];
                        if (c) {
                            return c;
                        }
                        c = a.charCodeAt();
                        return '\\u00' + Math.floor(c / 16).toString(16) +
                                                   (c % 16).toString(16);
                    }) + '"' :
                    '"' + value + '"';

            case 'number':

// JSON numbers must be finite. Encode non-finite numbers as null.

                return isFinite(value) ? String(value) : 'null';

            case 'boolean':
            case 'null':
                return String(value);

            case 'object':

// Due to a specification blunder in ECMAScript,
// typeof null is 'object', so watch out for that case.

                if (!value) {
                    return 'null';
                }

// If the object has a toJSON method, call it, and stringify the result.

                if (typeof value.toJSON === 'function') {
                    return stringify(value.toJSON());
                }
                a = [];
                if (typeof value.length === 'number' &&
                        !(value.propertyIsEnumerable('length'))) {

// The object is an array. Stringify every element. Use null as a placeholder
// for non-JSON values.

                    l = value.length;
                    for (i = 0; i < l; i += 1) {
                        a.push(stringify(value[i], whitelist) || 'null');
                    }

// Join all of the elements together and wrap them in brackets.

                    return '[' + a.join(',') + ']';
                }
                if (whitelist) {

// If a whitelist (array of keys) is provided, use it to select the components
// of the object.

                    l = whitelist.length;
                    for (i = 0; i < l; i += 1) {
                        k = whitelist[i];
                        if (typeof k === 'string') {
                            v = stringify(value[k], whitelist);
                            if (v) {
                                a.push(stringify(k) + ':' + v);
                            }
                        }
                    }
                } else {

// Otherwise, iterate through all of the keys in the object.

                    for (k in value) {
                        if (typeof k === 'string') {
                            v = stringify(value[k], whitelist);
                            if (v) {
                                a.push(stringify(k) + ':' + v);
                            }
                        }
                    }
                }

// Join all of the member texts together and wrap them in braces.

                return '{' + a.join(',') + '}';
            }
        }

        return {
            stringify: stringify,
            parse: function (text, filter) {
                var j;

                function walk(k, v) {
                    var i, n;
                    if (v && typeof v === 'object') {
                        for (i in v) {
                            if (Object.prototype.hasOwnProperty.apply(v, [i])) {
                                n = walk(i, v[i]);
                                if (n !== undefined) {
                                    v[i] = n;
                                }
                            }
                        }
                    }
                    return filter(k, v);
                }


// Parsing happens in three stages. In the first stage, we run the text against
// regular expressions that look for non-JSON patterns. We are especially
// concerned with '()' and 'new' because they can cause invocation, and '='
// because it can cause mutation. But just to be safe, we want to reject all
// unexpected forms.

// We split the first stage into 4 regexp operations in order to work around
// crippling inefficiencies in IE's and Safari's regexp engines. First we
// replace all backslash pairs with '@' (a non-JSON character). Second, we
// replace all simple value tokens with ']' characters. Third, we delete all
// open brackets that follow a colon or comma or that begin the text. Finally,
// we look to see that the remaining characters are only whitespace or ']' or
// ',' or ':' or '{' or '}'. If that is so, then the text is safe for eval.

                if (/^[\],:{}\s]*$/.test(text.replace(/\\./g, '@').
replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(:?[eE][+\-]?\d+)?/g, ']').
replace(/(?:^|:|,)(?:\s*\[)+/g, ''))) {

// In the second stage we use the eval function to compile the text into a
// JavaScript structure. The '{' operator is subject to a syntactic ambiguity
// in JavaScript: it can begin a block or an object literal. We wrap the text
// in parens to eliminate the ambiguity.

                    j = eval('(' + text + ')');

// In the optional third stage, we recursively walk the new structure, passing
// each name/value pair to a filter function for possible transformation.

                    return typeof filter === 'function' ? walk('', j) : j;
                }

// If the text is not JSON parseable, then a SyntaxError is thrown.

                throw new SyntaxError('parseJSON');
            }
        };
    }();
}



var base2={name:"base2",version:"1.0 (beta 2)",exports:"Base,Package,Abstract,Module,Enumerable,Map,Collection,RegGrp,"+"assert,assertArity,assertType,assignID,copy,detect,extend,"+"forEach,format,global,instanceOf,match,rescape,slice,trim,typeOf,"+"I,K,Undefined,Null,True,False,bind,delegate,flip,not,unbind",global:this,detect:new function(_){var global=_;var jscript=NaN/*@cc_on||@_jscript_version@*/;var java=_.java?true:false;if(_.navigator){var MSIE=/MSIE[\d.]+/g;var element=document.createElement("span");var userAgent=navigator.userAgent.replace(/([a-z])[\s\/](\d)/gi,"$1$2");if(!jscript)userAgent=userAgent.replace(MSIE,"");
if(MSIE.test(userAgent))userAgent=userAgent.match(MSIE)[0]+" "+userAgent.replace(MSIE,"");userAgent=navigator.platform+" "+userAgent;java&=navigator.javaEnabled()}return function(a){var r=false;var b=a.charAt(0)=="!";if(b)a=a.slice(1);if(a.charAt(0)=="("){try{eval("r=!!"+a)}catch(e){}}else{r=new RegExp("("+a+")","i").test(userAgent)}return!!(b^r)}}(this)};new function(_){var _0="function base(o,a){return o.base.apply(o,a)};";eval(_0);var detect=base2.detect;var Undefined=K(),Null=K(null),True=K(true),False=K(false);var _1=/%([1-9])/g;var _2=/^\s\s*/;var _3=/\s\s*$/;var _4=/([\/()[\]{}|*+-.,^$?\\])/g;var _5=/eval/.test(detect)?/\bbase\s*\(/:/.*/;var _6=["constructor","toString","valueOf"];var _7=detect("(jscript)")?new RegExp("^"+rescape(isNaN).replace(/isNaN/,"\\w+")+"$"):{test:False};var _8=1;var _9=Array.prototype.slice;var slice=Array.slice||function(a){return _9.apply(a,_9.call(arguments,1))};_10();var _11=function(a,b){base2.__prototyping=this.prototype;var c=new this;extend(c,a);delete base2.__prototyping;var d=c.constructor;function e(){if(!base2.__prototyping){if(this.constructor==arguments.callee||this.__constructing){this.__constructing=true;d.apply(this,arguments);delete this.__constructing}else{return extend(arguments[0],c)}}return this};c.constructor=e;for(var i in Base)e[i]=this[i];e.ancestor=this;e.base=Undefined;e.init=Undefined;extend(e,b);e.prototype=c;e.init();return e};var Base=_11.call(Object,{constructor:function(){if(arguments.length>0){this.extend(arguments[0])}},base:function(){},extend:delegate(extend)},Base={ancestorOf:delegate(_12),extend:_11,forEach:delegate(_10),implement:function(a){if(typeof a=="function"){if(_12(Base,a)){a(this.prototype)}}else{extend(this.prototype,a)}return this}});var Package=Base.extend({constructor:function(d,e){this.extend(e);if(this.init)this.init();if(this.name!="base2"){if(!this.parent)this.parent=base2;this.parent.addName(this.name,this);this.namespace=format("var %1=%2;",this.name,String(this).slice(1,-1))}var f=/[^\s,]+/g;if(d){d.imports=Array2.reduce(this.imports.match(f),function(a,b){eval("var ns=base2."+b);assert(ns,format("Package not found: '%1'.",b),ReferenceError);return a+=ns.namespace},_0+base2.namespace+JavaScript.namespace);d.exports=Array2.reduce(this.exports.match(f),function(a,b){var c=this.name+"."+b;this.namespace+="var "+b+"="+c+";";return a+="if(!"+c+")"+c+"="+b+";"},"",this)}},exports:"",imports:"",name:"",namespace:"",parent:null,addName:function(a,b){if(!this[a]){this[a]=b;this.exports+=","+a;this.namespace+=format("var %1=%2.%1;",a,this.name)}},addPackage:function(a){this.addName(a,new Package(null,{name:a,parent:this}))},toString:function(){return format("[%1]",this.parent?String(this.parent).slice(1,-1)+"."+this.name:this.name)}});var Abstract=Base.extend({constructor:function(){throw new TypeError("Class cannot be instantiated.");}});var Module=Abstract.extend(null,{extend:function(a,b){var c=this.base();c.implement(this);c.implement(a);extend(c,b);c.init();return c},implement:function(d){var e=this;if(typeof d=="function"){if(!_12(d,e)){this.base(d)}if(_12(Module,d)){forEach(d,function(a,b){if(!e[b]){if(typeof a=="function"&&a.call&&d.prototype[b]){a=function(){return d[b].apply(d,arguments)}}e[b]=a}})}}else{extend(e,d);_10(Object,d,function(b,c){if(c.charAt(0)=="@"){if(detect(c.slice(1))){forEach(b,arguments.callee)}}else if(typeof b=="function"&&b.call){e.prototype[c]=function(){var a=_9.call(arguments);a.unshift(this);return e[c].apply(e,a)}}})}return e}});var Enumerable=Module.extend({every:function(c,d,e){var f=true;try{this.forEach(c,function(a,b){f=d.call(e,a,b,c);if(!f)throw StopIteration;})}catch(error){if(error!=StopIteration)throw error;}return!!f},filter:function(d,e,f){var i=0;return this.reduce(d,function(a,b,c){if(e.call(f,b,c,d)){a[i++]=b}return a},[])},invoke:function(b,c){var d=_9.call(arguments,2);return this.map(b,(typeof c=="function")?function(a){return(a==null)?undefined:c.apply(a,d)}:function(a){return(a==null)?undefined:a[c].apply(a,d)})},map:function(c,d,e){var f=[],i=0;this.forEach(c,function(a,b){f[i++]=d.call(e,a,b,c)});return f},pluck:function(b,c){return this.map(b,function(a){return(a==null)?undefined:a[c]})},reduce:function(c,d,e,f){var g=arguments.length>2;this.forEach(c,function(a,b){if(g){e=d.call(f,e,a,b,c)}else{e=a;g=true}});return e},some:function(a,b,c){return!this.every(a,not(b),c)}},{forEach:forEach});var _13="#";var Map=Base.extend({constructor:function(a){this.merge(a)},copy:delegate(copy),forEach:function(a,b){for(var c in this)if(c.charAt(0)==_13){a.call(b,this[c],c.slice(1),this)}},get:function(a){return this[_13+a]},getKeys:function(){return this.map(flip(I))},getValues:function(){return this.map(I)},has:function(a){/*@cc_on@*//*@if(@_14<5.5)return $Legacy.has(this,_13+a);@else@*/return _13+a in this;/*@end@*/},merge:function(b){var c=flip(this.put);forEach(arguments,function(a){forEach(a,c,this)},this);return this},remove:function(a){delete this[_13+a]},put:function(a,b){if(arguments.length==1)b=a;this[_13+a]=b},size:function(){var a=0;for(var b in this)if(b.charAt(0)==_13)a++;return a},union:function(a){return this.merge.apply(this.copy(),arguments)}});Map.implement(Enumerable);var _15="~";var Collection=Map.extend({constructor:function(a){this[_15]=new Array2;this.base(a)},add:function(a,b){assert(!this.has(a),"Duplicate key '"+a+"'.");this.put.apply(this,arguments)},copy:function(){var a=this.base();a[_15]=this[_15].copy();return a},forEach:function(a,b){var c=this[_15];var d=c.length;for(var i=0;i<d;i++){a.call(b,this[_13+c[i]],c[i],this)}},getAt:function(a){if(a<0)a+=this[_15].length;var b=this[_15][a];return(b===undefined)?undefined:this[_13+b]},getKeys:function(){return this[_15].concat()},indexOf:function(a){return this[_15].indexOf(String(a))},insertAt:function(a,b,c){assert(Math.abs(a)<this[_15].length,"Index out of bounds.");assert(!this.has(b),"Duplicate key '"+b+"'.");this[_15].insertAt(a,String(b));this[_13+b]==null;this.put.apply(this,_9.call(arguments,1))},item:function(a){return this[typeof a=="number"?"getAt":"get"](a)},put:function(a,b){if(arguments.length==1)b=a;if(!this.has(a)){this[_15].push(String(a))}var c=this.constructor;if(c.Item&&!instanceOf(b,c.Item)){b=c.create.apply(c,arguments)}this[_13+a]=b},putAt:function(a,b){assert(Math.abs(a)<this[_15].length,"Index out of bounds.");arguments[0]=this[_15].item(a);this.put.apply(this,arguments)},remove:function(a){if(this.has(a)){this[_15].remove(String(a));delete this[_13+a]}},removeAt:function(a){var b=this[_15].removeAt(a);delete this[_13+b]},reverse:function(){this[_15].reverse();return this},size:function(){return this[_15].length},sort:function(c){if(c){var d=this;this[_15].sort(function(a,b){return c(d[_13+a],d[_13+b],a,b)})}else this[_15].sort();return this},toString:function(){return String(this[_15])}},{Item:null,create:function(a,b){return this.Item?new this.Item(a,b):b},extend:function(a,b){var c=this.base(a);c.create=this.create;extend(c,b);if(!c.Item){c.Item=this.Item}else if(typeof c.Item!="function"){c.Item=(this.Item||Base).extend(c.Item)}c.init();return c}});var _16=/\\(\d+)/g,_17=/\\./g,_18=/\(\?[:=!]|\[[^\]]+\]/g,_19=/\(/g,_20=/\$(\d+)/,_21=/^\$\d+$/;var RegGrp=Collection.extend({constructor:function(a,b){this.base(a);if(typeof b=="string"){this.global=/g/.test(b);this.ignoreCase=/i/.test(b)}},global:true,ignoreCase:false,exec:function(f,g){var h=(this.global?"g":"")+(this.ignoreCase?"i":"");f=String(f)+"";if(arguments.length==1){var j=this;var k=this[_15];g=function(a){if(a){var b,c=1,i=0;while((b=j[_13+k[i++]])){var d=c+b.length+1;if(arguments[c]){var e=b.replacement;switch(typeof e){case"function":return e.apply(j,_9.call(arguments,c,d));case"number":return arguments[c+e];default:return e}}c=d}}return""}}return f.replace(new RegExp(this,h),g)},insertAt:function(a,b,c){if(instanceOf(b,RegExp)){arguments[1]=b.source}return base(this,arguments)},test:function(a){return this.exec(a)!=a},toString:function(){var e=0;return"("+this.map(function(c){var d=String(c).replace(_16,function(a,b){return"\\"+(1+Number(b)+e)});e+=c.length+1;return d}).join(")|(")+")"}},{IGNORE:"$0",init:function(){forEach("add,get,has,put,remove".split(","),function(b){_22(this,b,function(a){if(instanceOf(a,RegExp)){arguments[0]=a.source}return base(this,arguments)})},this.prototype)},Item:{constructor:function(a,b){if(typeof b=="number")b=String(b);else if(b==null)b="";if(typeof b=="string"&&_20.test(b)){if(_21.test(b)){b=parseInt(b.slice(1))}else{var Q=/'/.test(b.replace(/\\./g,""))?'"':"'";b=b.replace(/\n/g,"\\n").replace(/\r/g,"\\r").replace(/\$(\d+)/g,Q+"+(arguments[$1]||"+Q+Q+")+"+Q);b=new Function("return "+Q+b.replace(/(['"])\1\+(.*)\+\1\1$/,"$1")+Q)}}this.length=RegGrp.count(a);this.replacement=b;this.toString=K(String(a))},length:0,replacement:""},count:function(a){a=String(a).replace(_17,"").replace(_18,"");return match(a,_19).length}});var JavaScript={name:"JavaScript",version:base2.version,exports:"Array2,Date2,String2",namespace:"",bind:function(c){forEach(this.exports.match(/\w+/g),function(a){var b=a.slice(0,-1);extend(c[b],this[a]);this[a](c[b].prototype)},this);return this}};if((new Date).getYear()>1900){Date.prototype.getYear=function(){return this.getFullYear()-1900};Date.prototype.setYear=function(a){return this.setFullYear(a+1900)}}Function.prototype.prototype={};if("".replace(/^/,K("$$"))=="$"){extend(String.prototype,"replace",function(a,b){if(typeof b=="function"){var c=b;b=function(){return String(c.apply(null,arguments)).split("$").join("$$")}}return this.base(a,b)})}var Array2=_23(Array,Array,"concat,join,pop,push,reverse,shift,slice,sort,splice,unshift",[Enumerable,{combine:function(d,e){if(!e)e=d;return this.reduce(d,function(a,b,c){a[b]=e[c];return a},{})},contains:function(a,b){return this.indexOf(a,b)!=-1},copy:function(a){var b=_9.call(a);if(!b.swap)this(b);return b},flatten:function(c){var d=0;return this.reduce(c,function(a,b){if(this.like(b)){this.reduce(b,arguments.callee,a,this)}else{a[d++]=b}return a},[],this)},forEach:_24,indexOf:function(a,b,c){var d=a.length;if(c==null){c=0}else if(c<0){c=Math.max(0,d+c)}for(var i=c;i<d;i++){if(a[i]===b)return i}return-1},insertAt:function(a,b,c){this.splice(a,b,0,c);return c},item:function(a,b){if(b<0)b+=a.length;return a[b]},lastIndexOf:function(a,b,c){var d=a.length;if(c==null){c=d-1}else if(c<0){c=Math.max(0,d+c)}for(var i=c;i>=0;i--){if(a[i]===b)return i}return-1},map:function(c,d,e){var f=[];this.forEach(c,function(a,b){f[b]=d.call(e,a,b,c)});return f},remove:function(a,b){var c=this.indexOf(a,b);if(c!=-1)this.removeAt(a,c);return b},removeAt:function(a,b){return this.splice(a,b,1)},swap:function(a,b,c){if(b<0)b+=a.length;if(c<0)c+=a.length;var d=a[b];a[b]=a[c];a[c]=d;return a}}]);Array2.reduce=Enumerable.reduce;Array2.like=function(a){return!!(a&&typeof a=="object"&&typeof a.length=="number")};var _25=/^((-\d+|\d{4,})(-(\d{2})(-(\d{2}))?)?)?T((\d{2})(:(\d{2})(:(\d{2})(\.(\d{1,3})(\d)?\d*)?)?)?)?(([+-])(\d{2})(:(\d{2}))?|Z)?$/;var _26={FullYear:2,Month:4,Date:6,Hours:8,Minutes:10,Seconds:12,Milliseconds:14};var _27={Hectomicroseconds:15,UTC:16,Sign:17,Hours:18,Minutes:20};var _28=/(((00)?:0+)?:0+)?\.0+$/;var _29=/(T[0-9:.]+)$/;var Date2=_23(Date,function(a,b,c,h,m,s,d){switch(arguments.length){case 0:return new Date;case 1:return new Date(a);default:return new Date(a,b,arguments.length==2?1:c,h||0,m||0,s||0,d||0)}},"",[{toISOString:function(c){var d="####-##-##T##:##:##.###";for(var e in _26){d=d.replace(/#+/,function(a){var b=c["getUTC"+e]();if(e=="Month")b++;return("000"+b).slice(-a.length)})}return d.replace(_28,"").replace(_29,"$1Z")}}]);Date2.now=function(){return(new Date).valueOf()};Date2.parse=function(a,b){if(arguments.length>1){assertType(b,"number","defaultDate should be of type 'number'.")}var c=String(a).match(_25);if(c){if(c[_26.Month])c[_26.Month]--;if(c[_27.Hectomicroseconds]>=5)c[_26.Milliseconds]++;var d=new Date(b||0);var e=c[_27.UTC]||c[_27.Hours]?"UTC":"";for(var f in _26){var g=c[_26[f]];if(!g)continue;d["set"+e+f](g);if(d["get"+e+f]()!=c[_26[f]]){return NaN}}if(c[_27.Hours]){var h=Number(c[_27.Sign]+c[_27.Hours]);var i=Number(c[_27.Sign]+(c[_27.Minutes]||0));d.setUTCMinutes(d.getUTCMinutes()+(h*60)+i)}return d.valueOf()}else{return Date.parse(a)}};var String2=_23(String,function(a){return new String(arguments.length==0?"":a)},"charAt,charCodeAt,concat,indexOf,lastIndexOf,match,replace,search,slice,split,substr,substring,toLowerCase,toUpperCase",[{trim:trim}]);function _23(c,constructor,d,e){var f=Module.extend();forEach(d.match(/\w+/g),function(a){f[a]=unbind(c.prototype[a])});forEach(e,f.implement,f);var g=function(){return f(this.constructor==f?constructor.apply(null,arguments):arguments[0])};g.prototype=f.prototype;forEach(f,function(a,b){if(c[b]){f[b]=c[b];delete f.prototype[b]}g[b]=f[b]});g.ancestor=Object;delete g.extend;if(c!=Array)delete g.forEach;return g};function extend(a,b){if(a&&b){if(arguments.length>2){var c=b;b={};b[c]=arguments[2]}var d=(typeof b=="function"?Function:Object).prototype;var i=_6.length,c;if(base2.__prototyping){while(c=_6[--i]){var e=b[c];if(e!=d[c]){if(_5.test(e)){_22(a,c,e)}else{a[c]=e}}}}for(c in b){if(d[c]===undefined){var e=b[c];if(c.charAt(0)=="@"){if(detect(c.slice(1)))arguments.callee(a,e);continue}var f=a[c];if(f&&typeof e=="function"){if(e!=f&&(!f.method||!_12(e,f))){if(_5.test(e)){_22(a,c,e)}else{e.ancestor=f;a[c]=e}}}else{a[c]=e}}}}return a};function _12(a,b){while(b){if(!b.ancestor)return false;b=b.ancestor;if(b==a)return true}return false};function _22(c,d,e){var f=c[d];var g=base2.__prototyping;if(g&&f!=g[d])g=null;function h(){var a=this.base;this.base=g?g[d]:f;var b=e.apply(this,arguments);this.base=a;return b};h.ancestor=f;c[d]=h};if(typeof StopIteration=="undefined"){StopIteration=new Error("StopIteration")}function forEach(a,b,c,d){if(a==null)return;if(!d){if(typeof a=="function"&&a.call){d=Function}else if(typeof a.forEach=="function"&&a.forEach!=arguments.callee){a.forEach(b,c);return}else if(typeof a.length=="number"){_24(a,b,c);return}}_10(d||Object,a,b,c)};function _24(a,b,c){if(a==null)return;var d=a.length,i;if(typeof a=="string"){for(i=0;i<d;i++){b.call(c,a.charAt(i),i,a)}}else{for(i=0;i<d;i++){/*@cc_on@*//*@if(@_14<5.2)if($Legacy.has(a,i))@else@*/if(i in a)/*@end@*/b.call(c,a[i],i,a)}}};function _10(g,h,j,k){var l=function(){this.i=1};l.prototype={i:1};var m=0;for(var i in new l)m++;_10=(m>1)?function(a,b,c,d){var e={};for(var f in b){if(!e[f]&&a.prototype[f]===undefined){e[f]=true;c.call(d,b[f],f,b)}}}:function(a,b,c,d){for(var e in b){if(a.prototype[e]===undefined){c.call(d,b[e],e,b)}}};_10(g,h,j,k)};function typeOf(a){var b=typeof a;switch(b){case"object":return a===null?"null":typeof a.call=="function"||_7.test(a)?"function":b;case"function":return typeof a.call=="function"?b:"object";default:return b}};function instanceOf(a,b){if(typeof b!="function"){throw new TypeError("Invalid 'instanceOf' operand.");}if(a==null)return false;/*@cc_on if(typeof a.constructor!="function"){return typeOf(a)==typeof b.prototype.valueOf()}@*//*@if(@_14<5.1)if($Legacy.instanceOf(a,b))return true;@else@*/if(a instanceof b)return true;/*@end@*/if(Base.ancestorOf==b.ancestorOf)return false;if(Base.ancestorOf==a.constructor.ancestorOf)return b==Object;switch(b){case Array:return!!(typeof a=="object"&&a.join&&a.splice);case Function:return typeOf(a)=="function";case RegExp:return typeof a.constructor.$1=="string";case Date:return!!a.getTimezoneOffset;case String:case Number:case Boolean:return typeof a==typeof b.prototype.valueOf();case Object:return true}return false};function assert(a,b,c){if(!a){throw new(c||Error)(b||"Assertion failed.");}};function assertArity(a,b,c){if(b==null)b=a.callee.length;if(a.length<b){throw new SyntaxError(c||"Not enough arguments.");}};function assertType(a,b,c){if(b&&(typeof b=="function"?!instanceOf(a,b):typeOf(a)!=b)){throw new TypeError(c||"Invalid type.");}};function assignID(a){if(!a.base2ID)a.base2ID="b2_"+_8++;return a.base2ID};function copy(a){var b=function(){};b.prototype=a;return new b};function format(c){var d=arguments;var e=new RegExp("%([1-"+arguments.length+"])","g");return String(c).replace(e,function(a,b){return d[b]})};function match(a,b){return String(a).match(b)||[]};function rescape(a){return String(a).replace(_4,"\\$1")};function trim(a){return String(a).replace(_2,"").replace(_3,"")};function I(i){return i};function K(k){return function(){return k}};function bind(a,b){var c=_9.call(arguments,2);return c.length==0?function(){return a.apply(b,arguments)}:function(){return a.apply(b,c.concat.apply(c,arguments))}};function delegate(b,c){return function(){var a=_9.call(arguments);a.unshift(this);return b.apply(c,a)}};function flip(a){return function(){return a.apply(this,Array2.swap(arguments,0,1))}};function not(a){return function(){return!a.apply(this,arguments)}};function unbind(b){return function(a){return b.apply(a,_9.call(arguments,1))}};base2=new Package(this,base2);eval(this.exports);base2.extend=extend;forEach(Enumerable,function(a,b){if(!Module[b])base2.addName(b,bind(a,Enumerable))});JavaScript=new Package(this,JavaScript);eval(this.exports)};new function(_){var DOM=new base2.Package(this,{name:"DOM",version:"1.0 (beta 2)",exports:"Interface,Binding,Node,Document,Element,AbstractView,HTMLDocument,HTMLElement,"+"Selector,Traversal,XPathParser,NodeSelector,DocumentSelector,ElementSelector,"+"StaticNodeList,Event,EventTarget,DocumentEvent,ViewCSS,CSSStyleDeclaration",bind:function(a){if(a&&a.nodeType){var b=assignID(a);if(!DOM.bind[b]){switch(a.nodeType){case 1:if(typeof a.className=="string"){(HTMLElement.bindings[a.tagName]||HTMLElement).bind(a)}else{Element.bind(a)}break;case 9:if(a.writeln){HTMLDocument.bind(a)}else{Document.bind(a)}break;default:Node.bind(a)}DOM.bind[b]=true}}return a},"@MSIE5.+win":{bind:function(a){if(a&&a.writeln){a.nodeType=9}return this.base(a)}}});eval(this.imports);var _30=detect("MSIE");var _31=detect("MSIE5");var Interface=Module.extend(null,{implement:function(e){var f=this;if(Interface.ancestorOf(e)){forEach(e,function(a,b){if(e[b]._32){f[b]=function(){return e[b].apply(e,arguments)}}})}else if(typeof e=="object"){this.forEach(e,function(a,b){if(b.charAt(0)=="@"){forEach(a,arguments.callee)}else if(typeof a=="function"&&a.call){if(!f[b]){var c="var fn=function _%1(%2){%3.base=%3.%1.ancestor;var m=%3.base?'base':'%1';return %3[m](%4)}";var d="abcdefghij".split("").slice(-a.length);eval(format(c,b,d,d[0],d.slice(1)));fn._32=b;f[b]=fn}}})}return this.base(e)}});var Binding=Interface.extend(null,{bind:function(a){return extend(a,this.prototype)}});var Node=Binding.extend({"@!(element.compareDocumentPosition)":{compareDocumentPosition:function(a,b){if(Traversal.contains(a,b)){return 4|16}else if(Traversal.contains(b,a)){return 2|8}var c=_33(a);var d=_33(b);if(c<d){return 4}else if(c>d){return 2}return 0}}});var _33=document.documentElement.sourceIndex?function(a){return a.sourceIndex}:function(a){var b=0;while(a){b=Traversal.getNodeIndex(a)+"."+b;a=a.parentNode}return b};var Document=Node.extend(null,{bind:function(b){extend(b,"createElement",function(a){return DOM.bind(this.base(a))});AbstractView.bind(b.defaultView);if(b!=window.document)new DOMContentLoadedEvent(b);return this.base(b)},"@!(document.defaultView)":{bind:function(a){a.defaultView=Traversal.getDefaultView(a);return this.base(a)}}});var _34=/^(href|src)$/;var _35={"class":"className","for":"htmlFor"};var Element=Node.extend({"@MSIE.+win":{getAttribute:function(a,b,c){if(a.className===undefined){return this.base(a,b)}var d=_36(a,b);if(d&&(d.specified||b=="value")){if(_34.test(b)){return this.base(a,b,2)}else if(b=="style"){return a.style.cssText}else{return d.nodeValue}}return null},setAttribute:function(a,b,c){if(a.className===undefined){this.base(a,b,c)}else if(b=="style"){a.style.cssText=c}else{c=String(c);var d=_36(a,b);if(d){d.nodeValue=c}else{this.base(a,_35[b]||b,c)}}}},"@!(element.hasAttribute)":{hasAttribute:function(a,b){return this.getAttribute(a,b)!=null}}});extend(Element.prototype,"cloneNode",function(a){var b=this.base(a||false);b.base2ID=undefined;return b});if(_30){var _37="colSpan,rowSpan,vAlign,dateTime,accessKey,tabIndex,encType,maxLength,readOnly,longDesc";extend(_35,Array2.combine(_37.toLowerCase().split(","),_37.split(",")));var _36=_31?function(a,b){return a.attributes[b]||a.attributes[_35[b.toLowerCase()]]}:function(a,b){return a.getAttributeNode(b)}}var TEXT=_30?"innerText":"textContent";var Traversal=Module.extend({getDefaultView:function(a){return this.getDocument(a).defaultView},getNextElementSibling:function(a){while(a&&(a=a.nextSibling)&&!this.isElement(a))continue;return a},getNodeIndex:function(a){var b=0;while(a&&(a=a.previousSibling))b++;return b},getOwnerDocument:function(a){return a.ownerDocument},getPreviousElementSibling:function(a){while(a&&(a=a.previousSibling)&&!this.isElement(a))continue;return a},getTextContent:function(a){return a[TEXT]},isEmpty:function(a){a=a.firstChild;while(a){if(a.nodeType==3||this.isElement(a))return false;a=a.nextSibling}return true},setTextContent:function(a,b){return a[TEXT]=b},"@MSIE":{getDefaultView:function(a){return(a.document||a).parentWindow},"@MSIE5":{getOwnerDocument:function(a){return a.ownerDocument||a.document}}}},{contains:function(a,b){while(b&&(b=b.parentNode)&&a!=b)continue;return!!b},getDocument:function(a){return this.isDocument(a)?a:this.getOwnerDocument(a)},isDocument:function(a){return!!(a&&a.documentElement)},isElement:function(a){return!!(a&&a.nodeType==1)},"@(element.contains)":{contains:function(a,b){return a!=b&&(this.isDocument(a)?a==this.getOwnerDocument(b):a.contains(b))}},"@MSIE5":{isElement:function(a){return!!(a&&a.nodeType==1&&a.nodeName!="!")}}});var AbstractView=Binding.extend();var Event=Binding.extend({"@!(document.createEvent)":{initEvent:function(a,b,c,d){a.type=b;a.bubbles=c;a.cancelable=d;a.timeStamp=new Date().valueOf()},"@MSIE":{initEvent:function(a,b,c,d){this.base(a,b,c,d);a.cancelBubble=!a.bubbles},preventDefault:function(a){if(a.cancelable!==false){a.returnValue=false}},stopPropagation:function(a){a.cancelBubble=true}}}},{"@!(document.createEvent)":{"@MSIE":{bind:function(a){if(!a.timeStamp){a.bubbles=!!_38[a.type];a.cancelable=!!_39[a.type];a.timeStamp=new Date().valueOf()}if(!a.target){a.target=a.srcElement}a.relatedTarget=a[(a.type=="mouseout"?"to":"from")+"Element"];return this.base(a)}}}});if(_30){var _38="abort,error,select,change,resize,scroll";var _39="click,mousedown,mouseup,mouseover,mousemove,mouseout,keydown,keyup,submit,reset";_38=Array2.combine((_38+","+_39).split(","));_39=Array2.combine(_39.split(","))}var EventTarget=Interface.extend({"@!(element.addEventListener)":{addEventListener:function(a,b,c,d){var e=assignID(a);var f=assignID(c);var g=_40[e];if(!g)g=_40[e]={};var h=g[b];var i=a["on"+b];if(!h){h=g[b]={};if(i)h[0]=i}h[f]=c;if(i!==undefined){a["on"+b]=_40._41}},dispatchEvent:function(a,b){return _41.call(a,b)},removeEventListener:function(a,b,c,d){var e=_40[a.base2ID];if(e&&e[b]){delete e[b][c.base2ID]}},"@(element.fireEvent)":{dispatchEvent:function(a,b){var c="on"+b.type;b.target=a;if(a[c]===undefined){return this.base(a,b)}else{return a.fireEvent(c,b)}}}}});var _40=new Base({_41:_41,"@MSIE":{_41:function(){var a=this;var b=(a.document||a).parentWindow;if(a.Infinity)a=b;return _41.call(a,b.event)}}});function _41(a){var b=true;var c=_40[this.base2ID];if(c){Event.bind(a);var d=c[a.type];for(var i in d){var listener=d[i];if(listener.handleEvent){var result=listener.handleEvent(a)}else{result=listener.call(this,a)}if(result===false||a.returnValue===false)b=false}}return b};var DocumentEvent=Interface.extend({"@!(document.createEvent)":{createEvent:function(a,b){return Event.bind({})},"@(document.createEventObject)":{createEvent:function(a,b){return Event.bind(a.createEventObject())}}},"@(document.createEvent)":{"@!(document.createEvent('Events'))":{createEvent:function(a,b){return this.base(a,b=="Events"?"UIEvents":b)}}}});var DOMContentLoadedEvent=Base.extend({constructor:function(b){var c=false;this.fire=function(){if(!c){c=true;setTimeout(function(){var a=DocumentEvent.createEvent(b,"Events");Event.initEvent(a,"DOMContentLoaded",false,false);EventTarget.dispatchEvent(b,a)},1)}};EventTarget.addEventListener(b,"DOMContentLoaded",function(){c=true},false);this.listen(b)},listen:function(a){EventTarget.addEventListener(Traversal.getDefaultView(a),"load",this.fire,false)},"@MSIE.+win":{listen:function(a){if(a.readyState!="complete"){var b=this;a.write("<script id=__ready defer src=//:><\/script>");a.all.__ready.onreadystatechange=function(){if(this.readyState=="complete"){this.removeNode();b.fire()}}}}},"@KHTML":{listen:function(a){if(a.readyState!="complete"){var b=this;var c=setInterval(function(){if(/loaded|complete/.test(a.readyState)){clearInterval(c);b.fire()}},100)}}}});new DOMContentLoadedEvent(document);Document.implement(DocumentEvent);Document.implement(EventTarget);Element.implement(EventTarget);var _42=/^\d+(px)?$/i;var _43=/(width|height|top|bottom|left|right|fontSize)$/;var _44=/^(color|backgroundColor)$/;var ViewCSS=Interface.extend({"@!(document.defaultView.getComputedStyle)":{"@MSIE":{getComputedStyle:function(a,b,c){var d=b.currentStyle;var e={};for(var i in d){if(_43.test(i)){e[i]=_45(b,e[i])+"px"}else if(_44.test(i)){e[i]=_46(b,i=="color"?"ForeColor":"BackColor")}else{e[i]=d[i]}}return e}}},getComputedStyle:function(a,b,c){return _47.bind(this.base(a,b,c))}},{toCamelCase:function(c){return c.replace(/\-([a-z])/g,function(a,b){return b.toUpperCase()})}});function _45(a,b){if(_42.test(b))return parseInt(b);var c=a.style.left;var d=a.runtimeStyle.left;a.runtimeStyle.left=a.currentStyle.left;a.style.left=b||0;b=a.style.pixelLeft;a.style.left=c;a.runtimeStyle.left=d;return b};function _46(a,b){var c=a.document.body.createTextRange();c.moveToElementText(a);var d=c.queryCommandValue(b);return format("rgb(%1,%2,%3)",d&0xff,(d&0xff00)>>8,(d&0xff0000)>>16)};var _47=Binding.extend({getPropertyValue:function(a,b){return this.base(a,_48[b]||b)},"@MSIE.+win":{getPropertyValue:function(a,b){return b=="float"?a.styleFloat:a[ViewCSS.toCamelCase(b)]}}});var CSSStyleDeclaration=_47.extend({setProperty:function(a,b,c,d){return this.base(a,_48[b]||b,c,d)},"@MSIE.+win":{setProperty:function(a,b,c,d){if(b=="opacity"){c*=100;a.opacity=c;a.zoom=1;a.filter="Alpha(opacity="+c+")"}else{a.setAttribute(b,c)}}}},{"@MSIE":{bind:function(a){a.getPropertyValue=this.prototype.getPropertyValue;a.setProperty=this.prototype.setProperty;return a}}});var _48=new Base({"@Gecko":{opacity:"-moz-opacity"},"@KHTML":{opacity:"-khtml-opacity"}});with(CSSStyleDeclaration.prototype)getPropertyValue.toString=setProperty.toString=function(){return"[base2]"};AbstractView.implement(ViewCSS);var NodeSelector=Interface.extend({"@!(element.querySelector)":{querySelector:function(a,b){return new Selector(b).exec(a,1)},querySelectorAll:function(a,b){return new Selector(b).exec(a)}}});extend(NodeSelector.prototype,{querySelector:function(a){return DOM.bind(this.base(a))},querySelectorAll:function(b){return extend(this.base(b),"item",function(a){return DOM.bind(this.base(a))})}});var DocumentSelector=NodeSelector.extend();var ElementSelector=NodeSelector.extend({"@!(element.matchesSelector)":{matchesSelector:function(a,b){return new Selector(b).test(a)}}});var StaticNodeList=Base.extend({constructor:function(b){b=b||[];this.length=b.length;this.item=function(a){return b[a]}},length:0,forEach:function(a,b){for(var i=0;i<this.length;i++){a.call(b,this.item(i),i,this)}},item:Undefined,"@(XPathResult)":{constructor:function(b){if(b&&b.snapshotItem){this.length=b.snapshotLength;this.item=function(a){return b.snapshotItem(a)}}else this.base(b)}}});StaticNodeList.implement(Enumerable);var _49=/'(\\.|[^'\\])*'|"(\\.|[^"\\])*"/g,_50=/([\s>+~,]|[^(]\+|^)([#.:\[])/g,_51=/(^|,)([^\s>+~])/g,_52=/\s*([\s>+~(),]|^|$)\s*/g,_53=/\s\*\s/g,_54=/\x01(\d+)/g,_55=/'/g;var CSSParser=RegGrp.extend({constructor:function(a){this.base(a);this.cache={};this.sorter=new RegGrp;this.sorter.add(/:not\([^)]*\)/,RegGrp.IGNORE);this.sorter.add(/([ >](\*|[\w-]+))([^: >+~]*)(:\w+-child(\([^)]+\))?)([^: >+~]*)/,"$1$3$6$4")},cache:null,ignoreCase:true,escape:function(b){var c=this._56=[];return this.optimise(this.format(String(b).replace(_49,function(a){return"\x01"+c.push(a.slice(1,-1).replace(_55,"\\'"))})))},format:function(a){return a.replace(_52,"$1").replace(_51,"$1 $2").replace(_50,"$1*$2")},optimise:function(a){return this.sorter.exec(a.replace(_53,">* "))},parse:function(a){return this.cache[a]||(this.cache[a]=this.unescape(this.exec(this.escape(a))))},unescape:function(c){var d=this._56;return c.replace(_54,function(a,b){return d[b-1]})}});function _57(c,d,e,f,g,h,i,j){f=/last/i.test(c)?f+"+1-":"";if(!isNaN(d))d="0n+"+d;else if(d=="even")d="2n";else if(d=="odd")d="2n+1";d=d.split("n");var a=d[0]?(d[0]=="-")?-1:parseInt(d[0]):1;var b=parseInt(d[1])||0;var k=a<0;if(k){a=-a;if(a==1)b++}var l=format(a==0?"%3%7"+(f+b):"(%4%3-%2)%6%1%70%5%4%3>=%2",a,b,e,f,h,i,j);if(k)l=g+"("+l+")";return l};var XPathParser=CSSParser.extend({constructor:function(){this.base(XPathParser.rules);this.sorter.putAt(1,"$1$4$3$6")},escape:function(a){return this.base(a).replace(/,/g,"\x02")},unescape:function(b){return this.base(b.replace(/\[self::\*\]/g,"").replace(/(^|\x02)\//g,"$1./").replace(/\x02/g," | ")).replace(/'[^'\\]*\\'(\\.|[^'\\])*'/g,function(a){return"concat("+a.split("\\'").join("',\"'\",'")+")"})},"@opera":{unescape:function(a){return this.base(a.replace(/last\(\)/g,"count(preceding-sibling::*)+count(following-sibling::*)+1"))}}},{init:function(){this.values.attributes[""]="[@$1]";forEach(this.types,function(a,b){forEach(this.values[b],a,this.rules)},this)},optimised:{pseudoClasses:{"first-child":"[1]","last-child":"[last()]","only-child":"[last()=1]"}},rules:extend({},{"@!KHTML":{"(^|\\x02) (\\*|[\\w-]+)#([\\w-]+)":"$1id('$3')[self::$2]","([ >])(\\*|[\\w-]+):([\\w-]+-child(\\(([^)]+)\\))?)":function(a,b,c,d,e,f){var g=(b==" ")?"//*":"/*";if(/^nth/i.test(d)){g+=_58(d,f,"position()")}else{g+=XPathParser.optimised.pseudoClasses[d]}return g+"[self::"+c+"]"}}}),types:{identifiers:function(a,b){this[rescape(b)+"([\\w-]+)"]=a},combinators:function(a,b){this[rescape(b)+"(\\*|[\\w-]+)"]=a},attributes:function(a,b){this["\\[([\\w-]+)\\s*"+rescape(b)+"\\s*([^\\]]*)\\]"]=a},pseudoClasses:function(a,b){this[":"+b.replace(/\(\)$/,"\\(([^)]+)\\)")]=a}},values:{identifiers:{"#":"[@id='$1'][1]",".":"[contains(concat(' ',@class,' '),' $1 ')]"},combinators:{" ":"/descendant::$1",">":"/child::$1","+":"/following-sibling::*[1][self::$1]","~":"/following-sibling::$1"},attributes:{"*=":"[contains(@$1,'$2')]","^=":"[starts-with(@$1,'$2')]","$=":"[substring(@$1,string-length(@$1)-string-length('$2')+1)='$2']","~=":"[contains(concat(' ',@$1,' '),' $2 ')]","|=":"[contains(concat('-',@$1,'-'),'-$2-')]","!=":"[not(@$1='$2')]","=":"[@$1='$2']"},pseudoClasses:{"empty":"[not(child::*) and not(text())]","first-child":"[not(preceding-sibling::*)]","last-child":"[not(following-sibling::*)]","not()":_59,"nth-child()":_58,"nth-last-child()":_58,"only-child":"[not(preceding-sibling::*) and not(following-sibling::*)]","root":"[not(parent::*)]"}},"@opera":{init:function(){this.optimised.pseudoClasses["last-child"]=this.values.pseudoClasses["last-child"];this.optimised.pseudoClasses["only-child"]=this.values.pseudoClasses["only-child"];this.base()}}});var _60=new XPathParser;function _59(a,b){return"[not("+_60.exec(trim(b)).replace(/\[1\]/g,"").replace(/^(\*|[\w-]+)/,"[self::$1]").replace(/\]\[/g," and ").slice(1,-1)+")]"};function _58(a,b,c){return"["+_57(a,b,c||"count(preceding-sibling::*)+1","last()","not"," and "," mod ","=")+"]"};var Selector=Base.extend({constructor:function(a){this.toString=K(trim(a))},exec:function(a,b){return Selector.parse(this)(a,b)},test:function(a){var b=new Selector(this+"[b2-test]");a.setAttribute("b2-test",true);var c=b.exec(Traversal.getOwnerDocument(a),true);a.removeAttribute("b2-test");return c==a},toXPath:function(){return Selector.toXPath(this)},"@(XPathResult)":{exec:function(a,b){if(_61.test(this)){return this.base(a,b)}var c=Traversal.getDocument(a);var d=b?9:7;var e=c.evaluate(this.toXPath(),a,null,d,null);return b?e.singleNodeValue:e}},"@MSIE":{exec:function(a,b){if(typeof a.selectNodes!="undefined"&&!_61.test(this)){var c=b?"selectSingleNode":"selectNodes";return a[c](this.toXPath())}return this.base(a,b)}},"@(true)":{exec:function(a,b){try{var c=this.base(a||document,b)}catch(error){throw new SyntaxError(format("'%1' is not a valid CSS selector.",this));}return b?c:new StaticNodeList(c)}}},{toXPath:function(a){if(!_62)_62=new XPathParser;return _62.parse(a)}});var _61=":(checked|disabled|enabled|contains)|^(#[\\w-]+\\s*)?\\w+$";if(detect("KHTML")){if(detect("WebKit5")){_61+="|nth\\-|,"}else{_61="."}}_61=new RegExp(_61);var _63={"=":"%1=='%2'","!=":"%1!='%2'","~=":/(^| )%1( |$)/,"|=":/^%1(-|$)/,"^=":/^%1/,"$=":/%1$/,"*=":/%1/};_63[""]="%1!=null";var _64={"checked":"e%1.checked","contains":"e%1[TEXT].indexOf('%2')!=-1","disabled":"e%1.disabled","empty":"Traversal.isEmpty(e%1)","enabled":"e%1.disabled===false","first-child":"!Traversal.getPreviousElementSibling(e%1)","last-child":"!Traversal.getNextElementSibling(e%1)","only-child":"!Traversal.getPreviousElementSibling(e%1)&&!Traversal.getNextElementSibling(e%1)","root":"e%1==Traversal.getDocument(e%1).documentElement"};var _65=detect("(element.sourceIndex)");var _66="var p%2=0,i%2,e%2,n%2=e%1.";var _67=_65?"e%1.sourceIndex":"assignID(e%1)";var _68="var g="+_67+";if(!p[g]){p[g]=1;";var _69="r[r.length]=e%1;if(s)return e%1;";var _70="var _71=function(e0,s){_72++;var r=[],p={},reg=[%1],"+"d=Traversal.getDocument(e0),c=d.body?'toUpperCase':'toString';";var _62;var _73;var _74;var _75;var _76;var _77;var _78={};var _79=new CSSParser({"^ \\*:root":function(a){_75=false;var b="e%2=d.documentElement;if(Traversal.contains(e%1,e%2)){";return format(b,_74++,_74)}," (\\*|[\\w-]+)#([\\w-]+)":function(a,b,c){_75=false;var d="var e%2=_80(d,'%4');if(e%2&&";if(b!="*")d+="e%2.nodeName=='%3'[c]()&&";d+="Traversal.contains(e%1,e%2)){";if(_76)d+=format("i%1=n%1.length;",_76);return format(d,_74++,_74,b,c)}," (\\*|[\\w-]+)":function(a,b){_77++;_75=b=="*";var c=_66;c+=(_75&&_31)?"all":"getElementsByTagName('%3')";c+=";for(i%2=0;(e%2=n%2[i%2]);i%2++){";return format(c,_74++,_76=_74,b)},">(\\*|[\\w-]+)":function(a,b){var c=_30&&_76;_75=b=="*";var d=_66;d+=c?"children":"childNodes";if(!_75&&c)d+=".tags('%3')";d+=";for(i%2=0;(e%2=n%2[i%2]);i%2++){";if(_75){d+="if(e%2.nodeType==1){";_75=_31}else{if(!c)d+="if(e%2.nodeName=='%3'[c]()){"}return format(d,_74++,_76=_74,b)},"\\+(\\*|[\\w-]+)":function(a,b){var c="";if(_75&&_30)c+="if(e%1.nodeName!='!'){";_75=false;c+="e%1=Traversal.getNextElementSibling(e%1);if(e%1";if(b!="*")c+="&&e%1.nodeName=='%2'[c]()";c+="){";return format(c,_74,b)},"~(\\*|[\\w-]+)":function(a,b){var c="";if(_75&&_30)c+="if(e%1.nodeName!='!'){";_75=false;_77=2;c+="while(e%1=e%1.nextSibling){if(e%1.b2_adjacent==_72)break;if(";if(b=="*"){c+="e%1.nodeType==1";if(_31)c+="&&e%1.nodeName!='!'"}else c+="e%1.nodeName=='%2'[c]()";c+="){e%1.b2_adjacent=_72;";return format(c,_74,b)},"#([\\w-]+)":function(a,b){_75=false;var c="if(e%1.id=='%2'){";if(_76)c+=format("i%1=n%1.length;",_76);return format(c,_74,b)},"\\.([\\w-]+)":function(a,b){_75=false;_73.push(new RegExp("(^|\\s)"+rescape(b)+"(\\s|$)"));return format("if(e%1.className&&reg[%2].test(e%1.className)){",_74,_73.length-1)},":not\\((\\*|[\\w-]+)?([^)]*)\\)":function(a,b,c){var d=(b&&b!="*")?format("if(e%1.nodeName=='%2'[c]()){",_74,b):"";d+=_79.exec(c);return"if(!"+d.slice(2,-1).replace(/\)\{if\(/g,"&&")+"){"},":nth(-last)?-child\\(([^)]+)\\)":function(a,b,c){_75=false;b=format("e%1.parentNode.b2_length",_74);var d="if(p%1!==e%1.parentNode)p%1=_81(e%1.parentNode);";d+="var i=e%1[p%1.b2_lookup];if(p%1.b2_lookup!='b2_index')i++;if(";return format(d,_74)+_57(a,c,"i",b,"!","&&","%","==")+"){"},":([\\w-]+)(\\(([^)]+)\\))?":function(a,b,c,d){return"if("+format(_64[b]||"throw",_74,d||"")+"){"},"\\[([\\w-]+)\\s*([^=]?=)?\\s*([^\\]]*)\\]":function(a,b,c,d){var e=_35[b]||b;if(c){var f="e%1.getAttribute('%2',2)";if(!_34.test(b)){f="e%1.%3||"+f}b=format("("+f+")",_74,b,e)}else{b=format("Element.getAttribute(e%1,'%2')",_74,b)}var g=_63[c||""];if(instanceOf(g,RegExp)){_73.push(new RegExp(format(g.source,rescape(_79.unescape(d)))));g="reg[%2].test(%1)";d=_73.length-1}return"if("+format(g,b,d)+"){"}});new function(_){var _80=_30?function(a,b){var c=a.all[b]||null;if(!c||c.id==b)return c;for(var i=0;i<c.length;i++){if(c[i].id==b)return c[i]}return null}:function(a,b){return a.getElementById(b)};var _72=1;function _81(a){if(a.rows){a.b2_length=a.rows.length;a.b2_lookup="rowIndex"}else if(a.cells){a.b2_length=a.cells.length;a.b2_lookup="cellIndex"}else if(a.b2_indexed!=_72){var b=0;var c=a.firstChild;while(c){if(c.nodeType==1&&c.nodeName!="!"){c.b2_index=++b}c=c.nextSibling}a.b2_length=b;a.b2_lookup="b2_index"}a.b2_indexed=_72;return a};Selector.parse=function(a){if(!_78[a]){_73=[];var b="";var c=_79.escape(a).split(",");for(var i=0;i<c.length;i++){_75=_74=_76=0;_77=c.length>1?2:0;var d=_79.exec(c[i])||"throw;";if(_75&&_30){d+=format("if(e%1.nodeName!='!'){",_74)}var e=(_77>1)?_68:"";d+=format(e+_69,_74);d+=Array(match(d,/\{/g).length+1).join("}");b+=d}eval(format(_70,_73)+_79.unescape(b)+"return s?null:r}");_78[a]=_71}return _78[a]}};Document.implement(DocumentSelector);Element.implement(ElementSelector);var HTMLDocument=Document.extend(null,{"@(document.activeElement===undefined)":{bind:function(b){b.activeElement=null;EventTarget.addEventListener(b,"focus",function(a){b.activeElement=a.target},false);return this.base(b)}}});var HTMLElement=Element.extend({addClass:function(a,b){if(!this.hasClass(a,b)){a.className+=(a.className?" ":"")+b}},hasClass:function(a,b){var c=new RegExp("(^|\\s)"+b+"(\\s|$)");return c.test(a.className)},removeClass:function(a,b){var c=new RegExp("(^|\\s)"+b+"(\\s|$)","g");a.className=trim(a.className.replace(c,"$2"))},toggleClass:function(a,b){if(this.hasClass(a,b)){this.removeClass(a,b)}else{this.addClass(a,b)}}},{bindings:{},tags:"*",bind:function(a){CSSStyleDeclaration.bind(a.style);return this.base(a)},extend:function(){var b=base(this,arguments);var c=(b.tags||"").toUpperCase().split(",");forEach(c,function(a){HTMLElement.bindings[a]=b});return b},"@!(element.ownerDocument)":{bind:function(a){a.ownerDocument=Traversal.getOwnerDocument(a);return this.base(a)}}});HTMLElement.extend(null,{tags:"APPLET,EMBED",bind:I});eval(this.exports)};
