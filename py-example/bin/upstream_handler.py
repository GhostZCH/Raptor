from events import NetEvent
from base_handler import BaseHandler


class UpstreamHandler(BaseHandler):
    def __init__(self, connection, server, conf, upstream_helper):
        BaseHandler.__init__(self, connection, server, conf)
        self._connection.setblocking(False)
        self._helper = upstream_helper

        event = NetEvent(self.fileno())
        event.read = True
        event.write = True
        event.error = True
        self._server.add_net_event(event)

    def connection(self):
        return self._connection

    def handle(self, ev):
        self._helper.handle_upstream(ev)
