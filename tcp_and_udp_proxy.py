import logging
import select
import socket

FORMAT = '%(asctime)-15s %(levelname)-10s %(message)s'
logging.basicConfig(format=FORMAT)
LOGGER = logging.getLogger()

LOCAL_DATA_HANDLER = lambda x: x
REMOTE_DATA_HANDLER = lambda x: x

BUFFER_SIZE = 2 ** 10  # 1024. Keep buffer size as power of 2.


def udp_proxy(src, dst, src_socket = None):
    """Run UDP proxy.

    Arguments:
    src -- Source IP address and port string. I.e.: '127.0.0.1:8000'
    dst -- Destination IP address and port. I.e.: '127.0.0.1:8888'
    """
    LOGGER.debug('Starting UDP proxy...')
    LOGGER.debug('Src: {}'.format(src))
    LOGGER.debug('Dst: {}'.format(dst))

    proxy_socket = src_socket

    client_address = None
    server_address = dst

    LOGGER.debug('Looping proxy (press Ctrl-Break to stop)...')
    while True:
        data, address = proxy_socket.recvfrom(BUFFER_SIZE)

        if client_address == None:
            client_address = address

        if address == client_address:
            data = LOCAL_DATA_HANDLER(data)
            proxy_socket.sendto(data, server_address)
        elif address == server_address:
            data = REMOTE_DATA_HANDLER(data)
            proxy_socket.sendto(data, client_address)
            client_address = None
        else:
            LOGGER.warning('Unknown address: {}'.format(str(address)))


# end-of-function udp_proxy


def tcp_proxy(src, dst):
    """Run TCP proxy.

    Arguments:
    src -- Source IP address and port string. I.e.: '127.0.0.1:8000'
    dst -- Destination IP address and port. I.e.: '127.0.0.1:8888'
    """
    LOGGER.debug('Starting TCP proxy...')
    LOGGER.debug('Src: {}'.format(src))
    LOGGER.debug('Dst: {}'.format(dst))

    sockets = []

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(src)
    s.listen(1)

    s_src, _ = s.accept()

    s_dst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_dst.connect(dst)

    sockets.append(s_src)
    sockets.append(s_dst)

    while True:
        s_read, _, _ = select.select(sockets, [], [])

        for s in s_read:
            data = s.recv(BUFFER_SIZE)

            if s == s_src:
                d = LOCAL_DATA_HANDLER(data)
                s_dst.sendall(d)
            elif s == s_dst:
                d = REMOTE_DATA_HANDLER(data)
                s_src.sendall(d)


# end-of-function tcp_proxy