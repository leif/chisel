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

    @defer.inlineCallbacks
    def test_list_scrolls(self):
        chisel_set_id = 'ham'
        my_data = 'spam'*20
        self.notary.create_chisel_set(chisel_set_id)
        self.notary.add(chisel_set_id, my_data)

        scrolls = yield self.client.jget('/chisel/scroll')
        scroll = scrolls[0] 
        self.assertEqual(scroll['state'], '7e5ca50fc95df01fe265fae4fa00d5e700e3c593')
        self.assertEqual(scroll['peer_id'], self.notary.fingerprint)
        self.assertEqual(scroll['id'], chisel_set_id)
