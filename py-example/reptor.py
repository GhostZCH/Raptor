import os
import socket
import traceback


from worker import Worker
from master import Master

from settings import CONF


def get_svr_conn(port=8000):
    svr = socket.socket()
    svr.bind(('', port))
    svr.listen(1024)

    return svr


def main():
    host = get_svr_conn()
    master = Master(host, CONF)

    try:
        for index in xrange(CONF["worker-count"]):
            pid = os.fork()
            if not pid:
                Worker(index, CONF, host).start()
                continue

            master.add_child(pid)

        master.start()
    except:
        host.close()
        traceback.print_exc()

if __name__ == '__main__':
    main()
