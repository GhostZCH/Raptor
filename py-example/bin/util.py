import socket


class ClientCloseConnection(Exception):
    def __init__(self):
        pass


class ServerCloseConnection(Exception):
    def __init__(self):
        pass


def get_host_conf(host, conf):
    return conf['servers'].get(host, None)


def read(conn):
    buf = ''
    try:
        while True:
            tmp = conn.recv(4096)
            if tmp:
                buf += tmp
            else:
                raise ClientCloseConnection()
    except socket.error as ex:
        if not ex.errno == 11:
            raise ex
    return buf


def write(conn, buf):
    try:
        while buf:
            n = conn.send(buf)
            buf = buf[n:]

    except socket.error as ex:
        if not ex.errno == 11:
            raise ex

    return buf
