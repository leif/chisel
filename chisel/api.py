import types

from cyclone import web, websocket, escape

from fs.opener import opener

from chisel import errors as e
from chisel import log, settings
from chisel import scroll, notary

class HTTPAPI(web.RequestHandler):
    notary = None

    def initialize(self):
        if not self.notary:
            log.warn("No notary is present.")

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

    def write_error(self, status_code, exception=None, **kw):
        self.set_status(status_code)
        error_message = 'generic-error'
        if exception.error_message:
            error_message = exception.error_message
        if exception:
            self.write({'error': error_message})

    def get(self):
        raise e.ResourceNotFound
    def post(self):
        raise e.ResourceNotFound
    def put(self):
        raise e.ResourceNotFound
    def head(self):
        raise e.ResourceNotFound

class SubscribeHandler(websocket.WebSocketHandler):
    @classmethod
    def publish_update(cls, update):
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
    def get_scroll(self, scroll_id):
        return scroll.Scroll(self.notary.pyfs, scroll_id)

class ScrollReadHandler(ScrollHandler):
    def get(self, scroll_id):
        scroll = self.get_scroll(scroll_id)
        limit = None
        try:
            start = int(self.get_argument('start'))
            limit = int(self.get_argument('limit'))
            items = scroll.slice(start, limit)
        except Exception as exc:
            print "No start provided"
            print exc
            items = list(scroll)

        self.write(items)

class ScrollListHandler(ScrollHandler):
    def get(self):
        scroll_list = []
        for cs_id, chisel_set in self.notary.chisel_sets.items():
            for peer_id, remote_scroll in chisel_set.peers.items():
                scroll_list.append({
                    'id': remote_scroll.id,
                    'peer_id': peer_id,
                    'state': remote_scroll.state.encode('hex'),
                    'policy': remote_scroll.policy,
                    # XXX should this flag be present or is it implicit in the peer_id?
                    'local': False
                })

            scroll_list.append({
                'id': chisel_set.scroll.id,
                'peer_id': self.notary.fingerprint,
                'state': chisel_set.scroll.state.encode('hex'),
                'policy': chisel_set.scroll.policy,
                'local': True
            })
        self.write(scroll_list)

    def post(self):
        """
        This shall create a new scroll based on the given request.

        XXX do we want to expose an API for creating new scrolls, or should we
        just allow the creation of new chisel sets? 
        ~ A.
        """
        pass

class ScrollPolicyHandler(ScrollHandler):
    def get(self, scroll_id):
        self.write(self.scroll.policy)

hash_regexp = '[0-9a-f]{40}'

def loadNotary():
    pyfs = opener.opendir(settings.config['fs_path'])
    chissel_set_id = 'spam'
    notary_fingerprint = notary.Notary.generate(pyfs)
    return notary.Notary(SubscribeHandler, pyfs, notary_fingerprint)

def notaryAPI(notary):
    HTTPAPI.notary = notary

    app = web.Application([

        (r'/chisel/scroll/(' + hash_regexp + ')/policy', ScrollPolicyHandler),
        (r'/chisel/scroll/(' + hash_regexp + ')', ScrollReadHandler),
        (r'/chisel/scroll', ScrollListHandler),

        (r'/chisel/item/(' + hash_regexp + ')', ItemRWHandler),
        (r'/chisel/item', ItemListHandler),
 
        (r'/chisel/subscribe', SubscribeHandler),
        (r'/.*', HTTPAPI),
    ])
    return app
