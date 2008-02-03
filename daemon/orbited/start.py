from orbited.app import Application

def main():
    app = Application()
    app.start()
    
    
def daemon():
    print 'daemon'
    
    
    
def profile():
    import hotshot
    prof = hotshot.Profile("orbited.profile")
    prof.runcall(main)
    prof.close()