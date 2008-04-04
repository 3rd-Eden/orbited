"""
Revolved implements a publish/subscribe infrastructure on top of CSP.

Revolved Backends implement an interface to a publish/subscribe system
such as IRC, XMPP, AMQP, etc. Revolved connections will interface to one of
those backends.

Revolved Authentication Backends implement an authorization interface, so that
external providers such as a database (or plain text file) can be used to 
determine whether or not clients are allowed to connect, publish, and subscribe.

This has proper nose tests, so let's try to be sure they keep working when
we modify this stuff.
"""

from orbited.json import json
from orbited.logger import get_logger

log = get_logger("revolved")

#######################################################################
# TODO: The Revolved dispatcher will need to handle calls to dispatcher.publish()
# in order to actually publish messages to clients. Everything else should be
# implemented.

class DummyCSPHandler(object):
    
    def __init__(self):
        self.connect_callbacks = []
    
    def trigger_connection_made(self, port, conn):
        """Notify listeners of a new CSP Connection."""
        cb, args = self.connect_callbacks[port]
        cb(conn, *args)
    
    # Callbacks
        
    def set_internal_connect_cb(self, port cb, args=[]):
        self.connect_callbacks.append( (cb, args) )
    
#    def remove_connect_callback(self, cb):
#        for fn, args in self.connect_callbacks:
#            if fn == cb:
#                self.connect_callbacks.remove( (fn, args) )
#                break
                
class DummyCSPConnection(object):
    
    def __init__(self):
        self.disconnect_callbacks = []
        self.message_callbacks = []
    
    def send(self, data):
        """Send a message on this connection."""
        pass
    
    def disconnect(self):
        """Disconnect this connection."""
        # Triggered by the revolved connection upon a DISCONNECT message
        for cb, args in self.disconnect_callbacks:
            cb(self, *args)
   
    def on_receive_message(self, msg):
        """Handle a received message."""
        for cb, args in self.message_callbacks:
            cb(self, msg, *args)
              
    # Callbacks
           
    def add_message_callback(self, cb, args=[]):
        """Set a callback for when messages arrive on this connection."""
        self.message_callbacks.append( (cb, args) )

    def remove_message_callback(self, cb):
        for fn, args in self.message_callbacks:
            if fn == cb:
                self.message_callbacks.remove( (fn, args) )
                break
    
    def add_disconnect_callback(self, cb, args=[]):
        """Set a callback for when this connection disconnects."""
        self.disconnect_callbacks.append( (cb, args) )
    
    def remove_disconnect_callback(self, cb):
        for fn, args in self.disconnect_callbacks:
            if fn == cb:
                self.disconnect_callbacks.remove( (fn, args) )
                break
    


    
class RevolvedHandler(object):
    """Handle Revolved connections.
    
    This must be created with a proper backend and auth_backend. It will
    listen for connection and disconnection notifications from CSP.
    """
    
    def __init__(self, csp, backend, auth_backend):
        self.csp = csp
        self.csp.set_internal_connect_cb(80, self.__csp_connect_cb)
        self.connections = []
        self.auth_backend = auth_backend
        self.backend = backend
    
    def __csp_connect_cb(self, conn):
        """Accept a new CSP connection and assign a RevolvedConnection to it."""
        conn.add_disconnect_callback(self.__csp_disconnect_cb)
        log.debug("Got CSP Connection")
        self.connections.append(RevolvedConnection(self, conn))
        
    def __csp_disconnect_cb(self, csp_conn):
        """Handle a CSPConnection Disconnection, removing the corresponding
        RevolvedConnection from the list of connections."""
        log.debug("Got CSP Disconnection")
        for conn in self.connections:
            if conn.csp_conn == csp_conn:
                self.connections.remove(conn)

