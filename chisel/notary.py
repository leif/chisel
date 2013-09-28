from chisel import settings, crypto
from chisel.scroll import LocalScroll
from chisel.pool import Pool
from chisel import errors as e

class ChiselSet(object):
    def __init__(self, pyfs, chisel_set_id, fingerprint):
        self.id = chisel_set_id
        self.pyfs = pyfs
        self.fingerprint = fingerprint
        self.peers = {}
        self._pending_item_requests = {}

        self.scroll = LocalScroll(pyfs, chisel_set_id, fingerprint)
        self.pool = Pool(pyfs)
    
    def add_peer(self, peer_id):
        self.peers[peer_id] = RemoteScroll(self.pyfs, self.scroll_id, peer_id)

    def __iter__(self):
        for item_hash in self.scroll:
            yield self.pool.get(item)
    
    def add(self, item):
        item_hash = settings.HASH(item)
        if not self.pool.has(item_hash):
            self.pool.put(item)
        if self.scroll.add(item_hash):
            return item_hash

    def has(self, item_hash):
        return self.scroll.has(item_hash)

class Notary(crypto.KeyStore):
    """
    A notary maintains one or more scrolls, keeping them up-to-date with
    corresponding scrolls maintained by other notaries.
    """
    def __init__(self, publisher, pyfs, fingerprint):
        self.pyfs = pyfs
        self.publisher = publisher
        self.fingerprint = fingerprint
        self.remote_pools = {}
        self.chisel_sets = {}
        self.verify_key = self.get_verify_key(self.fingerprint)
        self.signing_key = self.get_signing_key(self.fingerprint)

    def create_chisel_set(self, chisel_set_id):
        chisel_set = ChiselSet(self.pyfs, chisel_set_id, self.fingerprint)
        self.chisel_sets[chisel_set_id] = chisel_set
        return chisel_set

    def add_remote_pool(self, peer_id, pool):
        self.remote_pools[peer_id] = pool

    def fetch_item(self, item_hash, peer_id):
        pool = self.remote_pools[peer_id]
        if not item_hash in self._pending_item_requests:
            d = pool.get(item_hash)
            self._pending_item_requests[item_hash] = d

        d = self._pending_item_requests[item_hash]
        @d.addErrback
        def err(failure):
            failure.trap(e.PoolLookupFailed)
            self.failed_fetch(item_hash, peer_id)
            return self.fetch_item(item_hash, peer_id)
        return d

    def add(self, chisel_set_id, item):
        item_hash = self.chisel_sets[chisel_set_id].add(item)
        if item_hash:
            self.publish_update(chisel_set_id, item_hash)

    @classmethod
    def generate(cls, pyfs):
        signing_key = crypto.generate_signing_key()
        key_fingerprint = signing_key.verify_key.encode(crypto.HexEncoder)
        pyfs.setcontents(cls.skey % key_fingerprint,
                         signing_key.encode(crypto.RawEncoder))
        pyfs.setcontents(cls.vkey % key_fingerprint,
                         signing_key.verify_key.encode(crypto.RawEncoder))
        return key_fingerprint

    def invalid_update(self, scroll, update, exception):
        raise e.StreissandException

    def failed_fetch(self, item_hash, notary_fingerprint):
        print "Failed to fetch %s from %s" % (item_hash, notary_fingerprint)

    def receive_update(self, chisel_set_id, scroll, update):
        try:
            item_hash = scroll.verify_update(update)
            if not self.chisel_sets[chisel_set_id].has(item_hash):
                d = self.fetch_item(item_hash, scroll.fingerprint)
                @d.addCallback
                def cb(item):
                    self.add(item)

        except Exception as exception:
            self.invalid_update(scroll, update, exception)

    def publish_update(self, chisel_set_id, item_hash):
        update = item_hash + self.chisel_sets[chisel_set_id].scroll.state

        signed_update = self.chisel_sets[chisel_set_id].scroll.sign_update(update)
        self.publisher.publish_update(signed_update)
