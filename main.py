import asyncio
import secrets
import socket
from contextlib import closing
import stun
from aiobtdht import DHT
from aioudp import UDPServer
from tcp_and_udp_proxy import udp_proxy

bootstrap_nodes_hosts = [
    ("dht.transmissionbt.com", 6881),
    ("router.bittorrent.com", 6881),
    ("router.bitcomet.com", 6881),
    ("dht.aelitis.com", 6881),
    ("bootstrap.jami.net", 4222)
]


async def test_method():
    print("hello from async method")


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def get_random_infoHash():
    return secrets.token_bytes(20)


async def main(loop):
    bootstrap_nodes = []
    for (host, port) in bootstrap_nodes_hosts:
        try:
            bootstrap_nodes.append((socket.gethostbyname(host), port))
        except:
            pass

    udp = UDPServer()
    ip = "0.0.0.0"
    port = find_free_port()

    print("Start getting external ip and port by stun server")
    nat_type, external_ip, external_port = stun.get_ip_info(ip, port)
    print(f"{nat_type} {external_ip} {external_port}")

    print(f"start server on ip: {ip} port: {port}")
    udp.run(ip, port, loop=loop)
    user_infohash = get_random_infoHash()
    print(f"your infohash {user_infohash.hex()}")

    dht = DHT(int(user_infohash.hex(), 16), server=udp, loop=loop)

    print("start bootstraping")
    await dht.bootstrap(bootstrap_nodes)
    print("bootstraping is done")

    print(f"announce with port {external_port}")
    await dht.announce(user_infohash, external_port)
    print("announce done")

    print("Write yours peer hash")
    peer_infohash = bytes.fromhex(input())

    print("search your peer in dht")
    peers = []
    step = 0
    while len(peers) == 0:
        step += 1
        peers = await dht[peer_infohash]
        if step % 10000 == 0:
            print(f".", end=' ')

    print(f"{len(peers)} peers founded")
    print("peers:", peers)

    peer_host = external_ip + ":" + str(external_port)

    print("Select mode.")
    print("1 - Server mode. You want share your server")
    print("2 - Client mode. You want get access to server of other user")
    mode = input()
    if mode == 1:
        print("Write source for proxing data 'ip:port' ")
        real_server_host = input()
        udp_proxy(peer_host, real_server_host)
    elif mode == 2:
        local_host = ip + ":" + str(port)
        udp_proxy(local_host, peer_host)
        print("Use this host to connect for your peer" + local_host)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # remove on non windows system
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.run_forever()
