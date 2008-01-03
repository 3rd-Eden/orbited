id = 0;
function createXMLHttpRequest() {
  try { return new ActiveXObject("Msxml2.XMLHTTP"); } catch (e) {}
  try { return new ActiveXObject("Microsoft.XMLHTTP"); } catch (e) {}
  try { return new XMLHttpRequest(); } catch(e) {}
  return null;
}

function connect() {
  name = document.getElementById('nickname').value
  e = document.getElementById('events')
  e.src='/pylonschat|' + name + ',0,iframe'
  join(name);
}

function join(user) {
  id = id + 1
  xmlhttp = createXMLHttpRequest();
  xmlhttp.open("GET", "chat/join/" + user, true)
  xmlhttp.send(null);
}

function event(data) {
  chat_box = document.getElementById('box')
  div = window.parent.document.createElement('div')
  div.className = "event"
  div.innerHTML = data
  chat_box.appendChild(div)
  chat_box.scrollTop = chat_box.scrollHeight;
}

function send_msg() {
  id = id + 1
  xmlhttp = createXMLHttpRequest();
  msg = document.getElementById('chat').value
  nickname = document.getElementById('nickname').value
  xmlhttp.open("GET", "chat/msg/" + nickname + "/" + msg + "/" + id)
  xmlhttp.send(null);
}
