import socket
from server import Server

SVR_ADDR = ('0.0.0.0', 8000)


def main():
    svr_conn = socket.socket()
    svr_conn.bind(SVR_ADDR)
    svr_conn.listen(512)

    svr = Server(svr_conn, {}, {})
    svr.forever()

if __name__ == '__main__':
    main()
