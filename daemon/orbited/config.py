map = {
    '[global]': {
        'orbit.port': '9000',
        'http.port': '8000',
        'admin.enabled': '0',
        'proxy.enabled': '0',
        'proxy.keepalive': 0,
        'proxy.keepalive_default_timeout': 300,
        'log.enabled': '1'        
    },
    '[admin]': {
        'admin.port': '9001'
    },
    '[proxy]': [        
    ],
    '[log]': {
        'log.access': ('screen',),
        'log.error': ('screen',),
        'log.event': ('screen',)
    }
}

def update(**kwargs):
    map.update(kwargs)
    return True

def load(filename):
    try:
        f = open(filename)
        lines = [ i.strip() for i in f.readlines() ]
        
    except IOError:    
        print filename, "could not be found. Using default configuration"
        return False
        #lines = default.split('\n')
                
    section = None
    for line in lines:
        line = line.strip(' ')        
        if '#' in line:
            line, comment = line.split('#', 1)
        if not line:
            continue
        if line.startswith('[') and line.endswith(']'):
            section = line
            if section not in map:
                map[section]  = {}
            continue            
            
        if section == "[proxy]":
            source, target = line.split('->')
            source = source.strip(' ')
            target = target.strip(' ')
            map[section].append((source, target))
            continue
        if '=' not in line:
            continue
#        line = line.replace(' =', '=')
#        line = line.replace('= ', '=')        

        key, value = line.split('=')
        key = key.strip(' ')
        value = value.strip(' ')
        if section == "[log]":
            if ',' in value:
                values = value.split(',')
                value = values[0].strip(' '), values[1].strip(' ')
            else:
                value = value,
        if section not in map:
            map[section] = dict()
        map[section][key] = value
    print "CONFIG"
    print map
    return True
    