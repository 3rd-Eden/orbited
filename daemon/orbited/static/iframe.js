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
        console.log("iframe reload");
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
parent.window.location.attach_iframe(window.location);
// FIXME: Define this in orbited.js
