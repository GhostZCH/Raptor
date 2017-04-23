from tcp_handler import TcpHandler
from http_handler import HttpHandler

from event_server import Event


class HostHandler(TcpHandler):
    def __init__(self, conn, conf, event_server):
        TcpHandler.__init__(self, conn, conf, event_server)
        self._conn.setblocking(False)

    def event_write(self):
        pass

    def event_read(self):
        client_conn = self._conn.accept()[0]
        client_handler = HttpHandler(client_conn, self._conf, self._svr)

        event = Event(client_handler)
        event.read = True
        event.write = True
        event.hup = True
        event.et = True

        self._svr.add_handler(event)

    def event_hup(self):
        pass
        # raise Exception('bind in socket err')

