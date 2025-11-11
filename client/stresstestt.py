import socket
import time
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("49.3.59.62", 11000))
sock.send(b''.join([bytes(1), 'sigma\r'.encode('utf-16')]))
time.sleep(5)

while True:
    sock.send(b''.join([int(1).to_bytes(1, 'big'), 'm\r'.encode("utf-16")]))
    time.sleep(0.1)
