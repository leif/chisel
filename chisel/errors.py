class ScrollError(Exception):
    pass

class ScrollWriteError(ScrollError):
    pass

class ScrollReadError(ScrollError):
    pass

class PoolError(Exception):
    pass

class ObjectAlreadyInPool(PoolError):
    pass

class InconsistentState(ScrollError):
    pass

class StreissandException(ScrollError):
    pass

class SignatureError(Exception):
    pass

class InvalidUpdateSignature(SignatureError):
    pass

class PoolLookupFailed(Exception):
    def __init__(self, item_hash, peer_id):
        self.item_hash = item_hash
        self.peer_id = peer_id
