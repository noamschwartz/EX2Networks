import os
import socket
import sys

FILE_RECIEVER = "1"
FILE_SENDER = "0"


# This function gets the arguments from the cmd according to the user type
def get_args(user_type):
    ip = sys.argv[2]
    server_port = int(sys.argv[3])
    if user_type == "0":
        listening_port = sys.argv[4]
        return ip, server_port, listening_port
    else:
        return ip, server_port


# get user type
user_type = sys.argv[1]
if user_type == "0":
    ip, server_port, listening_port = get_args(user_type)
else:
    ip, server_port = get_args(user_type)

# if the user is a file sender i.e. 0
if user_type == FILE_SENDER:
    # open socket and connect as client to send filelist
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, server_port))
    #create the sender format
    msg = "1 " + listening_port + " "
    file_list = filter(os.path.isfile, os.listdir(os.curdir))
    #create the list of files in the correct format
    for file in file_list:
        msg += file + ","
    s.send(msg[:-1].encode())
    s.close()
    # connect as server and send the files to clients inquiries
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', int(listening_port)))
    server.listen(5)
    #open a socket and wait for other clients to connect and request a file.
    while True:
        client_socket, client_address = server.accept()
        data = client_socket.recv(1024)
        file = open(data.decode(), 'rb')
        #read from the file and send its info
        l = file.read(1024)
        while l:
            client_socket.send(l)
            l = file.read(1024)
        #notify the client the sending has been completed
        client_socket.send("quit".encode())
        file.close()

# if the user is a file receiver i.e. 1
elif user_type == FILE_RECIEVER:
    while True:
        # open socket and connect
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, server_port))
        # get a file request
        find_msg = "2 " + input("Search: ")
        s.send(find_msg.encode())
        data = s.recv(1024).decode()
        s.close()
        # now connect to the relevant client
        #as long as files exist
        if data is not '\n':
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_dtl = {}
                # print files to choose from
                files = data.split(",")
                final_list = []
                #iterate over the list of files and create the tuple of info
                for file in range(len(files) - 1):
                    args = files[file].split(" ")
                    file_name = args[0]
                    ip = args[1]
                    port = int(args[2])
                    list_tuple = str(file + 1) + " " + file_name
                    final_list.append(list_tuple)
                    client_dtl[file] = (file_name, (ip, port))
                #print the final list of files
                for i in final_list:
                    print(i)
                #if there are files existing
                if client_dtl:
                    chosen_num = int(input("Choose: "))
                    chosen= client_dtl[chosen_num - 1]
                    chosen_file_name = chosen[0]
                    chosen_ip_and_port = chosen[1]
                    #send the file name to the client
                    server.connect(chosen_ip_and_port)
                    server.send(chosen_file_name.encode())
                    # open the file and write
                    with open(chosen_file_name, 'wb') as f:
                        while True:
                            data = server.recv(1024)
                            if not data or 'quit'.encode() in data:
                                #get rid of last 4 chars : "quit"
                                data = data[:-5]
                                f.write(data)
                                break
                            f.write(data)
                    # close socket right after file has been recienved
                    f.close()
                    server.close()
                    # file has been recieved, continue to the next search