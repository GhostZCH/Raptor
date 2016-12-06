import os
import socket

from worker import Worker
from master import Master

from settings import CONF


def get_svr(port=8000):
    svr = socket.socket()
    svr.bind(('', port))
    svr.listen(1024)

    return svr


def main():
    master = Master(CONF)
    host = get_svr(8000)

    for index in xrange(CONF["worker-count"]):
        pid = os.fork()
        if not pid:
            Worker(index, CONF, host).start()

    master.start()

if __name__ == '__main__':
    main()
