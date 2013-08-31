import hashlib

class Config(dict):
    pass

HASH = lambda s:hashlib.sha1(s).digest()
HASH_LENGTH = 20

config = Config()
config['fs_path'] = "."
