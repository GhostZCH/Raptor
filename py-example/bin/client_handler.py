from base_handler import BaseHandler
from events import NetEvent, TimerEvent
from http import Request, Response

from helper import helper
from util import read, get_host_conf, ClientCloseConnection, ServerCloseConnection


class ClientHandler(BaseHandler):
    def __init__(self, connection, server, conf):
        BaseHandler.__init__(self, connection, server, conf)
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

                tmp, ex = read(self._connection)
                if ex:
                    raise ex

                self._req.buf += tmp
                if not self._req.parse_headers():
                    return

                self._init_helper(self._req.host)

            h = self._helpers[self._current_helper_index]

            if h.handle(ev):
                self._current_helper_index += 1
        except ServerCloseConnection:
            self.close()
        except ClientCloseConnection:
            self.close()

    def _init_helper(self, host):
        conf = get_host_conf(host, self._conf)
        if not conf:
            self._helpers.append(self._get_helper('Default'))
            return

        helpers = conf['helpers'].split()
        for name in helpers:
            self._helpers.append(self._get_helper(name))

    def _get_helper(self, name):
        return helper(name, self._conf, self._server, self._ctx, self._req, self._res)