import os
import socket
import copy

from upstream_handler import UpstreamHandler
from events import NetEvent
from util import read, write, ServerCloseConnection, ClientCloseConnection, get_host_conf


class BaseHelper:
    def __init__(self, conf, server, ctx, req, res):
        self._ctx = ctx
        self._svr = server
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

    def __init__(self, conf, server, ctx, req, res):
        BaseHelper.__init__(self, conf, server, ctx, req, res)

    def handle(self, event):
        self._res.buf = self.TEST_RESPONSE
        write(self._res.conn, self._res.buf)
        raise ServerCloseConnection()


class IndexHelper(BaseHelper):
    def __init__(self, conf, server, ctx, req, res):
        BaseHelper.__init__(self, conf, server, ctx, req, res)
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
        raise ServerCloseConnection()


class UpstreamHelper(BaseHelper):
    _RECV_FROM_CLIENT = 0
    _SEND_TO_UPSTREAM = 1
    _RECV_FROM_UPSTREAM = 2
    _SEND_TO_CLIENT = 3

    def __init__(self, conf, server, ctx, req, res):
        BaseHelper.__init__(self, conf, server, ctx, req, res)
        self._upstream_fd = self._get_upstream_handler()
        self._state = self._RECV_FROM_CLIENT
        self._upstream_buf_out = ''
        self._upstream_buf_in = ''

    def handle(self, event):
        # already recv head
        if event.read and self._state == self._RECV_FROM_CLIENT:
            if not self._req.is_recv_body:
                self._req.parse_body()

            if not self._req.is_recv_body:
                return

            self._state = self._SEND_TO_UPSTREAM
            self._upstream_buf_out = copy.copy(self._req.buf)
            upstream_ev = NetEvent(self._upstream_fd)
            upstream_ev.write = True
            self.handle_upstream(upstream_ev)

        if event.write and self._state == self._SEND_TO_CLIENT:
            self._upstream_buf_in = write(self._res.conn, self._upstream_buf_in)
            if not self._upstream_buf_in:
                raise ServerCloseConnection()

    def handle_upstream(self, event):
        h = self._svr.get_handler(self._upstream_fd)
        try:
            if event.write and self._state == self._SEND_TO_UPSTREAM:
                self._upstream_buf_out = write(h.connection(), self._upstream_buf_out)
                if self._upstream_buf_out:
                    return

                self._state = self._RECV_FROM_UPSTREAM
                event.read = True

            if event.read and self._state == self._RECV_FROM_UPSTREAM:
                tmp, ex = read(h.connection())
                self._res.buf += tmp
                if not self._res.parse():
                    return

                self._state = self._SEND_TO_CLIENT
                self._upstream_buf_in = self._res.buf
                self._upstream_buf_in = write(self._res.conn, self._upstream_buf_in)

                if ex:
                    raise ex

                if not self._upstream_buf_in:
                    raise ServerCloseConnection()
        except ServerCloseConnection:
            h.close()
        except ClientCloseConnection:
            h.close()

    def _get_upstream_handler(self):
        conn = socket.socket()
        conn.connect(self._server_conf['upstream'])
        h = UpstreamHandler(conn, self._svr, self._conf, self)
        self._svr.add_handler(h)
        return h.fileno()

_HELPERS = {
    'Default': DefaultHelper,
    'Index': IndexHelper,
    'Upstream': UpstreamHelper
}


def helper(name, conf, server, ctx, req, res):
    return _HELPERS[name](conf, server, ctx, req, res)
