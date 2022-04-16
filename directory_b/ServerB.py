# Ref 1 - https://realpython.com/python-sockets/#echo-client-and-server
# Ref 2 - https://www.simplifiedpython.net/python-get-files-in-directory/
# Ref 3 - https://flaviocopes.com/python-get-file-details/
# Ref 4 - https://datatofish.com/modified-time-file-python/

import socket
import os
import time
import pickle

HOST = '127.0.0.1'  # localhost
PORT = 65432        # Port to listen on
PATH = r"C:\Users\Karan\OneDrive - University of Texas at Arlington\UTA Study\Sem 3 - Fall 2021\CSE 5306 - Distributed Systems - Chance Eary\Lab 1\serverB"
data = []
cols = []

with os.scandir(PATH) as dirs:
    for entry in dirs:
        cols.append(entry.name)
        cols.append("{:.2f}".format((os.path.getsize(PATH + "\\" + entry.name))/1024) + " KB")
        cols.append(time.ctime(os.path.getmtime(PATH + "\\" + entry.name)))
        data.append(cols)
        cols = []

# print(*data, sep = '\n')

sendData = pickle.dumps(data)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(sendData)