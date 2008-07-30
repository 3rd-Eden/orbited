function() {

if (typeof(Orbited) == "undefined") {
    Orbited = {}
}

/* The URL Constructor takes a sourceUrl argument. If sourceUrl is a defined,
 * non-null value, then the initial attribute values are set via a call to
 * self.populateFromString.
 */
Orbited.URL = function(sourceUrl) {
    var self = this;

    self.protocol = null;
    self.domain = null;
    self.port = null;
    self.path = null;
    self.qs = null;
    self.hash = null;

    /* self.reset will set all the attributes back to null
     */
    self.reset = function() {
        
    }

    /* self.populateFromURL takes a URL instance and adopts any non-null
     * values that it contains. For instance, if url.protocol is "https", then
     * this.protocol should be set to "https". But if url.hostname is null,
     * then this.hostname should not be changed
     */
    self.populateFromURL = function(url) {

    }

    /* self.populateFromString will populate all url related values by extracting
     * the relevant fields from the given url string. This uses the same rules as
     * self.populateFromURL to choose which attributes to overwrite.
     */
    self.populateFromString = function(stringUrl) {

    }

    /* self.extractQsArgs will return a js object with all the key/value
     * combinations present in this.qs. If a key is only present once, then the
     * value should be in the form of a string. If there are multiple occurences
     * of a key, then the value should be in the form of a list.
     */
    self.extractQsArgs = function() {

    }

    /* self.addQsParameter takes a key and a value and concatenates it to
     * this.qs, with the appropriate format
     */
    self.addQsParameter = function(key, value) {
        
    }

    /* self.addQsParameter takes a key and a value and concatenates it to
     * this.qs, with the appropriate format
     */
    self.addQsParameter = function(key, value) {
        
    }

    /* self.removesQsParameter takes a key and removes from this.qs all 
     *key/value pairs that share the given key.
     */
    self.removeQsParameter = function(key) {
        
    }
    /* self.setQsFromObject takes an object, and builds a querystring based on
     * the key/value pairs present on the object. If a value is a list, each
     * element in the list will be set to the qs with the given key. All other
     * object types are converted to a string.
     */
    self.setQsFromObject = function(obj) {

    }

    /* self.render returns a string representation of the url. Note that this
     * must be consistent with self.populateFromString. For instance, if calls
     * to self.reset(); and self.populateFromString("/hello#world") are made,
     * then self.render should return "/hello#world" exactly
     */

    self.render = function() {

    }

    /* self.isSameDomain takes a url object and compares this.domain to
     * url.domain. If they are identical, it returns true, otherwise false.
     */
    self.isSamedomain = function(url) {

    }

    /* self.isChildDomain takes a url object and compares this.domain with
     * url.domain to see if this represents a child domain of url. For instance,
     * both "a.b.c.d" and "b.c.d" are child domains of "c.d". On the other hand
     * "a.b.c" and "d.b.c" do not share this relation
     */
    self.isChildDomain = function(url) {

    }
    /* self.isEqual takes a url object and compares *all* attributes for
     * equality. If everything is the same, it returns true; otherwise false.
     */
    self.isEqual = function(url) {
    
    }
    /* self.extendPath will add the given segment to the path. If the path
     * was previously null, then the path becomes the segment with "/"
     * prepended if it was missing. If the path was non-null, and didn't end
     * with "/", then "/" is put in between the current path and the segment.
     */
    self.extendPath = function(segment) {
    }



}

/* Examples of using the library

target = new URL("/hello")
current = new URL(location.href)
if (target.isSameDomain(current))
    alert('same domain!')
else if (target.isChildDomain(current))
    alert('child domain!')
else
    alert('invalid url')


sessionUrl = new URL("/tcp/ABC")
sessionUrl.addQsParameter('ack', 5)
xhr = new XMLHTTPRequest()
xhr.open('GET', sessionUrl.render(), true)
xhr.send(null);



handshakeUrl = new Url("/tcp")
...
upstreamUrl = new URL()
upstreamUrl.populateFromURL(handshakeUrl)
upstreamUrl.extendPath(sessionKey)
transportUrl = new URL(upstreamUrl) // Similar to last two lines
transportUrl.extendPath(transport)
Orbited.CometTransport.connect(transportUrl.render())
upstreamUrl == '/tcp/ABC' # true
transportUrl == '/tcp/ABC/xhrstream' # true







}();