import os

map = {
    '[global]': {
        'admin.enabled': '0',
        'proxy.enabled': '1',
        'proxy.keepalive': '1',
        'proxy.keepalive_default_timeout': '300',
        'log.enabled': '1',
        'session.default_key': '0', # TODO: change to token.default_key
        'session.timeout': '5',
        'event.retry_limit': '1'
    },
    '[op]': {
        'port': '9000',
        'bind_addr': '127.0.0.1',
    },    
    '[http]': {
        'port': '8000',
        'bind_addr': '127.0.0.1',
    },
    '[transport]': {
        'buffer': '1',
        'num_retry_limit': '1',
        'timeout': '30',
        'default': 'stream',
        'xhr.timeout': '30',
    },
    # TODO: in dispatcher, use this url rather than the routing one
    '[cometwire]': {
        'url': '/_/cometwire/',
        'connect_timeout': '3',
    },
    '[csp]': {
        'upstream_url':'/_/csp/up/xhr',
    },
    '[admin]': {
        'admin.port': '9001'
    },
    '[routing]': {
        '/_/static/': ('static', (os.path.join(os.path.dirname(__file__), 'static'),)),        
        '/_/': ('system', ()),
        '/': ('transport', ()),
        # ""/djangoapp/ -> wsgi:djangoapp.application:main""
        # '/djangoapp/': ('wsgi', ('djangoapp.application','main'))

        # ""/static/ -> static:/some/where""
        # '/static/': ('static', ('/somewhere/somewhere',))

        # ""/rubyapp/ -> proxy:127.0.0.1:80""
        # '/rubyapp': ('proxy', ('127.0.0.1', '80'))

        # ""/event/ -> transport""
        # '/event/': ('transport', (,))
    },
    '[revolved]': {
        'auth': 'open',
    },
    
    '[revolved_auth:http]': {
        'callback.authorize_connect': "http://localhost:4700/revolved_auth_connect",
        'callback.authorize_channel': "http://localhost:4700/revolved_auth_channel"
    },
        
    
    '[logging]': {
        'debug': '',
        'info': 'SCREEN',
        'access': 'SCREEN',
        'warn': 'SCREEN',
        'error': 'SCREEN',
        'enabled.default': '1',
    },
    '[loggers]': {

    },
    'default_config': '1', # set to 0 later if we load a config file
}

def update(**kwargs):
    map.update(kwargs)
    return True

class ParseError(Exception):
    pass

def error(f,s,n,l):
    return "Invalid entry in \"%s\" under \"%s\" on line %s:\r\n-- \"%s\"\r\nConfig parsing aborted."%(f,s,n,l)

def load(filename):
    try:
        f = open(filename)
        lines = f.readlines()
        map['default_config'] = '0'
    except IOError:
        print filename, 'could not be found. Using default configuration'
        return False

    section = None
    line_number = 0
    for full_line in lines:
        line_number += 1
        # ignore comments
        line = full_line.strip()
        if '#' in full_line:
            line, comment = [side.strip() for side in full_line.split('#', 1)]
        if not line:
            continue

        # start of new section; create a dictionary for it in map if one
        # doesn't already exist
        if line.startswith('[') and line.endswith(']'):
            section = line
            if section not in map:
                map[section] = {}
            continue

        # assign each source in the proxy section to a target address and port
        if section == '[routing]':
            if '->' not in line:
                raise ParseError, error(filename,section,line_number,full_line)
            source, target = [side.strip() for side in line.split('->')]
            location = target.split(':', 2)
            keyword = location.pop(0)
            map[section][source] = (keyword, tuple(location))
            continue

        # skip lines which do not assign a value to a key
        if '=' not in line:
            continue
        
        key, value = [side.strip() for side in line.split('=', 1)]
        if not key or not value:
            raise ParseError, error(filename,section,line_number,full_line)

        # in log section, value should be a tuple of one or two values
        if section == '[logging]':
            value = tuple([val.strip() for val in value.split(',')])

        map[section][key] = value
    return True
