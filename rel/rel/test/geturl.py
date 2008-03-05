import rel
rel.override()
from dez import io
from dez.network import Connection

def cb2(*args):
    print 'received this!',args

def cb(c):
    print 'wrote to connection!',c
    c.set_rmode_close(cb2)

def geturl(url):
    sock = io.client_socket(url,80)
    c = Connection((url,80),sock)
    c.write("GET / HTTP/1.0\r\n\r\n",cb,[c])
    rel.signal(2, rel.abort)
    rel.dispatch()

def main():
    import sys
    method = "pyevent"
    url = "www.google.com"
    if len(sys.argv) > 1:
        method = sys.argv[1]
        if len(sys.argv) > 2:
            url = sys.argv[2]
    rel.initialize([method])
    geturl(url)

if __name__ == "__main__":
    main()