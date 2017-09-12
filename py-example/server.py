from bin.event_server import EventServer
from conf.config import CONF


def main():
    svr = EventServer(CONF)
    svr.forever()

if __name__ == '__main__':
    main()
