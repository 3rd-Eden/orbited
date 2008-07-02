import os
import sys

map = {
    '[global]': {
        'dispatch.enabled': '0',
        'pid.location': '/tmp/orbited.pid'
    },
    '[logging]': {
        'debug': 'SCREEN',
        'info': 'SCREEN',
        'access': 'SCREEN',
        'warn': 'SCREEN',
        'error': 'SCREEN',
        'enabled.default': 'info,access,warn,error',
    },
    '[loggers]': {
    
    },
    'default_config': 1, # set to 0 later if we load a config file
    '[listen]': [
    ],
    '[access]': [
    ],
    '[static]': {
    
    }
    
}

defaults = {
    '[global]': {
        'dispatch.enabled': '1',
        'dispatch.port': '9000',
    },
    '[access]': [
        ('localhost', 9998), # Allow WebSocket test daemon
        ('irc.freenode.net', 6667), # Allow chat demo
        ('www.google.com', 80) # Telnet demo defaults
    ],
    '[listen]': [
        'http://:8000',
#        'https://:8043'
    ],
#    '[ssl]': {
#        'key': 'orbited.key',
#        'crt': 'orbited.crt'
#    },
    '[loggers]': {
        'WebSocket': 'debug,info,access,warn,error',
    },        
}

def update(**kwargs):
    map.update(kwargs)
    return True

def setup():
    try:
        path = os.path.join('/', 'etc', 'orbited.cfg')
        configfile = open(path, 'r')
        print "using config file:", path
        return load(configfile)
    except:
        pass
    try:
        path = os.path.join('/', 'Program Files', 'Orbited', 'etc', 'orbited.cfg')
        configfile = open(path, 'r')
        print "using config file:", path
        return load(configfile)
    except:
        pass
    try:
        configfile = open('orbited.cfg', 'r')
        print "using config file: ./orbited.cfg"
        return load(configfile)
    except:
        pass
    print "Could not locate configuration file. Using default configuration"
    for key, val in defaults.items():
        if isinstance(map.get(key), dict):
            map[key].update(val)
        else:
            map[key] = val
    
def load(f):
    lines = [line.strip() for line in f.readlines()]
    map['default_config'] = 0    
    section = None
    try:
        for (i, line) in enumerate(lines):
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
                if ':' in line:
                    addr, port = line.split(':', 1)
                    port = int(port)
                else:
                    addr, port = target, 80
                map[section].append((addr, port))
                continue
            if section == '[listen]':
                map[section].append(line)
                continue
            
            # skip lines which do not assign a value to a key
            if '=' not in line:
                print "Configuration parse error on line", i
                sys.exit(0)
            
            key, value = [side.strip() for side in line.split('=', 1)]
            
            # in log section, value should be a tuple of one or two values
            if section == '[log]':
                value = tuple([val.strip() for val in value.split(',', 1)])
            
            map[section][key] = value
    except Exception, e:
        print e
        sys.exit(0)
    return True

setup()