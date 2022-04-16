# Name - Karan Jeeten Thakkar
# UTA ID - 1001852000

import socket
import os
import time
import pickle
import threading

HOST = '127.0.0.1'  # localhost
LISTEN_PORT = 65431  # Port to listen on
SERVER_PORT = 65432  # Port server B is listening on
FILE_TRANSFER_PORT = 65433  # Port to connect with server B for file transfer

PATH = r"directory_a"
data = []
locked_files = set()
list_sent_to_client = []
operation = ''
index = -1

def refresh_server_A_data():
    global locked_files
    file_info_A = []
    cols = []
    with os.scandir(PATH) as dirs:
        for entry in dirs:
            cols.append(entry.name)
            cols.append("{:.2f}".format((os.path.getsize(PATH + "\\" + entry.name)) / 1024) + " KB")
            cols.append(time.ctime(os.path.getmtime(PATH + "\\" + entry.name)))
            # The below line is to store raw time for comparison NOT REDUNDANT
            cols.append(os.path.getmtime(PATH + "\\" + entry.name))
            if entry.name in locked_files:
                lock_status = "<locked>"
            else:
                lock_status = " "
            cols.append(lock_status)
            file_info_A.append(cols)
            cols = []
    return file_info_A


def get_data_from_serverB():
    file_info_B = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, SERVER_PORT))
        recv_data = b""
        while True:
            temp = s.recv(2048)
            recv_data += temp
            if len(temp) < 2048:
                break
    recv_data_list = pickle.loads(recv_data)
    for row in recv_data_list:
        file_info_B.append(row)
    return file_info_B


def get_and_merge_file_details():
    global list_sent_to_client
    global data
    file_info_A = refresh_server_A_data()
    file_info_B = get_data_from_serverB()
    data = file_info_A + file_info_B
    data = sorted(data, key=lambda x: x[0])
    print_data = []
    for idx in range(len(data)):
        if idx % 2 == 0:
            print_data.append(data[idx])
    sendData = pickle.dumps(print_data)
    list_sent_to_client = print_data
    return sendData


def get_filenames_to_transfer():
    file_info_A = refresh_server_A_data()
    file_info_B = get_data_from_serverB()
    files_to_fetch = []
    files_to_send = []
    file_dict_A = {row[0]: row for row in file_info_A}
    file_dict_B = {row[0]: row for row in file_info_B}
    for key in file_dict_B.keys():
        if key not in file_dict_A.keys() and key not in locked_files:
            files_to_fetch.append(key)
        elif (key in file_dict_A.keys() and file_dict_B[key][3] > file_dict_A[key][3]) and key not in locked_files:
            files_to_fetch.append(key)
    for key in file_dict_A.keys():
        if key not in file_dict_B.keys() and key not in locked_files:
            files_to_send.append(key)
        elif (key in file_dict_B.keys() and file_dict_A[key][3] > file_dict_B[key][3]) and key not in locked_files:
            files_to_send.append(key)
    return files_to_fetch, files_to_send


def sync_with_B():
    print("Listening for Server B on port {} for file transfer".format(FILE_TRANSFER_PORT))
    while True:
        time.sleep(4)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            recv_data = b""
            files_to_fetch, files_to_send = get_filenames_to_transfer()
            if len(files_to_fetch) == 0 and len(files_to_send) == 0:
                continue
            file_data_to_send = dict()
            for file in files_to_send:
                ptr = open(PATH + "\\" + file, "rb")
                file_data_to_send[file] = [ptr.read(), os.path.getmtime(PATH + "\\" + file)]
                ptr.close()

            list_of_file_exchange_data = [files_to_fetch, file_data_to_send]
            s.connect((HOST, FILE_TRANSFER_PORT))
            s.sendall(pickle.dumps(list_of_file_exchange_data))
            # print("Listening for Server B on port {} for file transfer.".format(FILE_TRANSFER_PORT))
            # conn, addr = s.accept()
            while True:
                temp = s.recv(8192)
                recv_data += temp
                if len(temp) < 8192:
                    break
            recv_data = pickle.loads(recv_data)
            file_data_to_write = recv_data
            for key in file_data_to_write.keys():
                ptr = open(PATH + "\\" + key, "wb")
                ptr.write(file_data_to_write[key][0])
                ptr.flush()
                ptr.close()
                os.utime(PATH + "\\" + key, (file_data_to_write[key][1], file_data_to_write[key][1]))
                print("Updated file {} on A".format(key))


def send_file_info_to_client():
    global operation
    global index
    global locked_files
    global list_sent_to_client
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, LISTEN_PORT))
        s.listen()
        print("Listening for client on port {}".format(LISTEN_PORT))
        while True:
            conn, addr = s.accept()
            print("Connected to client {}".format(addr))
            with conn:
                # while True:
                try:
                    conn.settimeout(0.2)
                    client_args = conn.recv(2048)
                    file_operation = pickle.loads(client_args)
                    operation = file_operation[0][1:]
                    index = int(file_operation[1][1:])
                    if operation.casefold() == 'lock':
                        locked_files.add(list_sent_to_client[index][0])
                    elif operation.casefold() == 'unlock':
                        locked_files.remove(list_sent_to_client[index][0])
                except Exception as e:
                    file_operation = []
                conn.sendall(get_and_merge_file_details())


file_info_thread = threading.Thread(target=send_file_info_to_client)
file_sync_thread = threading.Thread(target=sync_with_B)
file_info_thread.start()
file_sync_thread.start()
