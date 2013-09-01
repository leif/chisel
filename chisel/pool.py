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