class RevolvedConnection(object):
    """Handle one Revolved connection.
    
    When the user is authenticated (via an AUTH message), user_key will be
    their unique identifier; otherwise it will be None.
    """
    
    def __init__(self, handler, csp_conn):
        self.csp_conn = csp_conn
        self.csp_conn.add_disconnect_callback(self.__disconnect_cb)
        self.csp_conn.add_message_callback(self.__message_cb)
        self.backend = handler.backend
        self.auth_backend = handler.auth_backend
        self.user_key = None
        
    def __disconnect_cb(self, conn):
        log.debug("Revolved Disconnected")
        if self.user_key:
            self.backend.disconnect(self.user_key)
            self.user_key = None
    
    def send(self, obj):
        log.debug("Revolved SENDING: ", json.encode(obj))
        self.csp_conn.send(json.encode(obj))
    
    def send_ERR(self, msg_id, msg):
        """Send an error in response to msg_id."""
        self.send([msg_id, "ERR", [msg]])
        
    def send_OK(self, msg_id, msg=""):
        """Send an OK acknowledgement in response to msg_id."""
        self.send([msg_id, "OK", [msg]])
        
    def __message_cb(self, conn, msg):
        """Process Revolved Messages.
        
        Client-To-Server Messages:
            [msg_id, "AUTH", ["user_key", [opaquedata]]]
            [msg_id, "SUBSCRIBE", ["channel"]]
            [msg_id, "UNSUBSCRIBE", ["channel"]]
            [msg_id, "PUBLISH", ["channel", payload]]
            [msg_id, "SEND", ["recipient", payload]]
            [msg_id, "DISCONNECT", []]
        
        Server-To-Client Messages:
            [msg_id, "OK", ["reason"]]
            [msg_id, "ERR", ["reason"]]
            [0, "PUBLISH", [message]]
            
        """
        
        try:
            msg = json.decode(msg)
        except:
            log.warn("Invalid JSON message from ", conn, ": ", msg)
            self.send_ERR(0, "invalid json")
            return
        
        if len(msg) != 3:
            self.send_ERR(0, "invalid message format")
            return
        
        # Every frame will be a 3-tuple. The third item will be a list of arguments.
        msg_id, msg_type, args = msg
        log.debug("Got Revolved Message: %s %s %s" % (msg_id, msg_type, args))
        

        if msg_type == "AUTH":
            
            try:
                user_key, data = args
            except ValueError:
                self.send_ERR(msg_id, "invalid auth format")
                return
            
            can_connect = self.auth_backend.authorize_connect(user_key, data)
            if can_connect is True:
                can_connect = self.backend.connect(user_key)
            if can_connect is True:
                self.user_key = user_key
                self.send_OK(msg_id)
            else:
                # Send an error message
                can_connect = can_connect or "" # convert to string
                self.send_ERR(msg_id, can_connect)
        
        elif msg_type == "SUBSCRIBE":
            
            channels = args
            if type(channels) != type([]):
                self.send_ERR(msg_id, "channel names must be a list")
                return
            for channel in channels:
                permissions = self.auth_backend.authorize_channel(self.user_key, channel)
                if not permissions['subscribe']:
                    self.send_ERR(msg_id, "Not Authorized")
                    return
                subscribed = self.backend.subscribe(self.user_key, channel)
                
                if subscribed:
                    self.send_OK(msg_id)
                else:
                    self.send_ERR(msg_id, subscribed or "unable to subscribe to some channels")
            
        elif msg_type == "PUBLISH":
            
            try:
                channel, payload = args
            except ValueError:
                self.send_ERR("invalid publish format")
                return

            permissions = self.auth_backend.authorize_channel(self.user_key, channel)
            if not permissions['publish']:
                self.send_ERR(msg_id, "Not Authorized")
                return
                
            published = self.backend.publish(self.user_key, channel, payload)
            
            if published is True:
                self.send_OK(msg_id)
            else:
                self.send_ERR(msg_id, published or "unable to publish")

        elif msg_type == "SEND":
            
            try:
                recipient, payload = args
            except ValueError:
                self.send_ERR("invalid send format")
                return

            # TODO: No permissions check?
                
            sent = self.backend.send(self.user_key, recipient, payload)
            
            if sent is True:
                self.send_OK(msg_id)
            else:
                self.send_ERR(msg_id, sent or "unable to publish")
        
        elif msg_type == "DISCONNECT":
            
            # If we're connected to the backend, disconnect from it;
            # regardless, you must disconnect the CSP connection.
            if self.user_key:
                self.backend.disconnect(self.user_key)
                self.user_key = None
            self.csp_conn.disconnect()
        