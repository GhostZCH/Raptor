class BaseHandler:
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