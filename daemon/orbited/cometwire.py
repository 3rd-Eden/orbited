from orbited.config import map as config
from orbited.op.message import SingleRecipientMessage
from orbited.json import json
import random
import event

#COMETWIRE_URL = config['[cometwire]']['url']
#CSP_UPSTREAM_URL = config['[csp]']['upstream_url']

TIMEOUT = int(config['[cometwire]']['connect_timeout'])
#URLS = [ COMETWIRE_URL, CSP_UPSTREAM_URL ]

class CometWire(object):
    """Maps a downstream connection to an upstream connection."""
    
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.transports = self.dispatcher.app.transports
#        for url in URLS:
#            self.transports.set_identifier_callback(url, self.__client_connect_callback, [url])
        self.callbacks = {}
        self.downstream_connections = {}
        self.timers = {}
        
    def set_connect_cb(self, url, cb, args=[]):
        self.callbacks[url] = cb, args
        self.dispatcher.add_transport_rule(url)
        self.transports.set_identifier_callback(url, self.__client_connect_callback, [url])
        
    def __client_connect_callback(self, url):
        key = self.__generate_key()
        initial_msgs = []
        initial_msgs.append(SingleRecipientMessage(json.encode(["ID", key]), key))
        self.dispatcher.app.upstream.set_connect_cb(key, self.__upstream_connected, [key, url])
        self.timers[key] = event.timeout(TIMEOUT, self.__upstream_connect_timed_out, key, url)
        return (key, initial_msgs)
        
    def __upstream_connect_timed_out(self, key, url):
        conn = self.transports.get(key)
        conn.send_msgs([SingleRecipientMessage(json.encode(["TIMEOUT", []]), key)])
        # TODO: send a 'timeout' msg then close on success or failure of that msg?
        conn.close()
        self.timers[key].delete()
        del self.timers[key]
        
    def __generate_key(self):
        # return 'test'
        return ''.join([random.choice("123456789ABCDEF") for i in range(10)])
        
    def __upstream_connected(self, conn, key, url):
        # Are we waiting on this particular upstream connection?
        if key not in self.timers:
            # TODO: error...?
            return
        self.timers[key].delete()
        del self.timers[key]
        
        if url in self.callbacks:
            upstream_conn = conn
            downstream_conn = self.transports.get(key)
            downstream_conn.send(json.encode(["CONNECTED", []]))
            cb, args = self.callbacks[url]
            #self.callbacks[url]
            return cb(key, upstream_conn, downstream_conn, *args)
        else:
            conn.set_receive_cb(self.__upstream_receive_cb)

    def __upstream_receive_cb(self, data):
        print "UPSTREAM ---- GOT DATA", data

