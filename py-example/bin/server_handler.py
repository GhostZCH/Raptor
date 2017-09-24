import socket

from base_handler import BaseHandler
from client_handler import ClientHandler
from events import NetEvent


class ServerHandler(BaseHandler):
    def __init__(self, addr, server, conf):
        connection = socket.socket()
        BaseHandler.__init__(self, connection, server, conf)

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