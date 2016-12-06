import time

from select import epoll, EPOLLET, EPOLLIN, EPOLLOUT

_TEST_DATA = "HTTP/1.0 200 OK\r\nContent-type :text/plain\r\nContent-length: 100\r\n\r\n" + '0' * 100


class Worker:
    def __init__(self, worker_id, conf, host):
        self._id = worker_id
        self._conf = conf
        self._host = host
        self._epoll = epoll()

    def start(self):
        self._epoll.register(self._host, EPOLLIN | EPOLLOUT)
        while True:
            for fd, event in self._epoll.poll(1, 1024):
                if fd == self._host.fileno():
                    client = self._host.accept()[0]
                    print self._id, 'attept', client.fileno()
                    client.recv(1024)
                    client.send(_TEST_DATA)
                    client.close()
