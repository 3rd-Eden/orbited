from log import setup
from orbited.config import map as config
logroot = setup(config)


def get_logger(name):
    return logroot.get_logger(name)