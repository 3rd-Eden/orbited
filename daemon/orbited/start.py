import rel
rel.override()
#rel.initialize(["poll"])
from orbited.app import Application
from orbited.config import map as config
from orbited.config import load as load_config

def main():    
    import sys
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        load_config(config_file)
        print "with config file: %s" % config_file
    else:
        print "with default configuration"
    app = Application(config)
    app.start()
    
    
def daemon():
    print 'daemon'
    
    
    
def profile():
    import hotshot
    prof = hotshot.Profile("orbited.profile")
    prof.runcall(main)
    prof.close()
