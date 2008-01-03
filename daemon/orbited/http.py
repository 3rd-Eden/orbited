import io
import event
import random
import transport
import static
from debug import *
def debug(arg):
    return
    print arg
    
from proxy2 import Proxy
from config import map as config
class ProxyChecker(object):
    def __init__(self, rules):
        self.rules = rules
        
    def __call__(self, url):
        if '|' in url:
            return False
        if url.startswith('/_/'):
            
            data = getattr(static, url[3:], None)
            if data:
                raise "StaticContent", data
        if config['[global]']['proxy.enabled'] != '1':
            raise "ProxyDisabled", url
        for match, target in self.rules:
            if url.startswith(match):
                port = 80
                addr = None
                if '//' in target:
                    addr = target.split('//', 1)[1]
                if ':' in addr:
                    addr, port = addr.split(':', 1)                
                return (addr, int(port))
        raise "NoDestination", url
        

class HTTPDaemon(object):
    def __init__(self, app, log, port, rules):
        log("startup", "Created http@%s" % port)
        self.log = log
        sock = io.server_socket(port)
        self.app = app
        self.listen = event.event(self.accept_connection, handle=sock, evtype=event.EV_READ | event.EV_PERSIST)
        self.listen.add()
        self.proxy_checker = ProxyChecker(rules)
        self.keepalive_enabled = (config['[global]']['proxy.keepalive'] == '1')
        
        
    def accept_connection(self, ev, sock, event_type, *arg):
        sock, addr = sock.accept()
#        self.log("ACCESS", "http", *addr)

        HTTPConnection(self.app, self.log, self.proxy_checker, sock, addr, self.keepalive_enabled)
        
        
class HTTPConnection(object):

    def debug(self, data):
        return
        print "%s %s" % (self, data)
    def __str__(self):
        return "<HTTPConnection %s>" % self.id
    id = 0
    def __init__(self, app, log, proxy_checker, sock, addr, keepalive_enabled):
        self.keepalive_enabled = keepalive_enabled
        HTTPConnection.id += 1
        self.id = HTTPConnection.id 
        self.keepalive_timer = None
        self.proxy_id = 0
        self.debug("NEW Connection")
        self.sock = sock
        self.addr = addr
        self.app = app
        self.log = log
        self.proxy_checker = proxy_checker
        self.events = []
        self.proxy = None
        self.finish_close = False
        
        self.setup()
        
    def setup(self):
        self.revent = event.read(self.sock, self.read_ready)
        self.wevent = None
        self.buffer = ""
        self.write_buffer = ""
        self.request = HTTPRequest(self.log, self.proxy_checker)
        self.current_response = None
        
    def proxy_complete(self, proxy, complete=False):
        if complete:
            self.close()
        else:
            self.set_keepalive_timer()
            self.setup()
        
        
    def proxy_expired(self, proxy):
        self.debug("proxy expired")
        if self.proxy == proxy:
            self.proxy = None
            
#    def proxy_complete(self, proxy):
#        self.debug("Proxy Completed!")
#        self.set_keepalive_timer()
#        self.setup()
        

    def close(self):
