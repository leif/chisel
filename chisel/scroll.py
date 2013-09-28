from twisted.internet import defer

from chisel import settings, crypto
from chisel import errors as e

class Policy(dict):
    pass

class ScrollUpdate(object):
    def __init__(self, content):
        self.content = content

class Scroll(object):
    """
    Persistent ordered set of fixed-size values.
    """
    def __init__(self, pyfs, scroll_id, value_size=20):
        self.pyfs = pyfs
        self.scroll_id = scroll_id
        self.state = settings.HASH( scroll_id )
        self.policy={}
        self._value_size = value_size
        self._value_set = set()
        self._value_list = []
        self._fh = self.pyfs.open(self.scroll_path, 'a+')
        while True:
            value = self._fh.read( value_size )
            if value == '':
                break
            assert len(value) == value_size, "bad scroll: short record"
            self._add(value)

    @property 
    def scroll_path(self):
        return "%s.scroll" % self.scroll_id

    @property
    def serial_number(self):
        return len(self._value_list)

    def __iter__(self):
        for item_hash in self._value_list:
            yield item_hash

    def slice(self, start, limit=1):
        """
        Returns list of items from the scroll.
        """
        return self._value_list[start:start+limit]

    def has(self, item_hash):
        return item_hash in self._value_set
    
    def _write(self, item_hash):
        self._fh.write(item_hash)
        self._fh.flush()

    def _add(self, item_hash):
        self._value_set.add(item_hash)
        self._value_list.append(item_hash)
        self.state = settings.HASH(self.state + item_hash)

    def add(self, item_hash):
        """
        Adds an entry to the scroll if it isn't already present.
        """
        if item_hash not in self._value_set:
            self._write(item_hash)
            self._add(item_hash)
            return True

class SignedScroll(Scroll, crypto.KeyStore):
    def __init__(self, pyfs, scroll_id, fingerprint):
        self.fingerprint = fingerprint
        super(SignedScroll, self).__init__(pyfs, scroll_id)

    @property
    def scroll_path(self):
        self.pyfs.makeopendir(self.scroll_id, recursive=True)
        return "%s/%s.scroll" % (self.scroll_id, self.fingerprint)

class LocalScroll(SignedScroll):
    def sign_update(self, update):
        signing_key = self.get_signing_key(self.fingerprint)

        signed_update = signing_key.sign(update)
        return signed_update

class RemoteScroll(SignedScroll):
    def verify_update(self, signed_update):
        verify_key = self.get_verify_key(self.fingerprint)

        update = verify_key.verify(signed_update)

        item_hash = update[:20]
        state = update[20:]
        next_state = settings.HASH(self.state + item_hash)
        if state != next_state:
            raise e.InconsistentState

        return update
