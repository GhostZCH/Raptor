import socket
from events import NetEvent, TimerEvent

TEST_RESPONSE = 'HTTP/1.0 200 OK\r\n' \
                'Content-Type: text/html\r\n' \
                'Connection: keep-alive\r\n' \
                'Content-Length: 13\r\n\r\n' \
                'TEST_RESPONSE'


class ClientCloseConnection(Exception):
    def __init__(self):
        pass


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


class TcpHandler(HandlerBase):
    def __init__(self, connection, server, conf):
        HandlerBase.__init__(self, connection, server, conf)
        self._connection.setblocking(False)

    def read(self):
        buf = ''
        try:
            while True:
                tmp = self._connection.recv(4096)
                if tmp:
                    buf += tmp
                else:
                    raise ClientCloseConnection()

        except socket.error as ex:
            if not ex.errno == 11:
                raise ex
        return buf

    def write(self, buf):
        try:
            while buf:
                n = self._connection.send(buf)
                buf = buf[n:]

        except socket.error as ex:
            if not ex.errno == 11:
                raise ex

        return buf


class HttpHandler(TcpHandler):
    _READ_TIMER_ID = 1
    _WRITE_TIMER_ID = 2

    def __init__(self, connection, server, conf):
        TcpHandler.__init__(self, connection, server, conf)

        self._status = 'READ'
        self._read_buf = ''
        self._send_buf = ''

        event = NetEvent(self.fileno())
        event.read = True
        event.write = True
        event.error = True
        self._server.add_net_event(event)

    def handle(self, ev):
        try:
            if ev.error:
                raise ClientCloseConnection()

            if ev.read and self._status == 'READ':
                self._read()
                return

            if ev.write and self._status == 'WRITE':
                self._write()
                return
        except ClientCloseConnection:
            self.close()

    def _get_content(self):
        self._send_buf = TEST_RESPONSE

    def _read(self):
        self._read_buf += self.read()

        if self._read_buf.find('\r\n\r\n') > 0:
            self._status = 'WRITE'
            self._get_content()
            self._read_buf = ''

    def _write(self):
        self._send_buf = self.write(self._send_buf)

        if self._send_buf:
            return

        self._status = 'READ'
        return


class HttpUpstreamHandler(HandlerBase):
    def __init__(self, connection, server, conf):
        HandlerBase.__init__(self, connection, server, conf)


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
                h = HttpHandler(client_conn, self._server, self._conf)
                self._server.add_handler(h)
        except Exception as ex:
            if not ex.errno == 11:
                raise ex
