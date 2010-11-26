import sys

TESTING_HOSTS = ['www.orbited', 'sub.www.orbited', 'xp.orbited']
LOCALHOST = '127.0.0.1'

class HostsFile(object):
    HOSTS = '/etc/hosts'
    
    def __init__(self):
        self._entries = {}
    
    def _with_file(self, body, *args, **kwargs):
        f = file(*args, **kwargs)
        result = body(f)
        f.close()
        return result
    
    def load(self):
        return self._with_file(self._readlines, self.HOSTS, 'r')
    
    def _readlines(self, f):
        for line in f.readlines():
            self._readline(line)
    
    def _readline(self, line):
        comment = None
        if '#' in line:
            line, comment = line.split('#')
        parts = line.split()
        if comment is not None:
            parts[-1] += ' #' + comment
        self._entries[parts[0]] = parts[1:]
    
    def store(self):
        contents = str(self)
        def writelines(f):
                print >>f, contents
        return with_file(writelines, HOSTS, 'r')
    
    def add(self, entry, alias):
        self._entries.setdefault(entry, []).insert(0, alias)
    
    def remove(self, entry, alias):
        if entry in self._entries:
            self._entries[entry].remove(alias)
            if not self._entries[entry]:
                del self._entries[entry]
    
    def __str__(self):
        return '\n'.join(['\t'.join([key, ' '.join(value)])
                          for key, value in self._entries.items()])

class OrbitedDaemon(object):
    
    def __init__(self):
        pass
    
    def start(self):
        pass
    
    def stop(self):
        pass

class SeleniumRCServer(object):
    
    def __init__(self):
        pass
    
    def start(self):
        pass
    
    def stop(self):
        pass

def main(argv):
    hosts = HostsFile()
    hosts.load()
    print str(hosts)
    for host in TESTING_HOSTS:
        hosts.add(LOCALHOST, host)
    print str(hosts)
    for host in TESTING_HOSTS:
        hosts.remove(LOCALHOST, host)
    print str(hosts)
    

if (__name__=='__main__'):
    main(sys.argv)

orbited = OrbitedDaemon()
selenium_rc = SeleniumRCServer()

def setup():
    hosts = HostsFile()
    hosts.load()
    for host in TESTING_HOSTS:
        hosts.add(LOCALHOST, host)
    hosts.store()
    orbited.start()
    selenium_rc.start()
    
def teardown():
    selenium_rc.stop()
    orbited.stop()
    hosts = HostsFile()
    hosts.load()
    for host in TESTING_HOSTS:
        hosts.remove(LOCALHOST, host)
    hosts.store()
