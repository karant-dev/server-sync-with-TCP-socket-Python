# Name - Karan Jeeten Thakkar
# UTA ID - 1001852000

import socket
import pickle
import sys

HOST = '127.0.0.1'  # Server A's hostname or IP address
PORT = 65431        # The port used by the server

# Check number of arguments
if len(sys.argv) != 1 and len(sys.argv) != 3:
    print("Invalid number of arguments: Either enter only 'client.py' or 'client.py lock/unlock [index_of_file]")
    exit(0)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    if len(sys.argv) == 3:
        s.sendall(pickle.dumps(sys.argv[1:]))
    data = s.recv(2048)

printData = pickle.loads(data)
# print(*printData, sep = '\n')

print("\n{:5s}¦ {:32s}¦ {:10s}¦ {:26s}¦ {:13s} \n{}".format("Index", "File name", "File size", "Last modified / created", "Lock Status", "="*94))

i = 0

for data in printData:
    print("{:5d}¦ {:32s}¦ {:10s}¦ {:26s}¦ {:13s}".format(i, data[0], data[1], data[2], data[4]))
    i += 1

print("\n")