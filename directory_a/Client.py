# Ref 1 - https://realpython.com/python-sockets/#echo-client-and-server

import socket
import pickle

HOST = '127.0.0.1'  # Server A's hostname or IP address
PORT = 65431        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, world')
    data = s.recv(2048)

printData = pickle.loads(data)
print(*printData, sep = '\n')
# print('Received', repr(data))