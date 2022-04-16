# Name - Karan Jeeten Thakkar
# UTA ID - 1001852000

import socket
import os
import time
import pickle
import threading

HOST = '127.0.0.1'              # localhost
PORT = 65432                    # Port to listen on
FILE_TRANSFER_PORT = 65433      # Port to listen on for file transfers
PATH = r"directory_b"

def refresh_data():
    data = []
    cols = []
    with os.scandir(PATH) as dirs:
        for entry in dirs:
            cols.append(entry.name)
            cols.append("{:.2f}".format((os.path.getsize(PATH + "\\" + entry.name))/1024) + " KB")
            cols.append(time.ctime(os.path.getmtime(PATH + "\\" + entry.name)))
            # The below line is to store raw time for comparison NOT REDUNDANT
            cols.append(os.path.getmtime(PATH + "\\" + entry.name))
            cols.append(" ")
            data.append(cols)
            cols = []
    return pickle.dumps(data)

def send_file_info():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Listening for Server A on port {} to exchange file information.".format(PORT))
        while True:
            conn, addr = s.accept()
            # print("Polling for changes in directory_a {}".format(addr))
            with conn:
                # while True:
                conn.sendall(refresh_data())

def sync_with_A():
    while True:
        time.sleep(4)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            recv_data = b""
            s.bind((HOST, FILE_TRANSFER_PORT))
            s.listen()
            print("Listening for Server A on port {} for file transfer.".format(FILE_TRANSFER_PORT))
            conn, addr = s.accept()
            while True:
                temp = conn.recv(8192)
                recv_data += temp
                if len(temp) < 8192:
                    break
            recv_data = pickle.loads(recv_data)
            file_names_to_send = recv_data[0]
            file_data_to_write = recv_data[1]
            for key in file_data_to_write.keys():
                ptr = open(PATH + "\\" + key, "wb")
                ptr.write(file_data_to_write[key][0])
                ptr.flush()
                ptr.close()
                os.utime(PATH + "\\" + key, (file_data_to_write[key][1], file_data_to_write[key][1]))
                print("Updated file {} on B".format(key))
            file_data_to_send = dict()
            for file in file_names_to_send:
                ptr = open(PATH + "\\" + file, "rb")
                file_data_to_send[file] =[ptr.read(), os.path.getmtime(PATH + "\\" + file)]
                ptr.close()
            # s.connect((HOST, FILE_TRANSFER_PORT))
            conn.sendall(pickle.dumps(file_data_to_send))


file_info_thread = threading.Thread(target = send_file_info)
file_sync_thread = threading.Thread(target = sync_with_A)
file_info_thread.start()
file_sync_thread.start()