# https://segmentfault.com/a/1190000015068125

import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 8020))

print('waiting for message...')
while True:
    data, addr = sock.recvfrom(1024)
    data = data.decode('utf-8')
    print('Got message from', addr)
    print('Received message:', data)
    sock.sendto(bytes('[%s] %s' % (time.ctime(), data), 'utf-8'), addr)

sock.close()