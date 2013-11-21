import os
import hashlib
import random

import unittest

from chisel import settings
from chisel import scroll, crypto
from fs.opener import opener

HASH = settings.HASH

def random_hash(length=40):
    return ''.join(random.choice('') for i in range(length))

def random_bytes(size=20):
    return ''.join(chr(random.randint(0, 255)) for i in range(size))

twenty_bytes = 'A'*20
sha1_hexdigest = ''.join("%x" % (i%16) for i in range(40))

def hex_hash_int(i):
    return hashlib.sha1(str(i)).hexdigest()

def HASH(i):
    return hashlib.sha1(str(i)).digest()

class TestScroll(unittest.TestCase):
    def setUp(self):
        try: os.unlink(sha1_hexdigest + ".scroll")
        except: pass

    def test_add_one(self):
        scroll_id = 'test_add'
        data1 = HASH( '1' )
        pyfs = opener.opendir(settings.config['fs_path'])
        s = scroll.Scroll(pyfs, scroll_id)
        s.add(data1)
        contents = pyfs.getcontents(scroll_id + '.scroll')
        self.assertEqual(contents, data1)

    def test_load_artificial(self):
        """
        This test writes its own scroll to test scroll loading
        """
        scroll_id = 'test_load'
        data1 = HASH( '2' )
        data2 = HASH( '3' )
        expected_state = HASH( HASH( HASH( scroll_id ) + data1 ) + data2 )
        pyfs = opener.opendir(settings.config['fs_path'])
        with open(scroll_id + '.scroll', 'w+') as f:
            f.write( data1 + data2 )
        with open(scroll_id + '.state', 'w') as f:
            f.write( expected_state )
        s = scroll.Scroll(pyfs, scroll_id)
        self.assertTrue(s.has(data1))
        self.assertTrue(s.has(data2))
        self.assertFalse(s.has('1'))
        self.assertFalse(s.has(''))
        self.assertEqual(s.state, expected_state)
 
    def test_add_many(self):
        pyfs = opener.opendir(settings.config['fs_path'])
        scroll_id = sha1_hexdigest
        s = scroll.Scroll(pyfs, scroll_id)

        items = []
        for i in range(100):
            item_hash = HASH(i)
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
            item_hash = HASH(i)
            s.add(item_hash)
            items.append(item_hash)
        
        four, five = s.slice(4, 2)
        self.assertEqual(four, HASH(4))
        self.assertEqual(five, HASH(5))

    def test_sign_local_scroll(self):
        pyfs = opener.opendir(settings.config['fs_path'])

        signing_key = crypto.generate_signing_key()
        scroll_id = sha1_hexdigest
        s = scroll.LocalScroll(pyfs, 
                               scroll_id, 
                               signing_key.verify_key.encode(crypto.HexEncoder))
        s.get_signing_key = lambda y: signing_key
        
        items = []
        for i in range(10):
            item_hash = HASH(i)
            s.add(item_hash)
            items.append(item_hash)

        update = s.state + item_hash
        signed_update = s.sign_update(update)

        four, five = s.slice(4, 2)
        self.assertEqual(four, HASH(4))
        self.assertEqual(five, HASH(5))

        self.assertEqual(signing_key.verify_key.verify(signed_update), update)

    def test_verify_remote_scroll(self):
        pyfs = opener.opendir(settings.config['fs_path'])

        signing_key = crypto.generate_signing_key()
        scroll_id = sha1_hexdigest
        s = scroll.RemoteScroll(pyfs, 
                               scroll_id, 
                               signing_key.verify_key.encode(crypto.HexEncoder))
        s.get_verify_key = lambda y: signing_key.verify_key
        
        items = []
        for i in range(10):
            item_hash = HASH(i)
            s.add(item_hash)
            items.append(item_hash)

        four, five = s.slice(4, 2)
        self.assertEqual(four, HASH(4))
        self.assertEqual(five, HASH(5))

        new_item_hash = HASH(i)
        new_state = HASH(s.state + new_item_hash)
        update = new_item_hash + new_state
        signed_update = signing_key.sign(update)

        self.assertEqual(s.verify_update(signed_update), update)
