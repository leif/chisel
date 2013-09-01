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

class KeyStore(object):
    def get_keypair(self, fingerprint):
        skey = None
        pkey = None
        try:
            data = self._pyfs.getcontents("%s.skey" % self.fingerprint)
            skey = nacl.signing.SigningKey(data)
        except Exception as exc:
            # XXX make this exception handling more tight.
            pass

        try:
            data = self._pyfs.getcontents("%s.pkey" % self.fingerprint)
            pkey = nacl.signing.VerifyKey(data)
        except Exception as exc:
            # XXX make this exception handling more tight.
            pass
 
        return pkey, skey

class Notary(KeyStore):
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
        pyfs.setcontents("%s.pkey" % key_fingerprint,
                         skey.verify_key.encode(nacl.encoding.RawEncoder))
        return key_fingerprint

    def load_keys(self):
        self.public_key, self.signing_key = self.get_keypair(self.fingerprint)

    def load_scrolls(self):
        self.scrolls = []

    def invalid_update(self, scroll, update):
        raise e.StreissandException

    def receive_update(self, scroll, update):
        try:
            item_hash = scroll.verify_update(update)
            self.local_scroll.add(item_hash)
        except e.InvalidUpdateSignature:
            self.invalid_update(scroll, update)

    def publish_update(self, update):
        self.publisher.publish_update(update)
