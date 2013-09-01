import nacl.signing
import nacl.encoding
import nacl.secret

from chisel import settings
from chisel import errors as e

class ChiselSet(object):
    def __init__(self, pool, scroll):
        self.pool = pool
        self.scroll = scroll

    def __iter__(self):
        for item_hash in self.scroll:
            yield self.pool.get(item)

    def add(self, item):
        item_hash = settings.HASH(item)
        self.pool.put(item)
        self.scroll.add(item_hash)
        return item_hash

    def has(self, item):
        item_hash = settings.HASH(item)
        return self.scroll.has(item_hash)

class Notary(object):
    """
    A notary maintains one or more scrolls, keeping them up-to-date with
    corresponding scrolls maintained by other notaries.
    """
    def __init__(self, publisher, pyfs, fingerprint):
        self._pyfs = pyfs
        self.publisher = publisher
        self.fingerprint = fingerprint

        self.load_scrolls()
        self.load_keys()
    
    @classmethod
    def generate(cls, pyfs):
        skey = nacl.signing.SigningKey.generate()
        key_fingerprint = skey.verify_key.encode(nacl.encoding.HexEncoder)
        pyfs.setcontents("%s.skey" % key_fingerprint,
                         skey.encode(nacl.encoding.RawEncoder))
        return key_fingerprint

    def load_keys(self):
        skey = self._pyfs.getcontents("%s.skey" % self.fingerprint)
        self.signing_key = nacl.signing.SigningKey(skey)

    def load_scrolls(self):
        self.scrolls = []

    def receive_update(self, update):
        pass

    def publish_update(self, update):
        self.publisher.publish_update(update)
