from twisted.internet import reactor
from twisted.trial import unittest

from chisel.api import loadNotary
from chisel import client

class End2EndTestCase(unittest.TestCase):
    def setUp(self):
        self.port = reactor.listenTCP(0, loadNotary(), interface="127.0.0.1")
        self.chiseld_port = self.port.getHost().port
        self.client = client.HTTPClient("http://127.0.0.1:%s" % self.chiseld_port)

    def tearDown(self):
        return self.port.stopListening()
