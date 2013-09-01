from zope.interface import implementer

from twisted.internet import reactor
from twisted.web import client, iweb

class NotarySubscriber(object):
    pass

@implementer(iweb.IBodyProducer)
class StringProducer(object):

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass

class HTTPClient(object):
    def __init__(self, socks_proxy=None):
        """
        Args:
            socks_proxy: if set will use the specified SOCKS5 proxy for
                performing HTTP requests. (ex. "127.0.0.1:9050")

        """
        self.agent = client.Agent(reactor)
        if socks_proxy:
            socks_host, socks_port = socks_proxy.split(':')
            from txsocksx.http import SOCKS5Agent
            torEndpoint = TCP4ClientEndpoint(reactor, socks_host, int(socks_port))
            self.agent = SOCKS5Agent(reactor, proxyEndpoint=torEndpoint)
    
    def request(self, method, url, data=None):
        bodyProducer = None
        if data:
            bodyProducer = StringProducer(data)
        d = self.agent.request(method, url, bodyProducer=bodyProducer)
        d.addCallback(client.readBody)
        return d

    def get(self, url):
        return self.request('GET', url)

    def post(self, url, data=None):
        return self.request('POST', url, data)

     def put(self, url, data=None):
        return self.request('PUT', url, data)
    
class PoolClient(HTTPClient):
    pass

class ScrollClient(HTTPClient):
    pass

