import types

from cyclone import web, websocket, escape

from chisel import models

class HTTPAPI(web.RequestHandler):
    def write(self, chunk):
        """
        This is a monkey patch to RequestHandler to allow us to serialize also
        json list objects.
        """
        if isinstance(chunk, types.ListType):
            chunk = escape.json_encode(chunk)
            super(HTTPAPI, self).write(chunk)
            self.set_header("Content-Type", "application/json")
        else:
            super(HTTPAPI, self).write(chunk)

class SubscribeHandler(websocket.WebSocketHandler):
    def publish_update(self, update):
        pass

class ItemListHandler(HTTPAPI):
    pass

class ItemRWHandler(HTTPAPI):
    def put(self, hash_id):
        pass
    
    def get(self, hash_id):
        pass

    def head(self, hash_id):
        pass

class ScrollHandler(HTTPAPI):
    def initialize(self):
        pyfs = None
        self.scroll = models.Scroll(pyfs)

class ScrollListHandler(ScrollHandler):
    def get(self):
        limit = None
        try:
            start = int(self.get_argument('start'))
            limit = int(self.get_argument('limit'))
            items = self.scroll.slice(start, limit)
        except Exception as exc:
            print "No start provided"
            print exc
            items = list(self.scroll)

        self.write(items)

class ScrollPolicyHandler(ScrollHandler):
    def get(self):
        self.write(self.scroll.policy)


hash_regexp = '[0-9a-f]{40}'

spec = [
    (r'/item/(' + hash_regexp + ')', ItemRWHandler),
    (r'/item', ItemListHandler),
    
    (r'/scroll/(' + hash_regexp + ')/policy', ScrollPolicyHandler),
    (r'/scroll/(' + hash_regexp + ')', ScrollListHandler),

    (r'/subscribe', SubscribeHandler),

]


