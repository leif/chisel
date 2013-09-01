from chisel import settings, crypto
from chisel.scroll import LocalScroll
from chisel.pool import Pool
from chisel import errors as e

class ChiselSet(object):
    def __init__(self, pyfs, chisel_set_id, fingerprint):
        self.scroll = LocalScroll(pyfs, chisel_set_id, fingerprint)
        self.pool = Pool(pyfs)
        self.remote_scrolls = []
    
    def add_remote_scroll(self, remote_scroll):
        self.remote_scrolls.append(remote_scroll)

    def __iter__(self):
        for item_hash in self.scroll:
            yield self.pool.get(item)

    def add(self, item):
        item_hash = settings.HASH(item)
        self.pool.put(item)
        self.scroll.add(item_hash)
        return item_hash

    def has(self, item_hash):
        #item_hash = settings.HASH(item)
        return self.scroll.has(item_hash)

class Notary(crypto.KeyStore):
    """
    A notary maintains one or more scrolls, keeping them up-to-date with
    corresponding scrolls maintained by other notaries.
    """
    def __init__(self, publisher, pyfs, fingerprint):
        self._pyfs = pyfs
        self.publisher = publisher
        self.fingerprint = fingerprint

        self.load_keys()
   
    def create_chisel_set(self, chisel_set_id):
        self.chisel_set = ChiselSet(self._pyfs, chisel_set_id, self.fingerprint)

    def add(self, item):
        item_hash = self.chisel_set.add(item)
        self.publish_update(item_hash)

    @classmethod
    def generate(cls, pyfs):
        signing_key = crypto.generate_signing_key()
        key_fingerprint = signing_key.verify_key.encode(crypto.HexEncoder)
        pyfs.setcontents(cls.skey % key_fingerprint,
                         signing_key.encode(crypto.RawEncoder))
        pyfs.setcontents(cls.vkey % key_fingerprint,
                         signing_key.verify_key.encode(crypto.RawEncoder))
        return key_fingerprint

    def load_keys(self):
        self.verify_key = self.get_verify_key(self.fingerprint)
        self.signing_key = self.get_signing_key(self.fingerprint)

    def invalid_update(self, scroll, update, exception):
        raise e.StreissandException

    def receive_update(self, scroll, update):
        try:
            item_hash = scroll.verify_update(update)
            if not self.chisel_set.has(item_hash):
                d = scroll.fetch_item(item_hash)
                @d.addCallback
                def cb(result):
                    self.add(item)
        except Exception as exception:
            self.invalid_update(scroll, update, exception)

    def publish_update(self, item_hash):
        update = item_hash + self.chisel_set.scroll.state

        signed_update = self.chisel_set.scroll.sign_update(update)
        self.publisher.publish_update(signed_update)
