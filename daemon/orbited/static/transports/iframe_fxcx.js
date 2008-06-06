function getURLParam(strParamName){
  var strReturn = "";
  var strHref = window.location.href;
  if ( strHref.indexOf("?") > -1 ){
    var strQueryString = strHref.substr(strHref.indexOf("?")).toLowerCase();
    var aQueryString = strQueryString.split("&");
    for ( var iParam = 0; iParam < aQueryString.length; iParam++ ){
      if (
aQueryString[iParam].indexOf(strParamName.toLowerCase() + "=") > -1 ){
        var aParam = aQueryString[iParam].split("=");
        strReturn = aParam[1];
        break;
      }
    }
  }
  return unescape(strReturn);
}

function extract_xss_domain(old_domain) {
  domain_pieces = old_domain.split('.');
  if (domain_pieces.length === 4) {
    var is_ip = !isNaN(Number(domain_pieces.join('')));
    if (is_ip) {
      return old_domain;
    }
  }
  return domain_pieces.slice(-2).join('.');
}

function reload() {
    if(console !== undefined) {
//        console.log("iframe reload fxcx");
    }
    // TODO: This doesn't actually reload, but comet streaming will stop
    // after the predefined Content-Length has been reached. Fix this.
}

function e(data) {
    window.location.e(data)
}
/*window.location.crossdomain = function(data) { alert(data); }
function timeout() {
    window.location.crossdomain('ahoy!')
}
window.setInterval(timeout, 10000)
*/
p = function() {}
window.onError = null;
//document.domain = extract_xss_domain(document.domain);
//alert('attaching iframe1');
//alert(this);
//alert(this.contentWindow);
var attach_fname = getURLParam("attach_fname")
if (attach_fname == "")
    attach_fname = "attach_iframe"
f = parent.window.location[attach_fname]
f(window);
// FIXME: Define this in orbited.js
