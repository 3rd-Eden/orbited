from backends.simple import SimpleRevolvedBackend

class RevolvedDispatcherPlaceholder(object):
    """Provides a simple layer of abstraction between Revolved Backends and
    the Orbited server. Tracks mappings of revolved users to orbited keys...
    """
    
    def __init__(self):
        self.sent_messages = []
        self.published_messages = {}
    
    def send(self, sender, recipient, payload):
        """Send a message to the Revolved user."""
        self.sent_messages.append( [sender, recipient, payload] )
    
    def publish(self, recipient, channel, payload):
        """Send a message to a recipient with the specified channel."""
        if channel not in self.published_messages:
            self.published_messages[channel] = []
        self.published_messages[channel].append([recipient, channel, payload])

class TestRevolvedBackend(object):
    
    def setup(self):
        self.comm = RevolvedDispatcherPlaceholder()
        self.backend = SimpleRevolvedBackend(self.comm)
    
    def test_connections(self):
        assert self.backend.list_users() == []
        assert self.backend.list_subscriptions("marcus") == None
        self.backend.connect("marcus")
        self.backend.connect("mario")
        self.backend.connect("michael")
        assert "marcus" in self.backend.list_users()
        assert self.backend.list_subscriptions("marcus") == []
        self.backend.disconnect("mario")
        self.backend.disconnect("michael")
        assert self.backend.list_users() == ["marcus"]
        assert self.backend.list_subscriptions("marcus") == []

    def test_subscribe(self):
        self.backend.connect("marcus")
        # subscribing twice should be acceptable (do nothing)
        self.backend.subscribe("marcus", "cartoon_network")
        self.backend.subscribe("marcus", "cartoon_network")
        self.backend.subscribe("marcus", "msnbc")
        subscriptions = self.backend.list_subscriptions("marcus")
        subscriptions.sort() # make sure these are in the same order
        assert subscriptions == ["cartoon_network", "msnbc"]
        
    def test_unsubscribe(self):
        self.backend.connect("marcus")
        self.backend.subscribe("marcus", "cartoon_network")
        self.backend.subscribe("marcus", "msnbc")
        self.backend.subscribe("marcus", "comedy_central")
        self.backend.unsubscribe("marcus", "msnbc")
        
        subscriptions = self.backend.list_subscriptions("marcus")
        subscriptions.sort() # make sure these are in the same order
        assert subscriptions == ["cartoon_network", "comedy_central"]
    
    def test_move(self):
        self.backend.connect("bill_gates")
        self.backend.subscribe("bill_gates", "microsoft")
        assert self.backend.list_users() == ["bill_gates"]
        self.backend.move("bill_gates", "steve_jobs")
        assert self.backend.list_users() == ["steve_jobs"]
        assert self.backend.list_subscriptions("steve_jobs") == ["microsoft"]
    
    def test_publish(self):
        self.backend.connect("bill_gates")
        self.backend.connect("steve_ballmer")
        # publishing to a nonexistent channel should do nothing
        self.backend.publish("bill_gates", "good_software", "payload")
        assert "good_software" not in self.comm.published_messages
        # publish to a subscribed channel
        self.backend.subscribe("bill_gates", "good_software")
        self.backend.subscribe("bill_gates", "bloated_software")
        self.backend.subscribe("steve_ballmer", "bloated_software")
        self.backend.publish("bill_gates", "bloated_software", "payload")
        assert "good_software" not in self.comm.published_messages
        # Published to both steve_ballmer and bill_gates, so total is 2
        assert len(self.comm.published_messages["bloated_software"]) == 2
    
    def test_send(self):
        self.backend.connect("bill_gates")
        self.backend.connect("steve_ballmer")
        self.backend.connect("linus_torvalds")
        self.backend.send("bill_gates", "steve_ballmer", "vista")
        self.backend.send("steve_ballmer", "linus_torvalds", "opensource")
        assert len(self.comm.sent_messages) == 2
    
    # Now, test the unusual edge cases
    
    def test_subscribe_nonexistent_user(self):
        self.backend.subscribe("marcus", "msnbc")
        assert self.backend.list_subscriptions("marcus") == None

    def test_subscribe_and_disconnect(self):
        self.backend.connect("marcus")
        # subscribing twice should be acceptable (do nothing)
        self.backend.subscribe("marcus", "cartoon_network")
        self.backend.subscribe("marcus", "cartoon_network")
        self.backend.subscribe("marcus", "msnbc")
        self.backend.disconnect("marcus")
        self.backend.disconnect("nonexistent_user") # Should do nothing.
        assert self.backend.list_subscriptions("marcus") == None