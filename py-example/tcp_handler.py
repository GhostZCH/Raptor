import socket
from base_handler import BaseHandler


class TcpHandler(BaseHandler):
    def __init__(self, conn, conf, event_server):
        BaseHandler.__init__(self, conn.fileno(), event_server)
        self._conn = conn
        self._conf = conf

    def handle(self, event):
        if event.write:
            self.event_write()

        if event.read:
            self.event_read()

        if event.hup and not event.read and not event.write:
            self.event_hup()

    def event_write(self):
        raise NotImplementedError()

    def event_read(self):
        raise NotImplementedError()

    def event_hup(self):
        raise NotImplementedError()
