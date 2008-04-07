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
from orbited.revolved.auth.open import RevolvedOpenAuthBackend
from orbited.revolved.auth.http import RevolvedHTTPAuthBackend
from orbited.revolved.backends.simple import SimpleRevolvedBackend
from orbited.revolved.dispatcher import RevolvedDispatcher
log = get_logger("revolved")
REVOLVED_PORT = 80
#######################################################################
# TODO: The Revolved dispatcher will need to handle calls to dispatcher.publish()
# in order to actually publish messages to clients. Everything else should be
# implemented.

class DummyCSPHandler(object):
    
    def __init__(self):
        self.connect_callbacks = {}
    
    def trigger_connection_made(self, port, conn):
        """Notify listeners of a new CSP Connection."""
        if port in self.connect_callbacks:
            cb, args = self.connect_callbacks[port]
            cb(conn, *args)
    
    # Callbacks
        
    def set_internal_connect_cb(self, port, cb, args=[]):
        self.connect_callbacks[port] = (cb, args)
    
#    def remove_connect_callback(self, cb):
#        for fn, args in self.connect_callbacks:
#            if fn == cb:
#                self.connect_callbacks.remove( (fn, args) )
#                break
                
class DummyCSPConnection(object):
    
    def __init__(self):
        self.disconnect_callback = (None, None)
        self.message_callback = (None, None)
    
    def send(self, data):
        """Send a message on this connection."""
        pass
    
    def close(self):
        self.trigger_disconnect()
    
    def trigger_disconnect(self):
        """Disconnect this connection."""
        # Triggered by the revolved connection upon a DISCONNECT message
        cb, args = self.disconnect_callback
        if cb:
            cb(self, *args)
        self.disconnect_callback = None, None
    # Callbacks
           
    def set_message_callback(self, cb, args=[]):
        """Set a callback for when messages arrive on this connection."""
        self.message_callback = cb, args
    
    def set_close_callback(self, cb, args=[]):
        """Set a callback for when this connection disconnects."""
        self.disconnect_callback = cb, args    
        
    def trigger_receive_message(self, msg):
        """Handle a received message."""
        cb, args = self.message_callback
        if cb:
            print 'cb:', cb
            print 'msg:', msg            
            cb(self, msg, *args)

        
    
class RevolvedHandler(object):
    """Handle Revolved connections.
    
    This must be created with a proper backend and auth_backend. It will
    listen for connection and disconnection notifications from CSP.
    """
    
    def __init__(self, app):
        self.app = app
        self.csp = app.csp
        self.csp.set_internal_connect_cb(REVOLVED_PORT, self.__csp_connect_cb)
        self.connections = []
        self.auth_backend = RevolvedHTTPAuthBackend()
        self.dispatcher = RevolvedDispatcher()
        self.backend = SimpleRevolvedBackend(self.dispatcher)
        
    def __csp_connect_cb(self, conn):
        """Accept a new CSP connection and assign a RevolvedConnection to it."""
#        conn.set_disconnect_callback(self.__csp_disconnect_cb)
        log.debug("Got CSP Connection")
        self.connections.append(RevolvedConnection(self, conn))
        
    def disconnect_cb(self, conn):
        """Handle a CSPConnection Disconnection, removing the corresponding
        RevolvedConnection from the list of connections."""
        log.debug("Got CSP Disconnection")
        if conn in self.connections:
            self.connections.remove(conn)

    def auth_cb(self, conn):
        self.dispatcher.connect(conn.user_key, conn)

