import socket
import time
from select import epoll, EPOLLET, EPOLLHUP, EPOLLIN, EPOLLOUT


TEST_RESPONSE = 'HTTP/1.0 200 OK\r\n' \
                'Content-Type: text/html\r\n' \
                'Connection: keep-alive\r\n' \
                'Content-Length: 13\r\n\r\n' \
                'TEST_RESPONSE'


class Event:
    def __init__(self, epoll_event=0, timer=False):
        self.read = epoll_event & EPOLLIN
        self.write = epoll_event & EPOLLOUT
        self.error = epoll_event & EPOLLHUP
        self.timer = timer

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class TcpHandler:
    def __init__(self, conn, svr, conf, shared_conf):
        self._svr = svr
        self._conn = conn
        self._conf = conf
        self._shared_conf = shared_conf

        self._conn.setblocking(False)

        self._buf = ''

    def fileno(self):
        return self._conn.fileno()

    def read(self):
        try:
            while True:
                buf = self._conn.recv(4096)
                if not buf:
                    return

                self._buf += buf

        except socket.error as ex:
            if not ex.errno == 11:
                raise ex

        return len(self._buf)

    def write(self):
        try:
            while self._buf:
                n = self._conn.send(self._buf)
                self._buf = self._buf[n:]

        except socket.error as ex:
            if not ex.errno == 11:
                raise ex

    def accept(self):
        try:
            while True:
                client_conn = self._conn.accept()
                h = HttpHandler(client_conn[0], self._svr, self._conf, self._shared_conf)
                self._svr.add_handler(h)

        except socket.error as ex:
            if not ex.errno == 11:
                raise ex

    def __del__(self):
        self._conn.close()


class HttpHandler(TcpHandler):
    def __init__(self, conn, svr, conf, shared_conf):
        TcpHandler.__init__(self, conn, svr, conf, shared_conf)

        self.STATUS = {
            'READ': self.handle_read,
            'WRITE': self.handle_write,
            # 'WRITE_UPSTREAM',
            # 'READ_UPSTREAM'

        }

        self._keep_alive = True
        self._status = 'READ'
        self._add_read_timer = False
        self._add_write_timer = False

    def handle(self, ev):
        print self._status, ev
        return self.STATUS[self._status](ev)

    def handle_read(self, ev):
        if ev.read:
            self.read()
            if len(self._buf) > 0 and self._buf.find('\r\n\r\n') > 0:
                # read finished
                self._status = 'WRITE'
                self._buf = TEST_RESPONSE
                self.handle_write(Event(EPOLLOUT))
                return

            # if not self._add_read_timer:
                # read not finished
                # self._add_read_timer = False
                # self._svr.add_timer(self.fileno(), self._svr.now + 3)

            return

        if ev.timer or ev.error:
            # time out
            self._svr.remove_handler(self.fileno())
            return

    def handle_write(self, ev):
        if ev.write:
            self.write()

            if not self._buf:
                self._status = 'READ'
                return

            # if not self._add_write_timer:
            #     self._svr.add_timer(self.fileno(), self._svr.now + 3)

            return

        if ev.timer or ev.error:
            # time out
            self._svr.remove_handler(self.fileno())
            return


class ServerHandler(TcpHandler):
    def __init__(self,  conn, svr, conf, shared_conf):
        TcpHandler.__init__(self, conn, svr, conf, shared_conf)

    def handle(self, ev):
        if ev.read:
            return self.accept()


class TimerManager:
    def __init__(self):
        self._timers = {}  # {time-out: [ev1, ev2]}
        self._ev = Event(0, True)

    def run(self, handlers):
        now = time.time()

        for expired in self._timers.keys():
            if expired > now:
                continue

            for fd in self._timers[expired]:
                if fd not in handlers:
                    continue

                handlers[fd].handle(self._ev)

            del self._timers[expired]

    def add(self, expired, fd):
        if expired not in self._timers:
            self._timers[expired] = []

        self._timers[expired].append(fd)


class Server:
    def __init__(self, svr_sock, conf, shared_conf):
        self._conf = conf
        self._shared_conf = shared_conf

        self.now = int(time.time())
        self._epoll = epoll()
        self._timers = TimerManager()

        self._handlers = {}

        svr_handler = ServerHandler(svr_sock, self, conf, shared_conf)
        self.add_handler(svr_handler)

    def forever(self):
        while True:
            print '>>>>>'
            self._handle_epoll_event()
            self._timers.run(self._handlers)

    def _handle_epoll_event(self):
        ev_list = self._epoll.poll()
        print '>>>handle_epoll_event', len(ev_list)

        for fd, ev in ev_list:
            print 'handle_epoll_event', fd
            h = self._handlers[fd]
            h.handle(Event(ev))

    def add_timer(self, expired, fd):
        print 'add_timer'
        self._timers.add(expired, fd)

    def add_handler(self, handler):
        print 'add_handler'
        self._epoll.register(handler, EPOLLET | EPOLLHUP | EPOLLIN | EPOLLOUT)
        self._handlers[handler.fileno()] = handler

    def remove_handler(self, fd):
        print 'remove_handler'
        self._epoll.unregister(fd)
        del self._handlers[fd]

    def update_time(self):
        self.now = int(time.time())
