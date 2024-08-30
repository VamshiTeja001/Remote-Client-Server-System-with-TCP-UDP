# SERVER CODE #
# Name: Raghavendra Vamshi Teja Chathurajupalli
# Project 1

# Description: Code behaves as Server. It connects with cache for Get requests and Client for Put. The server responds to "get" request from Cache when cache doesn't have the file requested by client. It searches for the file from server_file directory and sends it to cache. Also the cache save the file sent from client into server_files directory.
# The server also prints messages whenever file is received or sent. 

# Execution Procedure: Open terminal/cmd, change to the directory in which server file is present, then run python3 server.py <server_host> <server_port> or python3 and then server.py <server_host> <server_port>

# Initializing necessary headers
import threading
import socket
import sys
import os
import snw_protocol as SNW   # Custom header for SNW protocol functions 
import tcp_transport as TCP  # Custom header for TCP protocol functions 


# Extracting socket details from command line
HOST = '' #sys.argv[1] # Alternativley repalce with localhost if necessary
PORT = int(sys.argv[1])
protocolType= sys.argv[2]
file_directory = "server_files"

# Definition to handle TCP tasks
 # References: https://docs.python.org/3/library/socket.html, https://realpython.com/python-sockets/
def handle_client(client_socket):
     try:
        data_received = TCP.receive_data(client_socket)
        
        if b"|" in data_received:  # To process put command
            filename, file_data = data_received.split(b"|", 1)
            filename = filename.decode('utf-8')
            with open(filename, 'wb') as f:
                f.write(file_data)
            TCP.send_data(client_socket, "File successfully uploaded".encode('utf-8'))
            print(f"File {filename} saved and acknowledgment sent.")
        else:  # To process get command
            filename = data_received.decode('utf-8').replace("get ", "")
            #filename = data_received.split(" ")[1]
            if os.path.exists(filename):  # check for file in directory
                with open(filename, 'rb') as f:
                    file_data_to_send = f.read()
                TCP.send_data(client_socket, file_data_to_send) # send file
                print(f"File {filename} sent to client.")
            else:
                TCP.send_data(client_socket, b"The file not found.") # Send acknolwdegement saying file not found
                print(f"The file {filename} not found.")
        TCP.close_socket(client_socket)
     except Exception as e:
        print(f"Error in handle_client: {e}")

#Definition to handle SNW
 # References: https://docs.python.org/3/library/socket.html, https://realpython.com/python-sockets/
def handle_request(data, address, server_socket):
    # If the received command starts with 'get'
    if data.startswith("get"):
        filename = data.split(" ")[1]
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                file_data = file.read()
            # Send file to cache
            SNW.send_packet_with_snw(server_socket, file_data, address)
            print(f"File {filename} sent to client.")
        else:
            print(f"File {filename} not found on server.")
            SNW.send_packet_with_snw(server_socket, "FileNotFound".encode(), address)
            #If the received command  is put
    elif data.startswith("put"):
        _, filename = data.split()
        
        # Receive the file data from the client and save it to the cache
        file_data, _ = SNW.receive_packet_with_snw(server_socket)
        SNW.send_packet_with_snw(server_socket, "File successfully uploaded".encode(), address)
        with open(filename, 'wb') as f:
            f.write(file_data)

        print(f"File {filename} received and saved to Server.")


def main():
    if not os.path.exists(file_directory):
        os.makedirs(file_directory)
    os.chdir(file_directory)  # Changes current saving directory of file to cache_files
     #If command line has tcp
    
    if len(sys.argv) != 3:
        print("Usage: python3 server.py <server_port> <Protocol>")
        sys.exit(1)

    if protocolType == 'tcp':
        
        server_socket = TCP.create_tcp_server_socket(HOST, PORT) 
        print(f"Server started on {HOST}:{PORT} using TCP Protocol")
        try:
            while True:
                client_socket, _ = server_socket.accept()
                client_handler = threading.Thread(target=handle_client, args=(client_socket,)) #Call TCP definition using thread to handle multiple request in relative to client and cache
                client_handler.start()
        except KeyboardInterrupt:
            print("\nServer shutting down.")
            sys.exit(0)
            TCP.close_socket(client_socket)
            
        finally:
            TCP.close_socket(client_socket)


        #If command line has tcp
    elif protocolType == 'snw':
        #server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #server_socket.bind((SERVER_HOST, SERVER_PORT))
        #print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Create server socket
        server_socket.bind((HOST, PORT))  #Bind socket
        print(f"Server started on {HOST}:{PORT} using SNW Protocol")

        try:
             while True:
                    data, address = SNW.receive_packet_with_snw(server_socket)
                    handle_request(data.decode(), address, server_socket)      #Call SNW definition
        except KeyboardInterrupt:
            print("\nServer shutting down.")
            #sys.exit(0)
            server_socket.close()
        finally:
            server_socket.close()

        
if __name__ == "__main__":
    main()
