import app
import config
import sys

def main():
    config_file = "orbit.cfg"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    config.load(config_file)
    server = app.App()
    server.start()
    
    
if __name__ == "__main__":
    main()