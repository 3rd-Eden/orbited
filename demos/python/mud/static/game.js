orig_domain = document.domain
nickname = null
letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
request_array = Array()

function make_query_string(params) {
    out = "?"
    for (var key in params) {
        out = out + key + '=' + escape(params[key]) + '&'
    }
    /* Get rid of trailing & */
    return out.substring(0, out.length-1);
}

function createXMLHttpRequest() {
    try { return new ActiveXObject("Msxml2.XMLHTTP"); } catch (e) {}
    try { return new ActiveXObject("Microsoft.XMLHTTP"); } catch (e) {}
    try { return new XMLHttpRequest(); } catch(e) {}
    return null;
}

function astarta(str) {
    nickname = str
    e = document.getElementById('events');
    e.src=orbit_hostname + '/game|' + nickname + ',0,iframe_domain';
    join();
}

function join() {
    var url = "/connect"
    var params = {user:nickname}
    add_request(url,params)
}

function chat() {
    if (nickname == null) {
        var str = document.getElementById('input').value
        var newstr = ''
        for (var i = 0; i < str.length; i++) {
            if (letters.indexOf(str.charAt(i)) != -1) {
                newstr += str.charAt(i);
            }
        }
        if (newstr != '') {
            var main = document.getElementById('main')
            main.innerHTML += "<br><div style='text-align:center;color:blue;font-weight:bold;'>MAXHEADROOMMAXHEADROOMMAXHEADROOMMAXHEADROOMM..<br>M...........................................MA.<br>M....../``\\\\./``\\\\../``/\\.../``/\\...........MAX<br>Mxxxx /`/\\`\\/`/\\`\\\\/``/_/__/``/`/xxxxxxxxxxxMAX<br>Mxxxx/`/`/\\__/`/\\`\\\\`____````/`/xxxxxxxxxxxxMAX<br>M.../_/`/..\\_\\/..\\`\\\\\\___/``/`/.............MAX<br>M...\\_\\/ax....../_\\///../__/`/eadroom's.....MAX<br>M...............\\__\\/...\\__\\/...............MAX<br>M.......Adventure.with.Max.Headroom:........MAX<br>M..The.Max.Headroom.Max.Headroom.Adventure..MAX<br>M...........................................MAX<br>MAXHEADROOMMAXHEADROOMMAXHEADROOMMAXHEADROOMMAX<br>.AXHEAD/________________________/\\AXHEADROOMM..<br>..XHEAD\\___|:::::::::::::::|____\\ \\XHEADROO....<br>...HEAD/___|:::featuring:::|____/+ \\HEADR......<br>....EAD\\___|:Max::Headroom:|____\\+ /HEA........<br>.....AD/___|:::::::::::::::|____/ /XH..........<br>......D\\________________________\\/A............<br></div>"+'<br>Welcome, <b>'+newstr+'</b><br>'
            main.scrollTop = main.scrollHeight
            astarta(newstr)
        }
        else {
            document.getElementById('main').innerHTML += '<br>seriously, enter name<br>'
        }
    }
    else {
        var msg = document.getElementById('input').value
        while (msg.indexOf("=") > -1)
            msg = msg.replace('=', '[equals]')
        while (msg.indexOf("&") > -1)
            msg = msg.replace('&', '[ampersand]')
        var url = "/msg"
        var params = {user:nickname,msg:msg}
        add_request(url,params)
    }
    document.getElementById('input').value = ''
}

function add_request(url, params) {
  request_array[request_array.length] = url
  request_array[request_array.length] = params
  execute_request()
}

function get_request() {
  url = request_array[0]
  params = request_array[1]
  new_array = []
  for (x = 2; x < request_array.length; x++) {
    new_array[x-2] = request_array[x]
  }
  request_array = new_array
  return [url, params]
}

function execute_request() {
  if (request_array.length == 0) {
    return
  }
  [url, params] = get_request()
  document.domain = orig_domain
  xmlhttp = createXMLHttpRequest()
  xmlhttp.open("GET", url + make_query_string(params), false)
  xmlhttp.send(null)
  document.domain = top_domain
  execute_request()
}

function restart() {
    nickname = null
    document.getElementById('main').appendChild(document.getElementById('intro_splash'))
}

function cls() {
    document.getElementById('main').innerHTML = 'screen cleared'
}

function event(data) {
    if (data[0] == 'ping') {
        ping(data[1])
    }
    else if (data[0] == 'restart') {
        restart()
    }
    else if (data[0] == 'cls') {
        cls()
    }
    else {
        if (data[0] == 'GOD') {
            var div = god(data[1])
        }
        else if (data[0] == 'JOINLEAVE') {
            var div = joinleave(data[1])
        }
        else if (data[0] == 'SAY') {
            var div = say(data[1])
        }
        else if (data[0] == 'LOOKROOM') {
            var div = lookroom(data[1])
            div.className = 'bigblock'
        }
        else if (data[0] == 'LOOKPERSON') {
            var div = lookperson(data[1])
            div.className = 'bigblock'
        }
        else if (data[0] == 'LOOKITEM') {
            var div = lookitem(data[1])
            div.className = 'bigblock'
        }
        else if (data[0] == 'INVENTORY') {
            var div = inventory(data[1])
            div.className = 'bigblock'
        }
        else if (data[0] == 'WHO') {
            var div = who(data[1])
            div.className = 'bigblock'
        }
        else if (data[0] == 'COMBAT') {
            var div = combat(data[1])
            div.className = 'bigblock'
        }
        var main = document.getElementById('main')
        main.appendChild(div)
        main.scrollTop = main.scrollHeight
    }
}

