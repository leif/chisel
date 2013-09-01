import os
import hashlib
import random

import unittest

from chisel import settings
from chisel import scroll
from fs.opener import opener

def random_hash(length=40):
    return ''.join(random.choice('') for i in range(length))

def random_bytes(size=20):
    return ''.join(chr(random.randint(0, 255)) for i in range(size))

twenty_bytes = 'A'*20
sha1_hexdigest = ''.join("%x" % (i%16) for i in range(40))

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
        s = scroll.Scroll(pyfs, scroll_id)
        s.add(item_hash)
        self.assertTrue(s.has(item_hash))
        contents = pyfs.getcontents(scroll_id + '.scroll')
        self.assertEqual(contents, item_hash)

    def test_load_scroll(self):
        item_hash = twenty_bytes
        scroll_id = sha1_hexdigest
        pyfs = opener.opendir(settings.config['fs_path'])

        with open(scroll_id + '.scroll', 'w+') as f:
            f.write(item_hash)

        s = scroll.Scroll(pyfs, scroll_id)
        s.load()
        self.assertTrue(s.has(item_hash))
 
    def test_save_big_scroll(self):
        pyfs = opener.opendir(settings.config['fs_path'])
        scroll_id = sha1_hexdigest
        s = scroll.Scroll(pyfs, scroll_id)

        items = []
        for i in range(100):
            item_hash = bytes_hash_int(i)
            s.add(item_hash)
            items.append(item_hash)

        for item_hash in items:
            self.assertTrue(s.has(item_hash))

        contents = pyfs.getcontents(scroll_id + '.scroll')
        self.assertEqual(contents, ''.join(items))

    def test_slice(self):
        pyfs = opener.opendir(settings.config['fs_path'])
        scroll_id = sha1_hexdigest
        s = scroll.Scroll(pyfs, scroll_id)
        
        items = []
        for i in range(10):
            item_hash = bytes_hash_int(i)
            s.add(item_hash)
            items.append(item_hash)
        
        four, five = s.slice(4, 2)
        self.assertEqual(four, bytes_hash_int(4))
        self.assertEqual(five, bytes_hash_int(5))

