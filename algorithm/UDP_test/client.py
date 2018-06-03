# https://segmentfault.com/a/1190000015068125


import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = ('127.0.0.1', 8020)

while True:
    msg = input('Wanna send: ')
    if not msg:
        break
    sock.sendto(bytes(msg, 'utf-8'), address)  # Return the number of bytes sent
    data, addr = sock.recvfrom(1024)
    data = data.decode('utf-8')
    print('Response:', data)

sock.close()