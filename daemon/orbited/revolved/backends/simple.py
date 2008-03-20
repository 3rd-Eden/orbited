class SimpleRevolvedBackend(object):
    """Simple interface for a publish/subscribe backend.
    
    This backend only implements a simple publish/subscribe backend with
    local (i.e. non-replicated) groups, on a single node.
    """
    
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.users = {} # Mapping of users to a list subscribed channels
        self.channels = {} # Mapping of channels to a list of users

    def connect(self, user):
        """Connect a user to Revolved."""
        self.users[user] = [] # Start without any subscriptions
    
    def disconnect(self, user):
        """Handle a disconnection from a revolved user, removing them from
        all subscriptions.
        
        If the user is not connected, do nothing.
        """
        if user not in self.users:
            return
            
        for channel in self.users[user]:
            self.unsubscribe(user, channel)
        del self.users[user]
        
    def send(self, sender, recipient, payload):
        """Send a payload to another revolved user.
        
        If the sender or receiver don't exist, do nothing.
        """
        if sender not in self.users or recipient not in self.users:
            return
        self.dispatcher.send(sender, recipient, payload)
        
    def publish(self, publisher, channel, payload):
        """Publish a payload to a channel on behalf of a revolved user.
        
        If the channel does not exist, do nothing.
        """
        if channel in self.channels:
            for user in self.channels[channel]:
                self.dispatcher.publish(user, channel, payload)
        
    def subscribe(self, subscriber, channel):
        """Subscribe the revolved user to a channel.
        
        If the channel does not exist, create it.
        If the user is already subscribed, do nothing.
        If the user is not connected, do nothing.
        """
        if subscriber not in self.users:
            return
        if channel not in self.users[subscriber]:
            self.users[subscriber].append(channel)
            if channel not in self.channels:
                self.channels[channel] = []
            self.channels[channel].append(subscriber)
        
    def unsubscribe(self, user, channel):
        """Unsubscribe the revolved user from a channel.
        
        If the user is not subscribed to the channel, do nothing.
        """
        if channel in self.users[user]:
            self.users[user].remove(channel)
            self.channels[channel].remove(user)
    
    def move(self, old_user, new_user):
        """Rename a user, transferring all old subscriptions to the
        new username and removing the old user.
        """
        if old_user not in self.users:
            return
        self.users[new_user] = []
        for channel in self.users[old_user]:
            self.channels[channel].remove(old_user)
            self.channels[channel].append(new_user)
            self.users[new_user].append(channel)
        del self.users[old_user]
    
    #----------------------------------------------------------------------
    # Utility functions for testing
    
    def list_subscriptions(self, user):
        if user in self.users:
            return self.users[user]
        else:
            return None
            
    def list_channels(self):
        return self.channels.keys()
        
    def list_users(self):
        return self.users.keys()
               
    def is_user_in_channel(self, channel, user):
        if channel in self.channels and user in self.channels[channel]:
            return True
        else:
            return False