function ping(data) {
    var url = "/msg"
    var params = {user:nickname,msg:'ping_reply'}
    add_request(url,params)
}

function combat(data) {
    var div = document.createElement('div')
    div.appendChild(chelp(data[0], [': ',' | ',': ', ' --]']))
    div.appendChild(chelp(data[1], [' ', ' ', ' for ', ' damage! --]']))
    div.appendChild(chelp(data[2], [' ', ' ', ' for ', ' damage! --]']))
    return div
}

function chelp(data, filler) {
    var name1 = document.createElement('span')
    name1.className = 'person'
    name1.innerHTML = data[0]
    var hp1 = document.createElement('span')
    hp1.className = 'direction'
    hp1.innerHTML = data[1]
    var name2 = document.createElement('span')
    name2.className = 'person'
    name2.innerHTML = data[2]
    var hp2 = document.createElement('span')
    hp2.className = 'direction'
    hp2.innerHTML = data[3]
    var hp = document.createElement('div')
    hp.innerHTML = '[-- '
    hp.appendChild(name1)
    hp.innerHTML += filler[0]
    hp.appendChild(hp1)
    hp.innerHTML += filler[1]
    hp.appendChild(name2)
    hp.innerHTML += filler[2]
    hp.appendChild(hp2)
    hp.innerHTML += filler[3]
    return hp
}

function god(data) {
    var div = document.createElement('div')
    div.innerHTML = data
    div.className = 'god'
    return div
}

function joinleave(data) {
    var person = document.createElement('span')
    person.innerHTML = data[0]
    person.className = 'person'
    var message = document.createElement('span')
    message.innerHTML = data[1]
    message.className = 'god'
    var direction = document.createElement('span')
    direction.innerHTML = data[2]
    direction.className = 'direction'
    var div = document.createElement('div')
    div.appendChild(person)
    div.appendChild(message)
    div.appendChild(direction)
    return div
}

function say(data) {
    var person = document.createElement('span')
    person.innerHTML = data[0]
    person.className = 'person'
    var message = document.createElement('span')
    message.innerHTML = data[1]
    message.className = data[2]
    var div = document.createElement('div')
    div.appendChild(person)
    div.appendChild(message)
    return div
}

function lookroom(data) {
    var name = document.createElement('div')
    name.innerHTML = data[0]
    name.className = 'roomname'
    var desc = document.createElement('div')
    desc.innerHTML = data[1]
    desc.className = 'roomdescription'
    var dire = getdirections(data[2])
    var occu = lookpeople(data[3])
    var item = lookitems(data[4])
    var div = document.createElement('div')
    div.appendChild(name)
    div.appendChild(desc)
    div.appendChild(dire)
    div.appendChild(occu)
    div.appendChild(item)
    return div
}

function getdirections(data) {
    var div = document.createElement('div')
    div.innerHTML = 'Obvious Exits: '
    for (var i = 0; i < data.length; i++) {
        var dir = document.createElement('span')
        dir.innerHTML = data[i]+' '
        dir.className = 'direction'
        div.appendChild(dir)
    }
    return div
}

function who(data) {
    var big = document.createElement('div')
    big.innerHTML = "People Currently Logged On:"
    big.appendChild(lookpeople(data))
    return big
}

function lookpeople(data) {
    var div = document.createElement('div')
    for (var i = 0; i < data.length; i++) {
        div.appendChild(lookperson(data[i]))
    }
    div.className = 'looking'
    return div
}

function lookperson(data) {
    var person = document.createElement('span')
    person.innerHTML = data[0]
    person.className = 'person'
    var description = document.createElement('span')
    description.innerHTML = data[1]
    description.className = 'persondescription'
    var guy = document.createElement('div')
    guy.appendChild(person)
    guy.appendChild(description)
    if (data.length == 5) {
        var attack = document.createElement('span')
        attack.className = 'direction'
        attack.innerHTML = data[2]
        var defense = document.createElement('span')
        defense.className = 'direction'
        defense.innerHTML = data[3]
        var hp = document.createElement('span')
        hp.className = 'direction'
        hp.innerHTML = data[4]
        var attributes = document.createElement('div')
        attributes.className = 'looking'
        attributes.innerHTML = 'attack: '
        attributes.appendChild(attack)
        attributes.innerHTML += '<br>defense: '
        attributes.appendChild(defense)
        attributes.innerHTML += '<br>hit points: '
        attributes.appendChild(hp)
        guy.appendChild(attributes)
    }
    return guy
}

function inventory(data) {
    var big = document.createElement('div')
    big.innerHTML = "You are carrying:"
    big.appendChild(lookitems(data))
    return big
}

function lookitems(data) {
    var itemdiv = document.createElement('div')
    for (var i = 0; i < data.length; i++) {
        itemdiv.appendChild(lookitem(data[i]))
    }
    itemdiv.className = 'looking'
    return itemdiv
}

function lookitem(data) {
    var itemname = document.createElement('span')
    itemname.innerHTML = data[0]
    itemname.className = 'item'
    var description = document.createElement('span')
    description.innerHTML = data[1]
    description.className = 'itemdescription'
    var item = document.createElement('div')
    item.appendChild(itemname)
    item.appendChild(description)
    if (data.length == 3) {
        var type = document.createElement('span')
        type.className = 'direction'
        type.innerHTML = data[2]
        var attributes = document.createElement('div')
        attributes.className = 'looking'
        attributes.innerHTML = 'item type: '
        attributes.appendChild(type)
        item.appendChild(attributes)
    }
    return item
}
