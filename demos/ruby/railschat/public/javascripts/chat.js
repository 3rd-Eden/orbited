id = 0

/* 
 * This is just boilerplate to create an XHR object. Should work on most
 * browsers.
 */
function createXMLHttpRequest() {
  try { return new ActiveXObject("Msxml2.XMLHTTP"); } catch (e) {}
  try { return new ActiveXObject("Microsoft.XMLHTTP"); } catch (e) {}
  try { return new XMLHttpRequest(); } catch(e) {}
  return null;
}

/* 
 * We need to do two things to connect. 1) Initialize the orbited event
 * stream. In this case we are using the iframe transport. 2) We need to
 * let the chat server know we are connected so it sends us any future
 * messages.
 */
function connect() {
  name = document.getElementById('nickname').value
  e = document.getElementById('events')
  e.src='/railschat|' + name + ',0,iframe'
  join(name);
}

/* 
 * Here we actually create the request to the chat server to join the chat.
 * This is just a helper function that is called by connect.
 */
function join(user) {
  xmlhttp = createXMLHttpRequest();
  xmlhttp.open("GET", "/chat/join?user=" + user, true)
  xmlhttp.send(null);
}

/* 
 * This will get the contents out of msg input box and send it to the server.
 */
function send_msg() {
  id = id + 1
  xmlhttp = createXMLHttpRequest();
  msg = document.getElementById('chat').value
  nickname = document.getElementById('nickname').value
  xmlhttp.open("GET", "/chat/msg?id=" + id + "&user=" + nickname + "&msg=" + msg, true)
  xmlhttp.send(null);
}

/* 
 * This is the function that orbited will call from the iframe whenever it
 * receives an event. We are expecting data to be a string and we just want
 * to dump the whole string into the chat_box.
 */
function event(data) {
  chat_box = document.getElementById('box')
  div = window.parent.document.createElement('div')
  div.className = "event"
  div.innerHTML = data
  chat_box.appendChild(div)
  chat_box.scrollTop = chat_box.scrollHeight;
}