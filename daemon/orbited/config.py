map = {
    '[global]': {
        'http.port': '7000',
        'log.enabled': '0'
    },
    '[access]': [
        ('127.0.0.1', 9998), # Allow WebSocket test daemon
        ('irc.freenode.net', 6667), # Allow chat demo
    ],

    '[logging]': {
        'debug': 'SCREEN',
        'info': 'SCREEN',
        'access': 'SCREEN',
        'warn': 'SCREEN',
        'error': 'SCREEN',
        'enabled.default': 'info,access,warn,error',
    },
    '[loggers]': {
        'WebSocket': 'debug,info,access,warn,error',
    },        
    'default_config': 1, # set to 0 later if we load a config file
}

def update(**kwargs):
    map.update(kwargs)
    return True

def load(filename):
    try:
        f = open(filename)
        lines = [line.strip() for line in f.readlines()]
        map['default_config'] = 0
    
    except IOError:    
        print filename, 'could not be found. Using default configuration'
        return False
        # lines = default.split('\n')
    
    section = None
    for line in lines:
        
        # ignore comments
        if '#' in line:
            line, comment = line.split('#', 1)
        if not line:
            continue
        
        # start of new section; create a dictionary for it in map if one
        # doesn't already exist
        if line.startswith('[') and line.endswith(']'):
            section = line
            if section not in map:
                map[section]  = {}
            continue
        
        # assign each source in the proxy section to a target address and port
        if section == '[access]':
            if ':' in target:
                addr, port = target.split(':', 1)
                port = int(port)
            else:
                addr, port = target, 80
            map[section].append((addr, port))
            continue
        
        # skip lines which do not assign a value to a key
        if '=' not in line:
            continue
        
        key, value = [side.strip() for side in line.split('=', 1)]
        
        # in log section, value should be a tuple of one or two values
        if section == '[log]':
            value = tuple([val.strip() for val in value.split(',', 1)])
        
        map[section][key] = value
        
    return True
