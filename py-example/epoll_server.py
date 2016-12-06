import socket
from select import epoll, EPOLLET, EPOLLIN, EPOLLOUT




class EpollServer:
    def __init__(self, host):
        self._host = host
        self._epoll = epoll()
        self._epoll.register(self._sock, EPOLLIN | EPOLLOUT)

    def wait(self):
        for fd, event in self._epoll.poll(1, 1024):
            if fd == self._sock.fileno():
                self._accept()

    def _accept(self):
        client = self._sock.accept()
        client.recv()
        client.send(_TEST_DATA)
        client.close()
