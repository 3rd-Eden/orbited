class RevolvedOpenAuthBackend(object):
    """An open authorization backend for Revolved 
    """     
    
    def authorize_channel(self, user_key, channel,cb, args=()):
        """Return a dictionary as follows, with information regarding the
        user's ability to publish and subscribe to the channel:
        
        { 'publish': True, 'subscribe': True }
        
        """
        # Make user_key a valid string, or None.
        return cb({ 'publish': True, 'subscribe': True }, *args)
    
    def authorize_connect(self, user_key, data, cb, args=()):
        """Return True if the user can connect to Revolved.
        
        Otherwise, return a string with an error message.
        
        If user is None, the user will be treated as anonymous
        and rules will be checked for anonymous users instead.
        """
        # Make user_key a valid string, or None.
        return cb(True, *args)

    def authorize_send(self, sender_key, recipient_key, cb, args=()):
        return cb(True, *args)