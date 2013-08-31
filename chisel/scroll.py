#!/usr/bin/python

"""
AsymFs   - asymmetrically encrypted files
ScrollFs - stores files by hash, maintains ordered log of writes
"""

import hashlib

class ScrollWriteError(Exception): pass
class ScrollReadError(Exception): pass

HASH = lambda s:hashlib.sha1(s).hexdigest()

class Scroll(object):

    """
    A scroll is an append-only list of unique items.
    """
    def __init__(self, pyfs):
        self._pyfs = pyfs
        self._data_list = []
        self._data_set = set()
        if 'writer_id' in self._pyfs._listdir():
            raise ScrollWriteError('scroll is already open for writing')
        else:
            self._pyfs.setcontents( 'writer_id', writer_id

    def put(self, obj):
        """
        Adds an entry to the scroll if it isn't already present.
        """
        value = HASH(obj)
        if value not in self._data_set:
            self._data_list.append(value)
            self._data_set.add(value)
            return True
        return False

    def get_log(self, start, limit=1 ):
        """
        Returns list of items from the scroll.
        """
        return self._data_list[ start : start+limit ]

class AsymFs(object):
    """
    Filesystem which asymmetrically encrypts files as they are written.
    """

class Trustee(object):
    """
    A trustee maintains one or more scrolls, keeping them up-to-date with
    corresponding scrolls maintained by other trustees.
    """
    pass
