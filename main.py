import asyncio
import secrets
import socket
import platform
import time
from contextlib import closing
import stun
from tcp_and_udp_proxy import udp_proxy


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

def get_ip_info(socket, source_ip="0.0.0.0", source_port=54320, stun_host=None,
                stun_port=3478):
    nat_type, nat = stun.get_nat_type(socket, source_ip, source_port,
                                      stun_host=stun_host, stun_port=stun_port)
    external_ip = nat['ExternalIP']
    external_port = nat['ExternalPort']

    return (nat_type, external_ip, external_port)

async def main(loop):
    ip = "0.0.0.0"
    port = find_free_port()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, port))

    print("Start getting external ip and port by stun server")
    nat_type, external_ip, external_port = get_ip_info(s, ip, port)
    print(f"{nat_type} {external_ip}:{external_port}")
    print(f"Send your ip and port to your friend - {external_ip}:{external_port}")

    print("Write your friend ip and port in format - ip:port")
    dest_ip, dest_port = input().split(":")
    dest_addr = (dest_ip, int(dest_port))

    print("start sending data...")

    pc_name = platform.node()
    for _ in range(1000):
        s.sendto(str.encode(f"Привет от {pc_name}"), dest_addr)
        time.sleep(1)
        data, _ = s.recvfrom(1024)
        print("вам прислали: " + data.decode())

    #print(f"start server on ip: {ip} port: {port}")
    #peer_host = external_ip + ":" + str(external_port)

    #print("Select mode.")
    #print("1 - Server mode. You want share your server")
    #print("2 - Client mode. You want get access to server")
    #mode = input()
    #if mode == 1:
    #    print("Write source for proxing data 'ip:port' ")
    #    real_server_host = input()
    #    udp_proxy(peer_host, real_server_host)
    #elif mode == 2:
    #    local_host = ip + ":" + str(port)
    #    udp_proxy(local_host, peer_host)
    #    print("Use this host to connect for your peer" + local_host)

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # remove on non windows system
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.run_forever()