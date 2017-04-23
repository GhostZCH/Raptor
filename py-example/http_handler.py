import socket
import errno
import copy

from event_server import Event
from tcp_handler import TcpHandler

_TEST_DATA = "HTTP/1.0 200 OK\r\nContent-type :text/plain\r\nContent-length: 12\r\n\r\nhello raptor"


class HttpHeader:
    def __init__(self, head_buf):
        self._buf = head_buf
        self.keep_alive = False
        self.content_len = 0
        self.host = None
        self.url = None
        self.type = None
        self.version = None

    def parse(self):
        lines = self._buf.splitlines()
        self._parse_request_line(lines[0])
        for l in lines[1:]:
            self._parse_header_line(l)

    def _parse_request_line(self, line):
        parts = line.split()
        if len(parts) != 3:
            raise Exception('request line parse err')

        self.url = parts[1]
        self.type = parts[0]
        self.version = parts[2]

        if self.version == 'HTTP/1.1':
            self.keep_alive = True

    def _parse_header_line(self, line):
        parts = line.split(': ')
        if len(parts) != 2:
            raise Exception('header line parse err')
        param = parts[0].lower()
        if param == 'content-length':
            self.content_len = int(parts[1])
            return

        if param == 'connection':
            self.keep_alive = parts[1].lower() == 'keep-alive'
            return

        self.__dict__[param] = parts[1]


class HttpHandler(TcpHandler):
    def __init__(self, conn, conf, event_server):
        TcpHandler.__init__(self, conn, conf, event_server)

        self._read_buf = ''
        self._send_buf = copy.copy(_TEST_DATA)

        self._conn.setblocking(False)
        self._current_process = self._read_head

        self._header = None

    def event_write(self):
        pass

    def event_read(self):
        self._current_process()

    def event_hup(self):
        self.close()
        print 'peer close connection'

    def close(self):
        self._conn.close()
        self._svr.remove_handler(Event(self))

    def _safe_read(self):
        try:
            buf = self._conn.recv(2048)
            return buf
        except socket.error as ex:
            if ex.errno == errno.EAGAIN:
                return ''
            else:
                raise ex

    def _read_head(self):
        self._read_buf += self._safe_read()

        header_end_index = self._read_buf.find('\r\n\r\n')
        if header_end_index < 0:
            return

        self._header = HttpHeader(self._read_buf[:header_end_index])
        self._header.parse()
        self._read_buf = self._read_buf[header_end_index+4:]

        self._current_process = self._read_body
        self._read_body()

    def _read_body(self):
        # TODO
        self._current_process = self._send_response
        self._send_response()
        return

    def _send_response(self):
        send_len = self._conn.send(self._send_buf)
        self._send_buf = self._send_buf[send_len:]  # TODO

        if self._header.keep_alive:
            self.close()
            return

        self._current_process = self._read_head
