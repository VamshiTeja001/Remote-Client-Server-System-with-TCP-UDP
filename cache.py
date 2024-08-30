# CACHE CODE #
# Name: Raghavendra Vamshi Teja Chathurajupalli
# Project 1

# Description: Code behaves as Cache. This system is closer to client. Whenever client requests for data, the cache checks if it has that file and if it does, it sends back the file to client, else it requests the Server for that file . 

# Execution Procedure: Open terminal/cmd, change to the directory in which cache.py file is present, then run python3 cache.py <cache_port> <server_host> <server_port> 

# Initializing necessary headers
import threading
import socket
import sys
import os
import snw_protocol as SNW
import tcp_transport as TCP

# python cache.py <cache_port> <server_host> <server_port>
CACHE_HOST ='0.0.0.0' #sys.argv[1] # Alternatively this can be replaced with 'localhost'. Windows sometimes doesnot permit two nodes using same host to connect with another node, so using this workaround
CACHE_PORT = int(sys.argv[1])
SERVER_HOST = sys.argv[2]
SERVER_PORT = int(sys.argv[3])
protocolType = sys.argv[4]

file_directory = "cache_files" # Save in this folder

def SNW_handle_request(data, address, cache_socket):
    command = data.decode()
    if command.startswith("get"):
        _, filename = command.split()

        # Check if the file exists in the cache
        if os.path.exists(filename):
            print(f"File {filename} found in cache.")
            
            # Send origin info
            #SNW.send_packet_with_snw(cache_socket, "Server Response: File delivered from cache".encode(), address)
            #SNW.send_packet_with_snw(cache_socket, "cache".encode(), address)
            SNW.send_packet_with_snw(cache_socket, "from cache".encode(), address) # Server

            # Send the file data
            with open(filename, 'rb') as f: 
                file_data = f.read()
            SNW.send_packet_with_snw(cache_socket, file_data, address)
        else:
            # If the file is not in the cache, request it from the server
            print(f"File {filename} not found in cache. Requesting from server.")
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
                server_socket.settimeout(SNW.TIMEOUT)
                
                SNW.send_packet_with_snw(server_socket, command.encode(), (SERVER_HOST, SERVER_PORT))
                file_data, _ = SNW.receive_packet_with_snw(server_socket)
                
                if file_data.startswith(b"FileNotFound"):
                    print("The file doesnot exist in Server")
                    SNW.send_packet_with_snw(cache_socket, "The file doesnot exist in Server".encode(), address) 
                else:   
                    # Save the file to cache
                    with open(filename, 'wb') as f:
                        f.write(file_data)
                
                    # Send origin info either from cache or server
                    SNW.send_packet_with_snw(cache_socket, "from origin".encode(), address)
                    
                    # Then send the file data to the client
                    SNW.send_packet_with_snw(cache_socket, file_data, address)

    elif command.startswith("put"):
        _, filename = command.split()
        
        # Receive the file data from the client and save it to the cache
        file_data, _ = SNW.receive_packet_with_snw(cache_socket)
        with open(filename, 'wb') as f:
            f.write(file_data)

        print(f"File {filename} received and saved to cache.")


def TCP_handle_client(client_socket):
    command = TCP.receive_data(client_socket).decode('utf-8')
    # Handling GET command
    if command.startswith("get "):
        filename = command.replace("get ", "")
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                file_data = f.read()
            TCP.send_data(client_socket, file_data + b"\nServer Response: File delivered from cache")
        else:
            server_socket = TCP.create_tcp_client_socket(SERVER_HOST, SERVER_PORT)
            TCP.send_data(server_socket, command.encode('utf-8'))
            file_data = TCP.receive_data(server_socket)
            if file_data.startswith(b"The file"):
                print("The file doesnot exist in Server")
                TCP.send_data(client_socket, file_data + b"\nFile Doesnot exist in Cache or Server")
            else:

                with open(filename, 'wb') as f:
                    f.write(file_data) # Save file data
                TCP.send_data(client_socket, file_data + b"\nServer Response: File delivered from origin")
                TCP.close_socket(server_socket)
    else:
        print("Cache does not handle PUT command directly.")

    TCP.close_socket(client_socket) # Close Socket


def main():
    

    if not os.path.exists(file_directory):
     os.makedirs(file_directory)
    
    os.chdir(file_directory) # Changes current saving directory of file to cache_files
    if len(sys.argv) != 5:
        print("Usage: python3 cache.py <cache_port> <server_host> <server_port> <Protocol>")
        sys.exit(1)
             
    if protocolType == 'tcp': # Handling for TCP section
        cache_socket = TCP.create_tcp_server_socket(CACHE_HOST, CACHE_PORT) # Creating Socket.Reference https://docs.python.org/3/howto/sockets.html, https://realpython.com/python-sockets/
        print(f"Cache started on {CACHE_HOST}:{CACHE_PORT}")
        while True:
            client_socket, _ = cache_socket.accept()
            client_handler = threading.Thread(target=TCP_handle_client, args=(client_socket,))
            client_handler.start() 
    elif protocolType == 'snw':   #  Making and using a socket object from the python's socket module, specifying the AF_INET address family for IPv4 config and the SOCK_DGRAM type for UDP communication.
        # References: https://docs.python.org/3/library/socket.html, https://realpython.com/python-sockets/
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as cache_socket: 
            cache_socket.bind((CACHE_HOST, CACHE_PORT)) # Binding the socket, i.e making sure that the system listens to the required application (cache) of ip addrss at right port
            cache_socket.settimeout(SNW.TIMEOUT)
            print(f"Cache listening on {CACHE_HOST}:{CACHE_PORT}") 

            while True:
                try:
                    data, address = SNW.receive_packet_with_snw(cache_socket)
                    SNW_handle_request(data, address, cache_socket)
                except socket.timeout:
                    continue

if __name__ == "__main__":
    main()