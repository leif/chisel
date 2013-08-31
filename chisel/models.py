"""
AsymFs   - asymmetrically encrypted files
ScrollFs - stores files by hash, maintains ordered log of writes
"""
from chisel import errors as e
import hashlib

HASH = lambda s:hashlib.sha1(s).digest()

class Pool(object):
    """
    A scroll is an append-only unordered list of unique items.
    """
    def __init__(self, pyfs):
        self._pyfs = pyfs

    def put(self, obj):
        pass

class Policy(dict):
    pass

class Scroll(object):
    """
    Ordered set of item hashes.
    """
    def __init__(self, pyfs, scroll_id):
        self._pyfs = pyfs
        self.id = scroll_id
        self._data_set = set()
        self._data_list = []
        self.policy = {
            'value-size': 20,
            'signed': True,
            'valid-keys': [],
            'go-hard': True,
        }

    def save(self):
        scroll_content = ""
        for item_hash in self._data_list:
            scroll_content += item_hash
        self._pyfs.setcontents("%s.scroll" % self.id, scroll_content)

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
            self._data_list.append(item_hash)
            self._data_set.add(item_hash)
        else:
            raise e.ObjectAlreadyInPool

class Set(object):
    def __init__(self, pool, scroll):
        self.pool = pool
        self.scroll = scroll

    def __iter__(self):
        for item_hash in self.scroll:
            yield self.pool.get(item)

    def add(self, item):
        pass

    def has(self, item):
        item_hash = HASH(item)
        return self.scroll.has(item_hash)

class Notary(object):
    """
    A notary maintains one or more scrolls, keeping them up-to-date with
    corresponding scrolls maintained by other trustees.
    """
    def __init__(self, publisher):
        self.load_scrolls()
        self.publisher = publisher

    def receive_update(self, update):
        pass

    def publish_update(self, update):
        self.publisher.publish_update(update)

    def load_scrolls(self):
        self.scrolls = []
