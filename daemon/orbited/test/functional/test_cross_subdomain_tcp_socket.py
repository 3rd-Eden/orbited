from selenium import selenium
import time, re

from orbited.test.functional import TCPSocketTestCase

class TestCrossSubdomainTCPSocket(TCPSocketTestCase):
    domain = "www.orbited"
    label = "Cross-Subdomain"

