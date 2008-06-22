if True:
    import log
    config = {
        '[logging]': {
            'debug': 'SCREEN',
            'info': 'SCREEN',
            'access': 'SCREEN',
            'warn': 'SCREEN,warn.log',
            'error': 'SCREEN,error.log',
            'enabled.default': '1',
        },
        '[loggers]': {
            'access': 1,
            'HTTPDaemon': '2',
        }
    }
    
    l = log.setup(config)
    
    http = l.get_logger("HTTPDaemon")
    
    
    http.debug('testing')
    http.access('HTTP', 'yoho')
    http.debug('testing')
    http.warn('what')
    http.debug('testing')
    http.error('err RAWR')
    http.debug('testing',stack=True)
    http.access('FTP', 'yoho')
    try:
        raise Exception()
    except:
        http.debug('wtf', tb=True)
        http.debug('wtf2', stack=True)
