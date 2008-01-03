recent_stats = {'plugins':{},'sessions':{},'all':{}};
current_stats = {'plugins':{},'sessions':{},'all':{}};
item_visible = {};
history_length = 10;
graph_x = 300;
graph_y = 100;
x_size = graph_x/history_length;
//scale for max
function initialize() {
    traffic = document.getElementById('traffic');
    graph = document.getElementById('graph').getContext('2d');
    table = {'plugins':document.getElementById('plugins'),'sessions':document.getElementById('sessions')}
    recent_stats['all'] = make_full_dict();
}

function on_off(id) {
    var x = document.getElementById(id);
    if (item_visible[id] == 'block') {
        item_visible[id] = 'none';
    }
    else {
        item_visible[id] = 'block';
    }
    document.getElementById(id).style.display = item_visible[id];
}

function manage_link(type,name) {
    if (type == 'plugins') {
        return '<a href=/_/'+name+'/manage/ target=_blank>manage</a><br>';
    }
    // SOMETHING for sessions
}

function render_table_type(type) {
    table[type].innerHTML = '';
    for (plugin in recent_stats[type]) {
        table[type].innerHTML += '<a href=javascript:on_off("'+type+plugin+'");>'+plugin+'</a>';
        info = document.createElement('div');
        info.className = 'plugin_info';
        info.id = type+plugin;
        info.style.display = item_visible[type+plugin];
        info.innerHTML = manage_link(type,plugin);
        for (attribute in recent_stats[type][plugin]) {
            info.innerHTML += attribute+': <b>'+recent_stats[type][plugin][attribute][history_length-1]+'</b><br>';
        }
        table[type].appendChild(info);
    }
}

function render_tables() {
    traffic.innerHTML = 'users: <b>'+current_stats['all']['users']+'</b><br>messages per second: <b>'+current_stats['all']['msgs']+'</b><br>bandwidth: <b>'+current_stats['all']['bandwidth']+'</b> bytes per second';
    render_table_type('plugins');
    render_table_type('sessions');
}

function render_graph() {
    graph.clearRect(0,0,graph_x,graph_y);
    for (attribute in recent_stats['all']) {
        graph.beginPath();
        graph.moveTo(graph_x, graph_y - recent_stats['all'][attribute][0]);
        for (var x = 1; x < history_length; x++) {
            var a = x*x_size;
            var b = graph_y - recent_stats['all'][attribute][x];
            graph.lineTo(a,b);
        }
        graph.stroke();
    }
}

function render() {
    render_tables();
    render_graph();
}

function make_history_list() {
    var the_list = [];
    for (var x = 0; x < history_length; x++) {
        the_list[x] = 0;
    }
    return the_list;
}

function make_full_dict() {
    return {'bandwidth':make_history_list(),'msgs':make_history_list(),'users':make_history_list()}
}

function update_type(data,type) {
    clear_stats(type);
    for (plugin in data) {
        if (! (plugin in recent_stats[type])) {
            recent_stats[type][plugin] = make_full_dict();
            item_visible[type+plugin] = 'none';
        }
        for (attribute in data[plugin]) {
            recent_stats[type][plugin][attribute].shift();
            recent_stats[type][plugin][attribute].push(data[plugin][attribute]);
            current_stats[type][attribute] += data[plugin][attribute];
            current_stats['all'][attribute] += data[plugin][attribute];
        }
        if (recent_stats[type][plugin]['users'] == 0) {
            recent_stats[type][plugin] = null;
        }
    }
}

function update_recent_all() {
    for (attribute in current_stats['all']) {
        recent_stats['all'][attribute].shift();
        recent_stats['all'][attribute].push(current_stats['all'][attribute]);
    }
}

function clear_stats(type) {
    current_stats[type]['bandwidth'] = 0;
    current_stats[type]['msgs'] = 0;
    current_stats[type]['users'] = 0;
}

function update(data) {
    clear_stats('all');
    clear_stats('plugins');
    clear_stats('sessions');
    update_type(data['plugins'],'plugins');
    update_type(data['sessions'],'sessions');
    update_recent_all();
}

function receive_event(data) {
    update(data);
    render();
}