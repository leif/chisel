import unittest

from chisel import settings
from chisel import pool
from fs.opener import opener

twenty_bytes = 'A'*20
sha1_hexdigest = ''.join("%x" % (i%16) for i in range(40))

class TestPool(unittest.TestCase):
    def test_put_get_pool(self):
        my_data = "B"*20
        scroll_id = sha1_hexdigest
        pyfs = opener.opendir(settings.config['fs_path'])
        p = pool.Pool(pyfs)
        hash_bytes = p.put(my_data)
        self.assertEqual(p.get(hash_bytes), my_data)

