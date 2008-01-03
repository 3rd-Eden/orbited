#import psyco
#psyco.full()
import sys
import os
#sys.path.insert(0, os.path.abspath('.'))
from orbited import config
from orbited.app import Application
from orbited import transport
from orbited import plugin
from orbited.http import router
def main():
    # Config
    config_file = 'orbited.cfg'
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    config.load(config_file)
    
    # Transports
    transport.load_transports()
    
    # Plugins
    plugin.load()
    
    # Setup Router
    router.setup()
    
    # Create Server
    server = Application()
    
    # Start Server
    server.start()

if __name__ == '__main__':
    main()
