from twisted.internet import defer
from chisel.test import e2e

class TestClientToNotary(e2e.End2EndTestCase):
    @defer.inlineCallbacks
    def test_get_invalid_resource(self):
        response = yield self.client.get('/spam')
        self.assertEqual(response, '{"error": "resource-not-found"}')

    @defer.inlineCallbacks
    def test_jget_invalid_resource(self):
        response = yield self.client.jget('/spam')
        self.assertEqual(response, {"error": "resource-not-found"})

