"""
AsymFs   - asymmetrically encrypted files
ScrollFs - stores files by hash, maintains ordered log of writes
"""
from chisel import errors as e
import hashlib

HASH = lambda s:hashlib.sha1(s).hexdigest()

class Pool(object):
    """
    A scroll is an append-only unordered list of unique items.
    """
    def __init__(self, pyfs):
        self._pyfs = pyfs

    def put(self, obj):
        pass

class Scroll(object):
    """
    Ordered set of item hashes.
    """
    def __init__(self, pyfs):
        self._pyfs = pyfs
        self._data_set = set()
        self._data_list = []

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

class Directory(Scroll):
    pass

class Trustee(object):
    """
    A trustee maintains one or more scrolls, keeping them up-to-date with
    corresponding scrolls maintained by other trustees.
    """
    pass

class Directory(Scroll):
    pass

