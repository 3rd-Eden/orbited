from dez.http.client import HTTPClientRequest, HTTPClient
from orbited.config import map as config
from orbited.logger import get_logger
from orbited.json import json
import urllib
log = get_logger("revolved")

options = config.get('revolved_plugin:http', {})
"""
[revolved_plugin:http]
callback.authorize_channel = http://localhost:4700/revolved_authorize_channel
callback.authorize_connect = http://localhost:4700/revolved_authorize_connect
cookies.enable = True
cookies.index = 0'
"""

auth_chan_url = config.get('callback.authorize_channel', None)
auth_conn_url = config.get('callback.authorize_connect', None)


auth_conn_url = "http://localhost:4700/revolved_auth_connect"
auth_chan_url = "http://localhost:4700/revolved_auth_channel"

#TODO: ensure that these are valid http urls

if False:
    auth_chan_url = None
    auth_conn_url = None
    
class RevolvedHTTPAuthBackend(object):
    """An open authorization backend for Revolved 
    """     
    
    def __init__(self):
        self.client = HTTPClient()
        
    def authorize_connect(self, user_key, data, cb, args=()):
        """Return True if the user can connect to Revolved.
        
        Otherwise, return a string with an error message.
        
        If user is None, the user will be treated as anonymous
        and rules will be checked for anonymous users instead.
        """
        # Make user_key a valid string, or None.
        if auth_conn_url:
            httpargs = (
                ('user_key', json.encode(user_key)),
                ('auth_data', json.encode(data))
            )
            
            self.client.get_url(auth_conn_url,
                 cb=self._conn_cb, 
                 cbargs=[cb, args],                 
                 body=urllib.urlencode(httpargs),
                method='POST'
            )
        else:
            return cb(False, *args)
                
    def _conn_cb(self, response, cb, args):
        print ('-a')
        print repr(response.body.get_value())
        try:
            result = json.decode(response.body.get_value())
            print 'a', repr(result)
            assert isinstance(result, bool)
        except:
            raise
            log.warn("Invalid http callback Response: %s" % response.body.get_value())
            return cb(False, *args)
        print 'cb(%s, %s)' % (result, args)
        return cb(result, *args)
    
        
    def authorize_channel(self, user_key, channel,cb, args=()):
        """Return a dictionary as follows, with information regarding the
        user's ability to publish and subscribe to the channel:
        
        { 'publish': True, 'subscribe': True }
        
        """
        # Make user_key a valid string, or None.
        if auth_chan_url:
            httpargs = (
                ('user_key', json.encode(user_key)),
            )
            
            self.client.get_url(auth_chan_url,
                 cb=self._chan_cb, 
                 cbargs=[cb, args],                 
                 body=urllib.urlencode(httpargs),
                method='POST'
            )
        else:
            return cb({ 'publish': False, 'subscribe': False }, *args)
    
    def _chan_cb(self, response, cb, args):
      
        try:
            result = json.decode(response.body.get_value())
            assert isinstance(result, dict)
            assert len(result.keys()) == 2
            assert 'publish' in result
            assert 'subscribe' in result
        except:
            raise
            log.warn("Invalid callback Response: %s" % response.bodyget_value())
            result = dict(publish=False, subscribe=False)
            
        return cb(result, *args)
    
    def authorize_send(self, sender_key, recipient_key, cb, args=()):
        if auth_send_url:
            pass
        else:
            return cb(False, *args)