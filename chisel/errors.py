from cyclone.web import HTTPError

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


class APIError(HTTPError):
    error_message = 'api-error'

    def __init__(self):
        self.log_message = self.error_message

class ResourceNotFound(APIError):
    status_code = 404
    error_message = 'resource-not-found'
