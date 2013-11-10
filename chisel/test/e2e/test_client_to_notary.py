from twisted.internet import reactor, defer
from twisted.trial import unittest

from chisel.api import loadNotary, notaryAPI
from chisel import client

class TestServer(object):
    def __init__(self):
        self.notary = loadNotary()
        self.api = notaryAPI(self.notary)
        self.listeningPort = reactor.listenTCP(0, self.api, interface="127.0.0.1")
        self.chiseld_port = self.listeningPort.getHost().port
        self.client = client.HTTPClient("http://127.0.0.1:%s" % self.chiseld_port)


class TestClientToNotary(unittest.TestCase):

    def setUp(self):
        self.server = TestServer()

    def tearDown(self):
        return self.server.listeningPort.stopListening()

    @defer.inlineCallbacks
    def test_get_invalid_resource(self):
        response = yield self.server.client.get('/spam')
        self.assertEqual(response, '{"error": "resource-not-found"}')

    @defer.inlineCallbacks
    def test_jget_invalid_resource(self):
        response = yield self.server.client.jget('/spam')
        self.assertEqual(response, {"error": "resource-not-found"})

    @defer.inlineCallbacks
    def test_list_scrolls(self):
        chisel_set_id = 'ham'
        my_data = 'spam'*20
        self.server.notary.create_chisel_set(chisel_set_id)
        self.server.notary.add(chisel_set_id, my_data)
        scrolls = yield self.server.client.jget('/chisel/scroll')
        scroll = scrolls[0]
        self.assertEqual(scroll['state'], 'ccc8f578e0faadef5b2135a81e3bbc592ac4d04e')
        self.assertEqual(scroll['peer_id'], self.server.notary.fingerprint)
        self.assertEqual(scroll['id'], chisel_set_id)

