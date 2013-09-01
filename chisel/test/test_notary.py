import os
import hashlib
import random

import unittest

from chisel import settings
from chisel import notary, pool, scroll
from fs.opener import opener

twenty_bytes = 'A'*20
sha1_hexdigest = ''.join("%x" % (i%16) for i in range(40))

class TestChiselSet(unittest.TestCase):
    def test_add(self):
        my_data = "B"*20
        pyfs = opener.opendir(settings.config['fs_path'])
        scroll_id = sha1_hexdigest
        
        s = scroll.Scroll(pyfs, scroll_id)
        p = pool.Pool(pyfs)
        
        chisel_set = notary.ChiselSet(p, s)
        hash_bytes = chisel_set.add(my_data)

        self.assertEqual(p.get(hash_bytes), my_data)
        self.assertTrue(s.has(hash_bytes))

        self.assertTrue(chisel_set.has(my_data))

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
