import socket
from events import NetEvent, TimerEvent
from http import Request, Response

from helper import helper
from util import read, get_host_conf, ClientCloseConnection, ServerCloseConnection


class HandlerBase:
    def __init__(self, connection, server, conf):
        self._conf = conf
        self._connection = connection
        self._server = server

    def fileno(self):
        return self._connection.fileno()

    def handle(self, ev):
        raise NotImplemented()

    def close(self):
        self._server.remove_handler(self.fileno())
        self._connection.close()

    def __del__(self):
        self.close()


class ClientHandler(HandlerBase):
    def __init__(self, connection, server, conf):
        HandlerBase.__init__(self, connection, server, conf)
        self._connection.setblocking(False)

        self._helpers = []
        self._current_helper_index = 0
        self._ctx = {}
        self._req = Request(self._connection, '')
        self._res = Response(self._connection)

        event = NetEvent(self.fileno())
        event.read = True
        event.write = True
        event.error = True
        self._server.add_net_event(event)

    def handle(self, ev):
        try:
            if not self._helpers:
                if not ev.read:
                    return

                self._req.buf += read(self._connection)
                if not self._req.parse_headers():
                    return

                self._init_helper(self._req.host)

            h = self._helpers[self._current_helper_index]

            if h.handle(ev):
                self._current_helper_index += 1
        except ServerCloseConnection or ClientCloseConnection:
            self.close()

    def _init_helper(self, host):
        conf = get_host_conf(host, self._conf)
        if not conf:
            self._helpers.append(self._get_helper('DefaultHelper'))
            return

        helpers = conf['helpers'].split()
        for name in helpers:
            self._helpers.append(self._get_helper(name))

    def _get_helper(self, name):
        return helper(name, self._conf, self._ctx, self._req, self._res)


class ServerHandler(HandlerBase):
    def __init__(self, addr, server, conf):
        connection = socket.socket()
        HandlerBase.__init__(self, connection, server, conf)

        self._addr = addr
        self._connection.bind(addr)
        self._connection.listen(1024)
        self._connection.setblocking(False)

        event = NetEvent(self.fileno())
        event.read = True
        event.error = True
        self._server.add_net_event(event)

    def handle(self, ev):
        if ev.error:
            self.close()
            raise Exception("server error")

        try:
            while True:
                client_conn = self._connection.accept()[0]
                h = ClientHandler(client_conn, self._server, self._conf)
                self._server.add_handler(h)
        except Exception as ex:
            if not ex.errno == 11:
                raise ex
