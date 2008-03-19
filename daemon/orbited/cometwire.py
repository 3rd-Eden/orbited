from orbited.config import map as config
from orbited.op.message import SingleRecipientMessage
from orbited.json import json
import random

COMETWIRE_URL = config['[cometwire]']['url']


class CometWire(object):
    
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.dispatcher.app.transports.set_identifier_callback(COMETWIRE_URL, self.__client_connect_callback)
    
    def __client_connect_callback(self):
        key = self.__generate_key()
        initial_msgs = []
        
        initial_msgs.append(SingleRecipientMessage(key, (key, COMETWIRE_URL)))
        
        self.dispatcher.app.upstream.set_connect_cb(key, self.__upstream_connected, [key])
        
        return (key, initial_msgs)
        
    def __generate_key(self):
        return ''.join([random.choice("123456789ABCDEF") for i in range(10)])
        
    def __upstream_connected(self, conn, key):
        print "UPSTREAM CONNECTED", key
        conn.set_receive_callback(self.__upstream_receive_cb)
    
    def __upstream_receive_cb(self, data):
        print "UPSTREAM ---- GOT DATA", data