import os
import hashlib
import random

import unittest

from chisel import settings
from chisel import notary, pool, scroll
from fs.opener import opener

HASH = settings.HASH

twenty_bytes = 'A'*20
sha1_hexdigest = ''.join("%x" % (i%16) for i in range(40))

class TestChiselSet(unittest.TestCase):
    def test_add(self):
        my_data = "B"*20
        pyfs = opener.opendir(settings.config['fs_path'])
        scroll_id = sha1_hexdigest

        chissel_set_id = 'spam'

        fingerprint = notary.Notary.generate(pyfs)
        
        chisel_set = notary.ChiselSet(pyfs, chissel_set_id, fingerprint)
        self.assertTrue( chisel_set.add(my_data)) # added
        self.assertFalse(chisel_set.add(my_data)) # this time it was already there
        self.assertTrue(chisel_set.scroll.has(HASH(my_data)))
        self.assertTrue(chisel_set.has(HASH(my_data)))

class TestNotary(unittest.TestCase):
    def test_generate(self):
        pyfs = opener.opendir(settings.config['fs_path'])
        fingerprint = notary.Notary.generate(pyfs)
        publisher = None
        n = notary.Notary(publisher, pyfs, fingerprint)

    def test_sign(self):
        my_message = 'Do it Like La La La!'
        pyfs = opener.opendir(settings.config['fs_path'])
        fingerprint = notary.Notary.generate(pyfs)
        publisher = None
        n = notary.Notary(publisher, pyfs, fingerprint)

        signed_message = n.signing_key.sign(my_message)
        verify_key = n.signing_key.verify_key
        self.assertEqual(verify_key.verify(signed_message), my_message)

    def test_receive_update(self):
        pass

    def test_publish_update(self):
        pass

