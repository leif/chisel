from chisel import settings
from chisel import errors as e

class Pool(object):
    """
    Simple content-addressable data store.
    """
    def __init__(self, pyfs):
        self._pyfs = pyfs

    def _get_dir(self, item_hash):
        assert len(item_hash) == settings.HASH_LENGTH
        hex_string = item_hash.encode('hex')
        dir_path = "%s/%s" % (hex_string[0:2], hex_string[2:4])
        return self._pyfs.makeopendir(dir_path, recursive=True)

    def put(self, item):
        item_hash = settings.HASH(item)
        self._get_dir(item_hash).setcontents(item_hash.encode('hex'), item)
        return item_hash

    def get(self, item_hash):
        return self._get_dir(item_hash).getcontents(item_hash.encode('hex'))

class RemotePool(object):
    def __init__(self, peer_id):
        self.peer_id = peer_id

    def get(self, item_hash):
        pass