#        tbinfo()
        if hasattr(self, 'proxy') and self.proxy:
            self.proxy.close_server()
        self.debug("CONNECTION CLOSED")
        self.sock.close()
        if self.revent:
            self.revent.delete()
            self.revent = None
        if self.wevent:
            self.wevent.delete()
            self.wevent = None
        if hasattr(self.request, 'user_id'):
            # This is an orbited connection that closed...
            self.app.expire_http_connection(self)
            
            
        
    def write_ready(self):
        if not self.write_buffer:
            if self.current_response:
                self.current_response.success(self)
                self.current_response = None
            if not self.events:
                
                self.wevent = None
                if self.finish_close:
                    self.close()
                return None
            self.current_response = self.events.pop(0)
            self.write_buffer = self.current_response.data        
        try:
            bsent = self.sock.send(self.write_buffer)
            debug("http sent: %s" % self.write_buffer[:bsent])
            self.write_buffer = self.write_buffer[bsent:]
            return True
        except io.socket.error:
            self.current_response.failure(self)
            self.close()
            return None

    def respond(self, response):
        self.events.append(response)
        if not self.wevent:
            self.wevent = event.write(self.sock, self.write_ready)

            
    def read_ready(self):
        try:
            data = self.sock.recv(io.BUFFER_SIZE)
            if not data:
                self.close()
                return None
            return self.read(data)
        except io.socket.error:
            self.close()
            return None

    def read(self, data):
        try:
            proxy_info =  self.request.read(data)
            # print 'a'
        except "NoDestination", url:
            self.complete = True
            self.log("ERROR", "PROXY\tNo proxy rule matches: " + url)
            return self.close()
        except "ProxyDisabled", url:
            self.complete = True
            self.log("ERROR", "PROXY\tProxy disabled. No match: " + url)
            return self.close()
        except "StaticContent", data:
            self.write_buffer = data
            self.wevent = event.write(self.sock, self.write_ready)
            self.finish_close = True
            return
        if proxy_info:
            addr, port = proxy_info
            self.log("ACCESS", "PROXY\t%s -> http://%s:%s" % (self.request.headers['url'],addr, port))
            a = self.request.action + "\r\n" + "\r\n".join([ ": ".join(i) for i in self.request.headers.items()]) + "\r\n\r\n"
            
            if self.proxy:
                # print " use old proxy"
                if (self.proxy.addr, self.proxy.port) == (addr, port):
                    # print "go!"
                    id_parts = self.proxy.id.split('.')
                    id_parts[2] = str(int(id_parts[2]) + 1)
                    self.proxy.id = '.'.join(id_parts)
                    self.proxy.next_request(self.sock, a)
                    self.revent.delete()
                    self.revent = None
                else:
                    # print "old proxy is to the wrong server"
                    self.proxy.close_server()
                    self.proxy = None
            if not self.proxy:
                # print "No proxy.. create one"
                self.keepalive_timeout = 0
                self.debug("headers: %s" % (self.request.headers,))
                self.debug("Checking Keep-alive")
                self.debug("Connection: %s" % self.request.headers.get("connection", "Close"))
                if self.request.headers.get("connection", "Close").lower() == "keep-alive" and self.keepalive_enabled:
                    # print "server says keepalive"
                    self.debug("Keep-alive: %s" % self.request.headers.get("keep-alive", -1))
                    self.keepalive_timeout = int(self.request.headers.get("keep-alive", config['[global]']['proxy.keepalive_default_timeout']))
                self.proxy_id += 1
                id = str(self.id) + '.' + str(self.proxy_id) + '.' + '1'
                self.proxy = Proxy(self, addr, port, self.sock, buffer=a, id=id, keepalive=self.keepalive_enabled )
                self.set_keepalive_timer()
                self.revent.delete()
                self.revent = None
            return None
        elif self.request.complete:
            self.log("ACCESS", "HTTP\t(%s, %s, %s)" % self.key())        
            self.app.accept_http_connection(self)
            return None
        return True

    def set_keepalive_timer(self):
        return
        if self.keepalive_timer:
            self.keepalive_timer.delete()
        self.keepalive_timer = event.timeout(self.keepalive_timeout, self.keepalive_timeout)
    
    def keepalive_timeout(self):
        if self.proxy:
            self.proxy.close_client()
            self.proxy.close_server()
        self.close()
        
    def key(self):
        return self.request.key()

        

class HTTPRequest(object):


    def __init__(self, log, proxy_checker):
        self.buffer = ""
        self.state = "action"
        self.headers = {}
        self.complete = False
        self.log = log
        self.proxy_checker = proxy_checker
        
    def read(self, data):
        self.buffer += data
        return self.process()
        
    def process(self):
        return getattr(self, 'state_%s' % self.state)()
        
    def state_action(self):
        if '\r\n' not in self.buffer:
            return
        i = self.buffer.find('\r\n')
        self.action = self.buffer[:i]
        debug("action: %s" % self.action)
        self.buffer = self.buffer[i+2:]
        self.state = "headers"
        self.headers['url'] = self.action.split(' ')[1]
        return self.state_headers()
        
    def state_headers(self):
        while True:
            index = self.buffer.find('\r\n')
            if index == -1:
                break;
            if index == 0:
                self.buffer = self.buffer[2:]
                self.state="completed"
                return self.state_completed()
            debug("line: %s" % self.buffer[:index])
#            debug("split: %s" % self.buffer[:index].split(': '))
            key, value = self.buffer[:index].split(': ')
            self.headers[key.lower()] = value
            self.buffer = self.buffer[index+2:]

    def state_completed(self):
        target_addr = self.proxy_checker(self.headers['url'])
        if target_addr:
            debug("target_addr: " + str(target_addr))
            return target_addr 
        else:
            self.location, identifiers = self.headers['url'].split('|')
            self.transport_name = 'iframe'
            if ',' not in identifiers:
                self.user_id = identifiers
                self.session_id = '0'
            else:
                self.user_id, self.session_id = identifiers.split(',', 1)
            if ',' in self.session_id:
                self.session_id, self.transport_name = self.session_id.split(',', 1)
            if ',' in self.transport_name:
                self.transport_name, self.extra = self.transport_name.split(',', 1)
            self.complete = True
            debug("completed")
            
    def key(self):
        return self.user_id, self.session_id, self.location
        
#    def state_body():
#        if len(self.buffer) < int(self.headers['content-length']):
#            return
#        self.body = self.buffer[:self.headers['content-length']
        # TODO: Exception if there's more data. when would this happen?
#        return True
        
#            if extra:
#                self.state = "body"
#            self.buffer = extra
#        elif state == "body":
#            self.buffer += data
#            if len(self.buffer) >= request['content-length']:

    