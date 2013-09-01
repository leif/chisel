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
