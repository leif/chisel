import os
import hashlib
import random

import unittest

from chisel import settings
from chisel import models
from fs.opener import opener

def random_hash(length=40):
    return ''.join(random.choice('') for i in range(length))

def random_bytes(size=20):
    return ''.join(chr(random.randint(0, 255)) for i in range(size))

twenty_bytes = 'A'*20
sha1_hexdigest = ''.join("%x" % i%16) for i in range(40))

def hex_hash_int(i):
    return hashlib.sha1(str(i)).hexdigest()

def bytes_hash_int(i):
    return hashlib.sha1(str(i)).digest()

class TestScroll(unittest.TestCase):
    def setUp(self):
        try: os.unlink(sha1_hexdigest + ".scroll")
        except: pass

    def test_save_scroll(self):
        item_hash = twenty_bytes
        scroll_id = sha1_hexdigest
        pyfs = opener.opendir(settings.config['fs_path'])
        scroll = models.Scroll(pyfs, scroll_id)
        scroll.add(item_hash)
        self.assertTrue(scroll.has(item_hash))
        contents = pyfs.getcontents(scroll_id + '.scroll')
        self.assertEqual(contents, item_hash)

    def test_load_scroll(self):
        item_hash = twenty_bytes
        scroll_id = sha1_hexdigest
        pyfs = opener.opendir(settings.config['fs_path'])

        with open(scroll_id + '.scroll', 'w+') as f:
            f.write(item_hash)

        scroll = models.Scroll(pyfs, scroll_id)
        scroll.load()
        self.assertTrue(scroll.has(item_hash))
 
    def test_save_big_scroll(self):
        pyfs = opener.opendir(settings.config['fs_path'])
        scroll_id = sha1_hexdigest
        scroll = models.Scroll(pyfs, scroll_id)

        items = []
        for i in range(100):
            item_hash = bytes_hash_int(i)
            scroll.add(item_hash)
            items.append(item_hash)

        for item_hash in items:
            self.assertTrue(scroll.has(item_hash))

        contents = pyfs.getcontents(scroll_id + '.scroll')
        self.assertEqual(contents, ''.join(items))

    def test_slice(self):
        pyfs = opener.opendir(settings.config['fs_path'])
        scroll_id = sha1_hexdigest
        scroll = models.Scroll(pyfs, scroll_id)
        
        items = []
        for i in range(10):
            item_hash = bytes_hash_int(i)
            scroll.add(item_hash)
            items.append(item_hash)
        
        four, five = scroll.slice(4, 2)
        self.assertEqual(four, bytes_hash_int(4))
        self.assertEqual(five, bytes_hash_int(5))

class TestPool(unittest.TestCase):
    def test_put_get_pool(self):
        my_data = "B"*20
        scroll_id = sha1_hexdigest
        pyfs = opener.opendir(settings.config['fs_path'])
        pool = models.Pool(pyfs)
        hash_bytes = pool.put(my_data)
        self.assertEqual(pool.get(hash_bytes), my_data)

class TestChiselSet(unittest.TestCase):
    def test_add(self):
        my_data = "B"*20
        pyfs = opener.opendir(settings.config['fs_path'])
        scroll_id = sha1_hexdigest
        
        scroll = models.Scroll(pyfs, scroll_id)
        pool = models.Pool(pyfs)
        
        chisel_set = models.ChiselSet(pool, scroll)
        hash_bytes = chisel_set.add(my_data)

        self.assertEqual(pool.get(hash_bytes), my_data)
        self.assertTrue(scroll.has(hash_bytes))

        self.assertTrue(chisel_set.has(my_data))

class TestNotary(unittest.TestCase):
    def test_generate(self):
        pyfs = opener.opendir(settings.config['fs_path'])
        fingerprint = models.Notary.generate(pyfs)
        publisher = None
        notary = models.Notary(publisher, pyfs, fingerprint)

    def test_sign(self):
        pyfs = opener.opendir(settings.config['fs_path'])
        fingerprint = models.Notary.generate(pyfs)
        publisher = None
        notary = models.Notary(publisher, pyfs, fingerprint)

        signed_message = notary.signing_key.sign('aaaaaaaaa')
        verify_key = notary.signing_key.verify_key
        verify_key.verify(signed_message)
