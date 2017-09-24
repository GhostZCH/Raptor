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
        self.body = ''

    def parse_headers(self):
        if '\r\n\r\n' not in self.buf:
            return False

        return True

    def parse_result(self):
        self.buf = self._RESPONSE % (
            _STATES[self.status],
            len(self.body),
            self.body
        )
