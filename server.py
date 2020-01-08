import socket
import sys

RECIEVING_MODE = "2"
SENDING_MODE = "1"

# return all info : port number and files
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = '0.0.0.0'
server_port = int(sys.argv[1])
server.bind((server_ip, server_port))
server.listen(5)
# list of objects
clients_files = {}

while True:
    # gets a string of either "1 port files" or "2 search filename" parse it and go to relevant part of code
    client_socket, client_address = server.accept()
    #print('Connection from: ', client_address)
    data = (client_socket.recv(1024)).decode()
    #parse data
    user_type = data[0]
    # if 1, add port ip and files to connections
    if user_type == SENDING_MODE and data[1] == ' ':
        # get port and ip of sender and create Sender object, add files to the objects list
        args = data[2:].split(' ')
        port = args[0]
        ip = client_address[0]
        files_list = args[1].split(',')
        files_list = sorted(files_list, key=str.lower)
        # hold a db of all the files and the port and ip of each client holding those files.
        clients_files[(ip, port)] = files_list

    # if "2 search" connections files and make a string as in assignment and return to client (can close connection)
    elif user_type == RECIEVING_MODE and data[1] == ' ':
        search_list = data[2:]
        found = []
        msg = ""
        # find the requested files
        for client in clients_files.items():
            for file in client[1]:
                if search_list in file:
                    #if a matching file has been found
                    found.append((client[0], file))
        #create the string of all files in the format requested: "filename ip port, ....,filename ip port,\n"
        for file in found:
            files = ''.join(file[1])
            msg += files + " " + file[0][0] + " " + str(file[0][1]) + ","
        msg = msg + "\n"
        if not found:
            msg = '\n'
        #send the list of files to the client
        client_socket.send(msg.encode())
