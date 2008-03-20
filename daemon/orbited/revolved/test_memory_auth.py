from auth.memory import RevolvedMemoryAuthBackend
        
class TestRevolvedMemoryAuth(object):
    
    def setup(self):
        self.auth = RevolvedMemoryAuthBackend({
            'michael': {
                'password': 'michaelpass',
                'connect': True,
                'subscribe': True,
                'publish': ['orbited', 'comet'],
            },
            'mario': {
                'password': 'mariopass',
                'connect': True,
                'subscribe': ['orbited'],
                'publish': ['orbited'],
            },
            'marcus': {
                'connect': True,
                'subscribe': True,
                'publish': [],
            },
            # All other users
            None: {
                'connect': False,
                'subscribe': False,
                'publish': [],
            },
        })
        
    def test_authorize_channel(self):
        assert (self.auth.authorize_channel('michael', 'comet') ==
                    {'publish': True, 'subscribe': True})
        assert (self.auth.authorize_channel('mario', 'comet') ==
                    {'publish': False, 'subscribe': False})
        assert (self.auth.authorize_channel('marcus', 'comet') ==
                    {'publish': False, 'subscribe': True})
        assert (self.auth.authorize_channel('michael', 'orbited') ==
                    {'publish': True, 'subscribe': True})
        assert (self.auth.authorize_channel('mario', 'orbited') ==
                    {'publish': True, 'subscribe': True})
        assert (self.auth.authorize_channel('marcus', 'orbited') ==
                    {'publish': False, 'subscribe': True})
    
    def test_authorize_connect(self):
        assert self.auth.authorize_connect('michael', ['michaelpass']) is True
        assert self.auth.authorize_connect('mario', ['mariopass']) is True
        assert self.auth.authorize_connect('marcus') is True
        assert self.auth.authorize_connect('randomuser') is not True
        assert self.auth.authorize_connect(None) is not True