class RevolvedConnection(object):
    """Handle one Revolved connection.
    
    When the user is authenticated (via an AUTH message), user_key will be
    their unique identifier; otherwise it will be None.
    """
    
    def __init__(self, handler, csp_conn):
        self.handler = handler
        self.csp_conn = csp_conn
        self.csp_conn.set_close_cb(self.__disconnect_cb)
        self.csp_conn.set_received_cb(self.__message_cb)
        self.backend = handler.backend
        self.auth_backend = handler.auth_backend
        self.user_key = None
        
    def __disconnect_cb(self, conn):
        log.debug("Revolved Disconnected")
        if self.user_key:
            self.backend.disconnect(self.user_key)
            self.user_key = None
        self.handler.disconnect_cb(self)
        
    def send(self, obj):
        log.debug("Revolved SENDING: ", json.encode(obj))
        self.csp_conn.send(json.encode(obj))
    
    def send_ERR(self, msg_id, info):
        """Send an error in response to msg_id."""
        self.send(["ERR", [msg_id, info]])
        
    def send_OK(self, msg_id):
        """Send an OK acknowledgement in response to msg_id."""
        self.send(["OK", [msg_id]])
        
    def __message_cb(self, msg):
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
            log.warn("Invalid JSON message from ", self.csp_conn, ": ", msg)
            self.send_ERR(0, "invalid json")
            return
        
        if len(msg) != 3:
            self.send_ERR(0, "invalid message format")
            return
        # Every frame will be a 3-tuple. The third item will be a list of arguments.
        msg_id, msg_type, args = msg
        log.debug("Got Revolved Message: %s %s %s" % (msg_id, msg_type, args))
        try:
            f = getattr(self, '_message_%s' % msg_type)
            f(msg_id, *args)
        # Note: may obscure unanticipated Attribute and Value Exceptions
        except AttributeError:
            return self.send_ERR        
        except ValueError:
            self.send_ERR(msg_id, "invalid message format")
        except Exception, e:
            self.send_ERR(msg_id, "unknown error: " + str(e))
            raise
        
    def _message_AUTH(self, msg_id, user_key, auth_data):
        self.auth_backend.authorize_connect(user_key, auth_data, self._AUTH_auth_cb, [msg_id, user_key])
            
    def _AUTH_auth_cb(self, msg_id, can_connect, user_key):
        if can_connect != True:
            can_connect = can_connect or "" # convert to string
            return self.send_ERR(msg_id, can_connect)
        
        self.backend.connect(user_key, self._AUTH_conn_cb, [msg_id, user_key])
        
    def _AUTH_conn_cb(self, connected, msg_id, user_key):
        if connected != True:
            return self.send_ERR(msg_id, "could not connect")
        self.user_key = user_key
        self.send_OK(msg_id)
        self.handler.auth_cb(self)
        
                
    def _message_SUBSCRIBE(self, msg_id, channel):
        permissions = self.auth_backend.authorize_channel(self.user_key, channel, self._SUBSCRIBE_auth_cb, [msg_id, channel])
            
    def _SUBSCRIBE_auth_cb(self, permissions, msg_id, channel):
      
        if not permissions['subscribe']:            
            return self.send_ERR(msg_id, "Not Authorized")

        self.backend.subscribe(self.user_key, channel, self._SUBSCRIBE_sub_cb, [msg_id])
            
    def _SUBSCRIBE_sub_cb(self, subscribed, msg_id):
        if subscribed == True:
            self.send_OK(msg_id)
        else:
            self.send_ERR(msg_id, subscribed)
                    
    def _message_UNSUBSCRIBE(self, msg_id, *channels):
        # TODO: Don't send multiple OKs for multiple channels
        for channel in channels:
            unsubscribed = self.backend.unsubscribe(self.user_key, channel)                
            if unsubscribed:
                self.send_OK(msg_id)
            else:
                self.send_ERR(msg_id, "unable to unsubscribe to some channels")
            
    def _message_PUBLISH(self, msg_id, channel, payload):
        log.info("_message_PUBLISH")
        self.auth_backend.authorize_channel(self.user_key, channel, self._PUBLISH_auth_cb, [msg_id, channel, payload])
        
    def _PUBLISH_auth_cb(self, permissions, msg_id, channel, payload):
        log.info("_PUBLISH_auth_cb")
        if not permissions['publish']:
            return self.send_ERR(msg_id, "Not Authorized")
            
        self.backend.publish(self.user_key, channel, payload, self._PUBLISH_pub_cb, [msg_id])
        
    def _PUBLISH_pub_cb(self, published, msg_id):
        log.info("_PUBLISH_pub_cb")
        
        if published == True:
            self.send_OK(msg_id)
        else:
            self.send_ERR(msg_id, published or "unable to publish")

    def _message_SEND(self, msg_id, recipient, payload):
        # TODO: No permissions check?
        self.auth_backend.authorize_send(self.user_key, recipient, self._SEND_auth_cb, [msg_id, recipient, payload])
        
    def _SEND_auth_cb(self, can_send, msg_id, recipient, payload):
        self.backend.send(self.user_key, recipient, payload, self._SEND_send_cb, [msg_id])
        
    def _SEND_send_cb(self, sent, msg_id):        
        if sent == True:
            self.send_OK(msg_id)
        else:
            self.send_ERR(msg_id, sent or "unable to publish")
        
    def _message_DISCONNECT(self, msg_id):
        # If we're connected to the backend, disconnect from it;
        # regardless, you must disconnect the CSP connection.
        # TODO: what if we've issued a backend.connect, but haven't yet connected?
        if self.user_key:
            self.backend.disconnect(self.user_key)
            self.user_key = None
        self.csp_conn.close()
        