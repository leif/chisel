"""
AsymFs   - asymmetrically encrypted files
ScrollFs - stores files by hash, maintains ordered log of writes
"""
import nacl.signing
import nacl.encoding
import nacl.secret

from chisel import settings
from chisel import errors as e

class Pool(object):
    """
    Simple content-addressable data store.
    """
    def __init__(self, pyfs):
        self._pyfs = pyfs

    def _get_dir(self, hash_bytes):
        assert len(hash_bytes) == settings.HASH_LENGTH
        hex_string = hash_bytes.encode('hex')
        dir_path = "%s/%s" % (hex_string[0:2], hex_string[2:4])
        return self._pyfs.makeopendir(dir_path, recursive=True)

    def put(self, data):
        hash_bytes = settings.HASH(data)
        self._get_dir(hash_bytes).setcontents(hash_bytes.encode('hex'), data)
        return hash_bytes

    def get(self, hash_bytes):
        return self._get_dir(hash_bytes).getcontents(hash_bytes.encode('hex'))

class Policy(dict):
    pass

class Scroll(object):
    """
    Ordered set of item hashes.
    """
    def __init__(self, pyfs, scroll_id):
        self.policy = {
            'value-size': 20,
            'signed': True,
            'valid-keys': [],
            'go-hard': True,
        }
        self._pyfs = pyfs
        self.id = scroll_id
        self._data_set = set()
        self._data_list = []
        self.state = scroll_id
        # XXX this is a blocking call
        self._fh = self._pyfs.open("%s.scroll" % scroll_id, 'a+')
    
    @property
    def serial_number(self):
        return len(self._data_list)

    def load(self):
        scroll_content = self._pyfs.getcontents("%s.scroll" % self.id)
        value_size = self.policy['value-size']
        assert len(scroll_content) % value_size == 0
        for i in range(len(scroll_content)/value_size):
            item_hash = scroll_content[value_size*i:value_size*(i+1)]
            self._data_set.add(item_hash)
            self._data_list.append(item_hash)

    def __iter__(self):
        for item_hash in self._data_list:
            yield item_hash

    def slice(self, start, limit=1):
        """
        Returns list of items from the scroll.
        """
        return self._data_list[start:start+limit]

    def has(self, item_hash):
        return item_hash in self._data_set
    
    def add(self, item_hash):
        """
        Adds an entry to the scroll if it isn't already present.
        """
        if item_hash not in self._data_set:
            assert self.policy['go-hard']

            self._fh.write(item_hash)
            self._fh.flush()

            self._data_set.add(item_hash)
            self._data_list.append(item_hash)

            self.state = settings.HASH(self.state + item_hash)
        else:
            raise e.ObjectAlreadyInPool

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
    corresponding scrolls maintained by other trustees.
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
