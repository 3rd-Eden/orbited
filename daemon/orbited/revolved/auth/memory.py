class RevolvedMemoryAuthBackend(object):
    """A simple memory-based backend for Revolved Authorization, using
    a username and password combination.
    
    Initialize this with a user_config object in the following form:
    
    {
        'username': {
            'password': 'foo',
            'connect': True,
            'publish': True,
            'subscribe: ['channel1', 'channel2']
        },
        'username2': {
            'password': 'foo',
            'connect': True,
            'publish': ['channel1'],
            'subscribe: ['channel1', 'channel2']
        },
        None: {
            'connect': False,
            'subscribe': False,
            'publish': [],
        },
    }
    
    Each user can be authorized to CONNECT via a simple boolean.
    Publish and Subscribe privileges can either be given carte-blanche
    via a simple boolean, or can be a list of channel names allowed.
    
    If a username of None (the python type, not a string) is provided, it
    will be used to determine privileges anonymous access. If no rules are
    provided, users will be denied by default.
    """     
    
    def __init__(self, user_config):
        self.users = user_config
    
    def authorize_channel(self, user_key, channel):
        """Return a dictionary as follows, with information regarding the
        user's ability to publish and subscribe to the channel:
        
        { 'publish': True, 'subscribe': True }
        
        """
        if user_key not in self.users:
            user_key = None
        try:
            auth_info = self.users[user_key]
        except KeyError:
            # No rules defined for unknown users
            return {'publish': False, 'subscribe': False}
        
        return {
            'publish': (auth_info['publish'] is True 
                            or channel in auth_info['publish']),
            'subscribe': (auth_info['subscribe'] is True 
                            or channel in auth_info['subscribe'])
        }
    
    def authorize_connect(self, user_key, data=""):
        """Return True if the user can connect to Revolved, False otherwise.
        
        If user is None, the user will be treated as anonymous
        and rules will be checked for anonymous users instead.
        """
        if user_key not in self.users:
            user_key = None
        try:
            auth_info = self.users[user_key]
        except KeyError:
            # No rules defined for anonymous users
            return False
        
        # Interpret data as a password
        password = data
        if 'password' in auth_info and auth_info['password'] != password:
            return False
            
        return auth_info['connect']