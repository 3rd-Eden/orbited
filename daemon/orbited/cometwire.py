from orbited.config import map as config
from orbited.op.message import SingleRecipientMessage
from orbited.json import json
import random

COMETWIRE_URL = config['[cometwire]']['url']


class CometWire(object):
    
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        dispatcher.app.transports.set_identifier_callback(COMETWIRE_URL, self.__client_connect_callback)
    
    def __client_connect_callback(self):
        key = self.__generate_key()
        initial_msgs = []
        
        initial_msgs.append(SingleRecipientMessage("Hello 1", (key, COMETWIRE_URL)))
        initial_msgs.append(SingleRecipientMessage("Hello 2", (key, COMETWIRE_URL)))
        initial_msgs.append(SingleRecipientMessage("Hello 3", (key, COMETWIRE_URL)))
        
        return (key, initial_msgs)
        
    def __generate_key(self):
        return ''.join([random.choice("123456789ABCDEF") for i in range(10)])
        
    def connect_upstream(self, req):
        