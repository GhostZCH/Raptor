_STATES = {
    200: '200 OK',
    404: '404 Not Found'
}


class Request:
    def __init__(self, conn, buf):
        self.conn = conn
        self.method = ''
        self.buf = buf
        self.header = ''
        self.headers = {}
        self.keep_alive = False
        self.host = ''
        self.url = ''
        self.params = ''
        self.body = ''
        self.content_len = 0
        self.is_recv_header = False
        self.is_recv_body = False

    def parse_headers(self):
        if '\r\n\r\n' not in self.buf:
            return False

        self.header = self.buf.split('\r\n\r\n')[0]
        lines = self.header.split('\r\n')

        self.method, self.url, _ = lines[0].split()
        for l in lines[1:]:
            k, v = l.split(': ')
            self.headers[k.strip().lower()] = v.strip()

        self.host = self.headers['host']
        self.content_len = int(self.headers.get('content-length', 0))

        self.is_recv_header = True
        return True

    def parse_body(self):
        if not self.is_recv_header:
            return False

        if len(self.buf) < len(self.header) + len('\r\n\r\n') + self.content_len:
            return False

        start = len(self.header) + len('\r\n\r\n')

        self.body = self.buf[start: start+self.content_len]
        self.is_recv_body = True
        return True


class Response:
    _RESPONSE = 'HTTP/1.1 %s\r\n' \
                'Content-Type: text/html\r\n' \
                'Connection: close\r\n' \
                'Content-Length: %s\r\n\r\n' \
                '%s'

    def __init__(self, conn):
        self.conn = conn
        self.status = 200
        self.buf = ''
        self.header = ''
        self.headers = {}
        self.body = ''
        self.content_len = 0
        self.is_recv_header = False
        self.is_recv_body = False

    def parse_headers(self):
        if '\r\n\r\n' not in self.buf:
            return False

        self.header = self.buf.split('\r\n\r\n')[0]

        lines = self.header.split('\r\n\r\n')
        _, self.status, _ = lines[0].split(' ', 2)
        self.status = int(self.status)

        for l in lines[1:]:
            k, v = l.split(': ')
            self.headers[k.strip().lower()] = v.strip()

        self.content_len = int(self.headers.get('content-length', 0))

        self.is_recv_header = True
        return True

    def parse_body(self):
        if not self.is_recv_header:
            return False

        if len(self.buf) < len(self.header) + len('\r\n\r\n') + self.content_len:
            return False

        start = len(self.headers) + len('\r\n\r\n')

        self.body = self.buf[start: start+self.content_len]
        self.is_recv_body = True
        return True

    def parse(self):
        if not self.is_recv_header and not self.parse_headers():
            return False

        if not self.is_recv_body and not self.parse_body():
            return False

        return True

    def parse_result(self):
        self.buf = self._RESPONSE % (
            _STATES[self.status],
            len(self.body),
            self.body
        )
