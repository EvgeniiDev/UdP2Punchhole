import socket
import platform

pc_name = platform.node()

print("Write your penfriend ip and port in format - ip:port")
dest_ip, dest_port = input().split(":")
dest_addr = (dest_ip, int(dest_port))

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    s.sendto(str.encode(f"{input()} от {pc_name}"), dest_addr)
    data, _ = s.recvfrom(1024)
    print("вам прислали: " + data.decode())
else:
    s.close()