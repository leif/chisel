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
