import os
from util import read, write, ServerCloseConnection, ClientCloseConnection, get_host_conf


class BaseHelper:
    def __init__(self, conf, ctx, req, res):
        self._ctx = ctx
        self._req = req
        self._res = res
        self._conf = conf
        self._server_conf = get_host_conf(self._req.host, self._conf)

    def handle(self, event):
        raise NotImplementedError()


class DefaultHelper(BaseHelper):
    TEST_RESPONSE = 'HTTP/1.1 200 OK\r\n' \
                    'Content-Type: text/html\r\n' \
                    'Connection: close\r\n' \
                    'Content-Length: 18\r\n\r\n' \
                    'Welcome To Raptor!'

    def __init__(self, conf, ctx, req, res):
        BaseHelper.__init__(self, conf, ctx, req, res)

    def handle(self, event):
        self._res.buf = self.TEST_RESPONSE
        write(self._res.conn, self._res.buf)
        raise ServerCloseConnection


class IndexHelper(BaseHelper):
    def __init__(self, conf, ctx, req, res):
        BaseHelper.__init__(self, conf, ctx, req, res)
        self._base = self._server_conf["base-dir"]

    def handle(self, event):
        file_name = self._base + self._req.url.split('?')[0]
        if not os.path.isfile(file_name):
            self._res.status = 404
        else:
            with open(file_name) as f:
                self._res.status = 200
                self._res.body = f.read()
        self._res.parse_result()
        write(self._res.conn, self._res.buf)
        raise ServerCloseConnection


_HELPERS = {
    'DefaultHelper': DefaultHelper,
    'IndexHelper': IndexHelper
}


def helper(name, conf, ctx, req, res):
    return _HELPERS[name](conf, ctx, req, res)
