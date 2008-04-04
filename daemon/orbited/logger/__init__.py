from log import setup
from orbited.config import map as configmap

print 'AAAAAAAAAAEEEEEEEEEEEEEEEEee', configmap
print 'AAAAAAAAAAEEEEEEEEEEEEEEEEee'
logroot = setup(configmap)


def get_logger(name):
    return logroot.get_logger(name)